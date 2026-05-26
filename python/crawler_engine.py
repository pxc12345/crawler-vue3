import json
import requests
from bs4 import BeautifulSoup
import threading
import time
import random
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse

# 可选：浏览器 TLS 指纹 / Cloudflare 绕过
try:
    from curl_cffi import requests as curl_cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    curl_cffi_requests = None
    HAS_CURL_CFFI = False

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    cloudscraper = None
    HAS_CLOUDSCRAPER = False

ENGINE_VERSION = "v3-curl-multi"


def get_engine_info():
    """供 health 接口与启动日志确认当前运行的是新版引擎"""
    return {
        "version": ENGINE_VERSION,
        "curl_cffi": HAS_CURL_CFFI,
        "cloudscraper": HAS_CLOUDSCRAPER,
    }


class CrawlerEngine:
    """
    通用爬虫引擎 - requests + BeautifulSoup4
    支持：多页同域发现、可配置重试/代理/请求头、增强图片与链接解析
    """

    CRAWL_MODE_LINK = "link"
    CRAWL_MODE_IMAGE = "image"
    CRAWL_MODE_MIXED = "mixed"

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    ]

    ACCEPT_LANGUAGES = [
        "zh-CN,zh;q=0.9,en;q=0.8",
        "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "en-US,en;q=0.9,zh-CN;q=0.8",
    ]

    ACCEPT_VALUES = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    ]

    BLOCKED_HTML_MARKERS = (
        "access denied", "403 forbidden", "cloudflare", "cf-browser-verification",
        "please enable javascript", "captcha", "verify you are human", "robot check",
        "security check", "attention required", "ddos-guard",
    )

    RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}

    CURL_IMPERSONATES = ("chrome131", "chrome124", "safari18_0", "edge131")

    PROTECTED_SITE_KEYWORDS = (
        "pixabay.com", "pexels.com", "unsplash.com", "shutterstock.com",
        "gettyimages", "istockphoto", "alamy.com", "freepik.com",
    )

    def __init__(self):
        self._stop_flag = threading.Event()
        self._task_id = None
        self._crawl_thread = None
        self._status = "idle"
        self._collected_count = 0
        self._current_page = 0
        self._total_pages = 0
        self._start_time = None
        self._elapsed_seconds = 0
        self._error_message = ""
        self._succeeded_pages = 0
        self._db_callback = None
        self._crawl_mode = self.CRAWL_MODE_LINK
        self._crawl_options = {}
        self._last_fetch_method = ""

    @property
    def status(self):
        return self._status

    @property
    def collected_count(self):
        return self._collected_count

    @property
    def current_page(self):
        return self._current_page

    @property
    def total_pages(self):
        return self._total_pages

    @property
    def elapsed_seconds(self):
        if self._start_time and self._status == "running":
            return int(time.time() - self._start_time)
        return self._elapsed_seconds

    @property
    def error_message(self):
        return self._error_message

    @staticmethod
    def normalize_url(url, base):
        """规范化 URL，支持协议相对路径 //cdn.example.com/img.jpg"""
        if not url:
            return None
        url = str(url).strip().strip("\"'")
        if not url or url.startswith("data:") or url.startswith("javascript:") or url.startswith("mailto:"):
            return None
        if url.startswith("#"):
            return None
        if url.startswith("//"):
            url = "https:" + url
        elif not url.startswith(("http://", "https://")):
            url = urljoin(base, url)
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                return None
            return urlunparse(parsed._replace(fragment=""))
        except Exception:
            return None

    @staticmethod
    def _same_registrable_domain(url_a, url_b):
        try:
            a = urlparse(url_a).netloc.lower().split(":")[0]
            b = urlparse(url_b).netloc.lower().split(":")[0]
            if a == b:
                return True
            return a.endswith("." + b) or b.endswith("." + a)
        except Exception:
            return False

    def _get_random_ua(self):
        return random.choice(self.USER_AGENTS)

    def _get_headers(self, url, referer=None):
        headers = {
            "User-Agent": self._get_random_ua(),
            "Accept": random.choice(self.ACCEPT_VALUES),
            "Accept-Language": random.choice(self.ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin" if referer else "none",
            "Sec-Fetch-User": "?1",
        }
        if referer:
            headers["Referer"] = referer
        custom = self._crawl_options.get("headers") or {}
        if isinstance(custom, dict):
            for k, v in custom.items():
                if k and v is not None:
                    headers[str(k)] = str(v)
        return headers

    def _pick_proxy(self):
        proxies_list = self._crawl_options.get("proxies") or []
        if not proxies_list:
            return None
        return random.choice(proxies_list)

    def _retry_wait(self, attempt, status_code=0, response=None):
        base = max(int(self._crawl_options.get("retry_interval") or 3), 1)
        if response is not None and status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after and str(retry_after).isdigit():
                return int(retry_after)
        if status_code == 403:
            return base + random.randint(4, 10)
        if status_code in (408, 429, 502, 503, 504):
            return base + random.randint(2, 6) + attempt
        return base + random.randint(1, 4) + attempt * 0.5

    def _url_candidates(self, url):
        """403 时尝试备用 URL（如去掉 /zh/ 语言路径）"""
        candidates = [url]
        seen = {url}
        for alt in (
            url.replace("/zh-cn/", "/").replace("/zh-CN/", "/"),
            url.replace("/zh/", "/"),
            re.sub(r"^(https?://[^/]+)/zh(?:-[a-z]{2})?/", r"\1/", url, flags=re.I),
        ):
            if alt and alt not in seen:
                seen.add(alt)
                candidates.append(alt)
        return candidates

    def _warmup_session(self, session, seed_url):
        try:
            parsed = urlparse(seed_url)
            origin = f"{parsed.scheme}://{parsed.netloc}/"
            session.get(
                origin,
                headers=self._get_headers(origin),
                timeout=12,
                allow_redirects=True,
                proxies=self._pick_proxy(),
            )
            time.sleep(random.uniform(0.4, 1.2))
        except Exception:
            pass

    def _response_to_html(self, response):
        encoding = self._detect_encoding(response)
        if hasattr(response, "encoding"):
            response.encoding = encoding
        if hasattr(response, "text"):
            return response.text
        return response.content.decode(encoding, errors="replace")

    def _fetch_via_requests(self, session, url, referer=None):
        max_retries = max(int(self._crawl_options.get("max_retries") or 5), 1)
        timeout = max(int(self._crawl_options.get("timeout") or 22), 5)
        last_error = None

        for attempt in range(max_retries):
            proxies = self._pick_proxy()
            try:
                response = session.get(
                    url,
                    headers=self._get_headers(url, referer=referer or url),
                    timeout=timeout,
                    allow_redirects=True,
                    proxies=proxies,
                )
                status = response.status_code

                if status == 403 and attempt < max_retries - 1:
                    time.sleep(self._retry_wait(attempt, 403))
                    continue

                if status in self.RETRYABLE_STATUS and attempt < max_retries - 1:
                    time.sleep(self._retry_wait(attempt, status, response))
                    continue

                if status >= 400:
                    raise Exception(f"HTTP {status}")

                html = self._response_to_html(response)
                if self._is_blocked_html(html):
                    raise Exception("页面内容为反爬/验证页")
                return html

            except Exception as e:
                last_error = e
                if attempt >= max_retries - 1:
                    break
                time.sleep(self._retry_wait(attempt))

        raise last_error or Exception("requests 请求失败")

    def _fetch_via_curl_cffi(self, url, referer=None):
        if not HAS_CURL_CFFI:
            raise Exception("curl_cffi 未安装")
        timeout = max(int(self._crawl_options.get("timeout") or 22), 5)
        proxy = self._pick_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        headers = self._get_headers(url, referer=referer or url)
        last_error = None

        for imp in self.CURL_IMPERSONATES:
            try:
                response = curl_cffi_requests.get(
                    url,
                    impersonate=imp,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True,
                    proxies=proxies,
                )
                status = getattr(response, "status_code", 0)
                if status >= 400:
                    raise Exception(f"HTTP {status}")
                html = self._response_to_html(response)
                if self._is_blocked_html(html):
                    raise Exception("页面内容为反爬/验证页")
                return html
            except Exception as e:
                last_error = e
                continue

        raise last_error or Exception("curl_cffi 请求失败")

    def _fetch_via_cloudscraper(self, url, referer=None):
        if not HAS_CLOUDSCRAPER:
            raise Exception("cloudscraper 未安装")
        timeout = max(int(self._crawl_options.get("timeout") or 22), 5)
        proxy = self._pick_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        response = scraper.get(
            url,
            headers=self._get_headers(url, referer=referer or url),
            timeout=timeout,
            allow_redirects=True,
            proxies=proxies,
        )
        if response.status_code >= 400:
            raise Exception(f"HTTP {response.status_code}")
        html = self._response_to_html(response)
        if self._is_blocked_html(html):
            raise Exception("页面内容为反爬/验证页")
        return html

    def _is_protected_site(self, url):
        host = urlparse(url).netloc.lower()
        return any(k in host for k in self.PROTECTED_SITE_KEYWORDS)

    def _build_fetch_strategies(self, session, url):
        strategies = []
        protected = self._is_protected_site(url)

        if HAS_CURL_CFFI and self._crawl_options.get("use_curl_cffi", True):
            strategies.append(("浏览器指纹", lambda u, r: self._fetch_via_curl_cffi(u, r)))
        if HAS_CLOUDSCRAPER and self._crawl_options.get("use_cloudscraper", True):
            strategies.append(("Cloudflare绕过", lambda u, r: self._fetch_via_cloudscraper(u, r)))

        # 图库/强反爬站禁止使用普通 requests（易 403 且不会自动切换）
        if not protected and self._crawl_options.get("use_requests", True):
            strategies.append(("标准请求", lambda u, r: self._fetch_via_requests(session, u, r)))

        if not strategies:
            if HAS_CURL_CFFI:
                strategies.append(("浏览器指纹", lambda u, r: self._fetch_via_curl_cffi(u, r)))
            else:
                strategies.append(("标准请求", lambda u, r: self._fetch_via_requests(session, u, r)))

        if not protected:
            strategies = list(reversed(strategies))
        return strategies

    def _fetch_page(self, session, url, referer=None):
        """多策略抓取；返回 (html, 策略名称)"""
        errors = []
        strategies = self._build_fetch_strategies(session, url)
        if self._is_protected_site(url) and not HAS_CURL_CFFI:
            raise Exception(
                "当前 Python 环境未安装 curl_cffi，无法抓取 Pixabay 等强反爬站点。"
                "请在运行 app.py 的同一环境中执行: pip install curl_cffi cloudscraper，然后重启后端。"
            )

        for candidate_url in self._url_candidates(url):
            ref = referer or candidate_url
            for name, fetcher in strategies:
                try:
                    html = fetcher(candidate_url, ref)
                    if html and len(html.strip()) > 100:
                        self._last_fetch_method = name
                        return html, name
                    errors.append(f"{name}@{candidate_url}: 内容过短")
                except Exception as e:
                    err_text = str(e).strip() or name
                    errors.append(f"{name}: {err_text}")

        hint = "请确认已重启后端(health 中 crawler.version 应为 v3-curl-multi)；强反爬站请配置代理组 proxy_group"
        detail = "; ".join(errors[-5:]) if errors else "未知错误"
        if "403" in detail:
            raise Exception(
                f"HTTP错误 [403]: {url} — 已用 {', '.join(n for n, _ in strategies)} 等方式尝试仍失败。"
                f"{hint}。详情: {detail[:200]}"
            )
        raise Exception(f"无法获取页面: {url} — {detail[:280]}。{hint}")

    def _detect_encoding(self, response):
        try:
            content_type = response.headers.get("Content-Type", "")
            m = re.search(r"charset=([\w-]+)", content_type, re.I)
            if m:
                return m.group(1)
        except Exception:
            pass
        enc = getattr(response, "apparent_encoding", None) or "utf-8"
        if enc and enc.lower() in ("ascii", "none"):
            return "utf-8"
        return enc or "utf-8"

    def _is_blocked_html(self, html):
        if not html:
            return True
        sample = html[:8000].lower()
        if len(sample.strip()) < 80:
            return True
        hits = sum(1 for m in self.BLOCKED_HTML_MARKERS if m in sample)
        return hits >= 2

    def _extract_images_from_scripts(self, soup, source_url, add_result, is_duplicate):
        """从 script / JSON-LD 中提取图片 URL（适配 Pixabay 等 SPA 站点）"""
        img_url_pattern = re.compile(
            r"https?://[^\s\"'<>\\]+\.(?:jpg|jpeg|png|webp|gif|avif)(?:\?[^\s\"'<>\\]*)?",
            re.I,
        )

        def try_add(raw_url, title="脚本图片"):
            full_url = self.normalize_url(raw_url, source_url)
            if not full_url:
                return
            item = {
                "title": title[:200],
                "link": full_url[:500],
                "image_url": full_url[:500],
                "content": "",
                "source_url": source_url[:500],
                "type": "image",
            }
            if not is_duplicate(item):
                add_result(item)

        for script in soup.find_all("script", type="application/ld+json"):
            raw = script.string or script.get_text()
            if not raw:
                continue
            try:
                data = json.loads(raw)
                stack = [data]
                while stack:
                    node = stack.pop()
                    if isinstance(node, dict):
                        img = node.get("image") or node.get("thumbnailUrl") or node.get("contentUrl")
                        if isinstance(img, str):
                            try_add(img, "JSON-LD图片")
                        elif isinstance(img, list):
                            for u in img:
                                if isinstance(u, str):
                                    try_add(u, "JSON-LD图片")
                                elif isinstance(u, dict) and u.get("url"):
                                    try_add(u["url"], "JSON-LD图片")
                        for v in node.values():
                            if isinstance(v, (dict, list)):
                                stack.append(v)
                    elif isinstance(node, list):
                        stack.extend(node)
            except (json.JSONDecodeError, TypeError):
                continue

        for script in soup.find_all("script"):
            text = script.string or script.get_text() or ""
            if len(text) < 20:
                continue
            for match in img_url_pattern.findall(text):
                try_add(match, "页面脚本图片")

    def _probe_image_url(self, session, image_url, referer):
        if not self._crawl_options.get("validate_images"):
            return True
        try:
            resp = session.head(
                image_url,
                headers=self._get_headers(image_url, referer=referer),
                timeout=min(int(self._crawl_options.get("timeout") or 15), 12),
                allow_redirects=True,
                proxies=self._pick_proxy(),
            )
            if resp.status_code >= 400:
                return False
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if ctype and "image" not in ctype and "octet-stream" not in ctype:
                return False
            return True
        except Exception:
            try:
                resp = session.get(
                    image_url,
                    headers={**self._get_headers(image_url, referer=referer), "Range": "bytes=0-512"},
                    timeout=10,
                    stream=True,
                    proxies=self._pick_proxy(),
                )
                return resp.status_code < 400
            except Exception:
                return False

    def _extract_img_url(self, img_tag, base_url):
        lazy_attrs = [
            "data-src", "data-original", "data-lazy-src", "data-lazy", "data-url",
            "data-srcset", "data-image", "data-ks-image", "data-bg-src", "data-bg",
            "data-echo", "data-lazyload", "data-original-src", "data-thumb", "data-poster",
        ]
        for attr in lazy_attrs:
            src = (img_tag.get(attr) or "").strip()
            if src:
                first = src.split(",")[0].strip().split()[0] if "," in src else src
                normalized = self.normalize_url(first, base_url)
                if normalized:
                    return normalized

        srcset = img_tag.get("srcset") or img_tag.get("data-srcset") or ""
        if srcset:
            for part in srcset.split(","):
                url = part.strip().split()[0] if part.strip() else ""
                normalized = self.normalize_url(url, base_url)
                if normalized:
                    return normalized

        return self.normalize_url((img_tag.get("src") or "").strip(), base_url)

    def _parse_page(self, html, source_url, session=None):
        soup = BeautifulSoup(html, "lxml")
        results = []
        seen_urls = set()

        main_content = soup.find("body") or soup
        parsed_source = urlparse(source_url)
        base_url = f"{parsed_source.scheme}://{parsed_source.netloc}"

        def is_duplicate(item):
            link = item.get("link", "")
            img = item.get("image_url", "")
            return link in seen_urls or (img and img in seen_urls)

        def add_result(item):
            link = item.get("link", "")
            img = item.get("image_url", "")
            if link:
                seen_urls.add(link)
            if img:
                seen_urls.add(img)
            results.append(item)

        def link_title(link, full_url):
            title = (link.get_text(strip=True) or "").strip()
            if not title:
                title = (link.get("title") or link.get("aria-label") or "").strip()
            if not title:
                path = urlparse(full_url).path.rstrip("/")
                title = path.split("/")[-1] if path else full_url
            return (title or "链接")[:200]

        if self._crawl_mode in (self.CRAWL_MODE_LINK, self.CRAWL_MODE_MIXED):
            for link in main_content.find_all("a", href=True):
                href = (link.get("href") or "").strip()
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue
                full_url = self.normalize_url(href, source_url)
                if not full_url:
                    continue

                parent_text = ""
                parent = link.find_parent(["p", "div", "section", "article", "li", "td", "h1", "h2", "h3"])
                if parent:
                    parent_text = parent.get_text(separator=" ", strip=True)[:500]

                item = {
                    "title": link_title(link, full_url),
                    "link": full_url[:500],
                    "content": parent_text[:1000],
                    "source_url": source_url[:500],
                    "type": "link",
                }
                if not is_duplicate(item):
                    add_result(item)

        if self._crawl_mode in (self.CRAWL_MODE_IMAGE, self.CRAWL_MODE_MIXED):
            image_candidates = []

            for img in main_content.find_all("img"):
                full_url = self._extract_img_url(img, source_url)
                if full_url:
                    image_candidates.append((full_url, img))

            for meta in main_content.find_all("meta"):
                prop = (meta.get("property") or meta.get("name") or "").lower()
                if prop in ("og:image", "og:image:url", "twitter:image", "twitter:image:src"):
                    content = meta.get("content", "")
                    full_url = self.normalize_url(content, source_url)
                    if full_url:
                        image_candidates.append((full_url, None))

            for video in main_content.find_all("video"):
                poster = video.get("poster") or ""
                full_url = self.normalize_url(poster, source_url)
                if full_url:
                    image_candidates.append((full_url, None))
                src = video.get("src") or ""
                full_url = self.normalize_url(src, source_url)
                if full_url:
                    image_candidates.append((full_url, None))

            for picture in main_content.find_all("picture"):
                for source in picture.find_all("source"):
                    srcset = source.get("srcset", "")
                    if srcset:
                        first_url = srcset.split(",")[0].strip().split()[0]
                        full_url = self.normalize_url(first_url, source_url)
                        if full_url:
                            image_candidates.append((full_url, None))

            for elem in main_content.find_all(style=True):
                style = elem.get("style", "")
                for bg_url in re.findall(
                    r'background(?:-image)?\s*:\s*url\s*\([\'"]?([^\'")]+)[\'"]?\)', style, re.I
                ):
                    full_url = self.normalize_url(bg_url.strip(), source_url)
                    if full_url:
                        image_candidates.append((full_url, None))

            for elem in main_content.find_all(attrs={"data-bg": True}):
                full_url = self.normalize_url(elem.get("data-bg", ""), source_url)
                if full_url:
                    image_candidates.append((full_url, None))

            probe_budget = int(self._crawl_options.get("image_probe_limit") or 40)
            probed = 0

            for full_url, img in image_candidates:
                if probed >= probe_budget and session and self._crawl_options.get("validate_images"):
                    break
                if session and self._crawl_options.get("validate_images"):
                    if not self._probe_image_url(session, full_url, source_url):
                        continue
                    probed += 1

                alt_text = ""
                title_text = ""
                if img is not None:
                    alt_text = (img.get("alt") or "").strip()[:200]
                    title_text = (img.get("title") or "").strip()[:200]
                img_title = alt_text or title_text or "图片"

                parent_text = ""
                if img is not None:
                    parent = img.find_parent(["p", "div", "section", "article", "figure"])
                    if parent:
                        parent_text = parent.get_text(separator=" ", strip=True)[:500]

                item = {
                    "title": img_title[:200],
                    "link": full_url[:500],
                    "image_url": full_url[:500],
                    "content": parent_text[:1000],
                    "source_url": source_url[:500],
                    "type": "image",
                }
                if not is_duplicate(item):
                    add_result(item)

            self._extract_images_from_scripts(main_content, source_url, add_result, is_duplicate)

        if not results:
            text_content = main_content.get_text(separator=" ", strip=True)[:500]
            page_title = ""
            if soup.title and soup.title.string:
                page_title = soup.title.string.strip()[:200]
            results.append({
                "title": page_title or "页面内容",
                "link": source_url[:500],
                "content": text_content[:1000],
                "source_url": source_url[:500],
                "type": "page",
            })

        return results

    def _discover_page_urls(self, html, seed_url, max_count):
        """从页面发现同域可继续爬取的 URL（分页、导航链接）"""
        if max_count <= 1:
            return []

        soup = BeautifulSoup(html, "lxml")
        found = []
        seen = {seed_url}

        def add_candidate(raw):
            full = self.normalize_url(raw, seed_url)
            if not full or full in seen:
                return
            if not self._same_registrable_domain(full, seed_url):
                return
            seen.add(full)
            found.append(full)

        for link in soup.find_all("a", href=True):
            rel = " ".join(link.get("rel") or []).lower()
            href = link.get("href", "")
            cls = " ".join(link.get("class") or []).lower()
            text = link.get_text(strip=True).lower()
            if "next" in rel or "下一页" in text or "next" in cls or "pagination" in cls:
                add_candidate(href)
            if re.search(r"[?&]page=\d+", href) or re.search(r"/page/\d+", href, re.I):
                add_candidate(href)

        for link in soup.find_all("a", href=True):
            if len(found) >= max_count - 1:
                break
            add_candidate(link.get("href"))

        return found[: max_count - 1]

    def _crawl_task(self, target_url, total_pages, interval_seconds, db_callback):
        self._stop_flag.clear()
        self._status = "running"
        self._collected_count = 0
        self._current_page = 0
        self._total_pages = total_pages
        self._start_time = time.time()
        self._elapsed_seconds = 0
        self._error_message = ""
        self._succeeded_pages = 0
        self._db_callback = db_callback
        continue_on_error = self._crawl_options.get("continue_on_error", True)

        validate_images = self._crawl_mode in (
            self.CRAWL_MODE_IMAGE, self.CRAWL_MODE_MIXED
        )
        self._crawl_options["validate_images"] = self._crawl_options.get(
            "validate_images", validate_images
        )

        def _emit_log(level, message):
            if db_callback and self._task_id:
                try:
                    db_callback({
                        "type": "log",
                        "task_id": self._task_id,
                        "level": level,
                        "message": message,
                    })
                except Exception:
                    pass

        session = requests.Session()
        self._warmup_session(session, target_url)
        page_urls = [target_url]
        last_html = None
        referer = None

        _emit_log(
            "INFO",
            f"任务[{self._task_id}] 引擎{ENGINE_VERSION} 开始爬取: {target_url[:120]}, "
            f"curl_cffi={HAS_CURL_CFFI}, cloudscraper={HAS_CLOUDSCRAPER}, "
            f"强反爬={'是' if self._is_protected_site(target_url) else '否'}, "
            f"共{total_pages}页, 模式={self._crawl_mode}",
        )

        try:
            for page in range(1, total_pages + 1):
                if self._stop_flag.is_set():
                    self._status = "stopped"
                    self._elapsed_seconds = int(time.time() - self._start_time)
                    return

                self._current_page = page
                if page <= len(page_urls):
                    current_url = page_urls[page - 1]
                elif page_urls:
                    current_url = page_urls[-1]
                else:
                    current_url = target_url

                try:
                    html, fetch_via = self._fetch_page(
                        session, current_url, referer=referer or target_url
                    )
                    last_html = html
                    referer = current_url
                    _emit_log("INFO", f"第{page}页抓取成功，方式: {fetch_via}, 大小: {len(html)} 字符")
                except Exception as e:
                    self._error_message = f"第{page}页请求失败: {str(e)}"
                    _emit_log("ERROR", self._error_message)
                    if continue_on_error and page < total_pages:
                        continue
                    self._status = "error"
                    self._elapsed_seconds = int(time.time() - self._start_time)
                    return

                if page == 1 and total_pages > 1 and len(page_urls) < total_pages:
                    extra = self._discover_page_urls(html, target_url, total_pages)
                    for u in extra:
                        if u not in page_urls:
                            page_urls.append(u)
                        if len(page_urls) >= total_pages:
                            break

                try:
                    items = self._parse_page(html, current_url, session=session)
                except Exception as e:
                    self._error_message = f"第{page}页解析失败: {str(e)}"
                    _emit_log("ERROR", self._error_message)
                    if continue_on_error and page < total_pages:
                        continue
                    self._status = "error"
                    self._elapsed_seconds = int(time.time() - self._start_time)
                    return

                if items and db_callback:
                    for item in items:
                        item["page_number"] = page
                    try:
                        saved_count = db_callback(items)
                        self._collected_count += saved_count
                        self._succeeded_pages += 1
                        _emit_log("INFO", f"第{page}页入库 {saved_count} 条 (来源: {current_url[:80]})")
                    except Exception as e:
                        self._error_message = f"第{page}页数据保存失败: {str(e)}"
                        _emit_log("ERROR", self._error_message)
                        if continue_on_error and page < total_pages:
                            continue
                        self._status = "error"
                        self._elapsed_seconds = int(time.time() - self._start_time)
                        return
                elif not items:
                    _emit_log("WARNING", f"任务[{self._task_id}] 第{page}页未解析到数据")

                if page < total_pages and not self._stop_flag.is_set():
                    time.sleep(max(interval_seconds, 1))

        except Exception as e:
            self._error_message = f"爬取过程异常: {str(e)}"
            self._status = "error"
            _emit_log("ERROR", self._error_message)
        finally:
            session.close()
            if self._status == "running":
                if self._succeeded_pages > 0:
                    self._status = "completed"
                elif last_html:
                    self._status = "completed"
                    _emit_log("WARNING", "任务完成但未成功入库任何页面数据")
                else:
                    self._status = "error"
                    if not self._error_message:
                        self._error_message = "未能成功抓取任何页面"
            self._elapsed_seconds = int(time.time() - self._start_time)
            if self._task_id and db_callback:
                try:
                    total_pages = max(1, self._total_pages or 1)
                    succeeded = self._succeeded_pages or 0
                    success_rate = min(
                        100.0, round((succeeded / total_pages) * 100, 2)
                    )
                    db_callback({
                        "type": "complete",
                        "task_id": self._task_id,
                        "status": self._status,
                        "execution_time": self._elapsed_seconds,
                        "collected_count": self._collected_count,
                        "succeeded_pages": succeeded,
                        "total_pages": total_pages,
                        "success_rate": success_rate,
                        "error_message": self._error_message or "",
                    })
                except Exception as e:
                    print(f"[Crawler] Update task status error: {e}")

    @staticmethod
    def _resolve_crawl_options(crawl_options=None):
        opts = dict(crawl_options or {})
        opts.setdefault("max_retries", 6)
        opts.setdefault("retry_interval", 3)
        opts.setdefault("timeout", 22)
        opts.setdefault("continue_on_error", True)
        opts.setdefault("validate_images", False)
        opts.setdefault("image_probe_limit", 30)
        opts.setdefault("use_curl_cffi", True)
        opts.setdefault("use_cloudscraper", True)
        opts.setdefault("use_requests", True)
        headers = opts.get("headers")
        if isinstance(headers, str):
            try:
                import json
                headers = json.loads(headers)
            except Exception:
                headers = {}
        if not isinstance(headers, dict):
            headers = {}
        opts["headers"] = headers
        return opts

    @staticmethod
    def _load_proxies_for_group(proxy_group):
        if not proxy_group:
            return []
        try:
            from proxy_db import proxy_db
            rows = proxy_db.get_proxies_by_group_name(proxy_group)
        except Exception:
            return []
        result = []
        for row in rows:
            ip = row.get("ip")
            port = row.get("port")
            protocol = (row.get("protocol") or "http").lower()
            if not ip or not port:
                continue
            result.append(f"{protocol}://{ip}:{port}")
        return result

    def start(
        self,
        target_url,
        total_pages,
        interval_seconds,
        db_callback,
        crawl_mode="link",
        task_id=None,
        crawl_options=None,
    ):
        if self._status == "running":
            return False, "爬虫已在运行中，请先停止当前任务"

        if not target_url or not target_url.startswith(("http://", "https://")):
            return False, "请输入有效的网址（以 http:// 或 https:// 开头）"

        if total_pages < 1 or total_pages > 100:
            return False, "爬取页数需在 1-100 之间"

        if interval_seconds < 1 or interval_seconds > 60:
            return False, "请求间隔需在 1-60 秒之间"

        if crawl_mode in (self.CRAWL_MODE_LINK, self.CRAWL_MODE_IMAGE, self.CRAWL_MODE_MIXED):
            self._crawl_mode = crawl_mode
        else:
            self._crawl_mode = self.CRAWL_MODE_LINK

        self._crawl_options = self._resolve_crawl_options(crawl_options)
        proxy_group = self._crawl_options.get("proxy_group") or ""
        if proxy_group:
            self._crawl_options["proxies"] = self._load_proxies_for_group(proxy_group)

        self._task_id = task_id
        self._crawl_thread = threading.Thread(
            target=self._crawl_task,
            args=(target_url, total_pages, interval_seconds, db_callback),
            daemon=True,
        )
        self._crawl_thread.start()
        return True, "爬虫任务已启动"

    def stop(self):
        if self._status != "running":
            return False, "当前没有正在运行的爬虫任务"

        self._stop_flag.set()
        self._status = "stopping"
        return True, "停止信号已发送，等待当前页面完成后停止"

    def get_status(self):
        return {
            "status": self._status,
            "collected_count": self._collected_count,
            "current_page": self._current_page,
            "total_pages": self._total_pages,
            "elapsed_seconds": self.elapsed_seconds,
            "error_message": self._error_message,
            "task_id": self._task_id,
            "succeeded_pages": self._succeeded_pages,
        }

    def reset(self):
        if self._status == "running":
            return False, "爬虫正在运行，请先停止"
        self._status = "idle"
        self._collected_count = 0
        self._current_page = 0
        self._total_pages = 0
        self._start_time = None
        self._elapsed_seconds = 0
        self._error_message = ""
        self._succeeded_pages = 0
        self._crawl_options = {}
        return True, "爬虫状态已重置"


crawler_engine = CrawlerEngine()

if __name__ != "__main__":
    _info = get_engine_info()
    print(
        "[CrawlerEngine] version={version}, curl_cffi={curl_cffi}, cloudscraper={cloudscraper}".format(
            **_info
        )
    )
