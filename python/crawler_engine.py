import requests
from bs4 import BeautifulSoup
import threading
import time
import random
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse


class CrawlerEngine:
    """
    通用爬虫引擎 - 基于 requests + BeautifulSoup4 实现
    功能：
    1. 多线程爬取，支持启停控制
    2. UA 请求头伪装，随机切换，降低封禁风险
    3. 请求延时，模拟人工浏览间隔
    4. 通用页面解析：提取标题、链接、正文内容、图片地址
    5. 支持爬取模式切换：链接模式、图片模式、混合模式
    """

    CRAWL_MODE_LINK = "link"      # 只爬取链接
    CRAWL_MODE_IMAGE = "image"    # 只爬取图片
    CRAWL_MODE_MIXED = "mixed"    # 同时爬取链接和图片

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]

    # Accept-Language 列表
    ACCEPT_LANGUAGES = [
        "zh-CN,zh;q=0.9,en;q=0.8",
        "zh-CN,zh;q=0.9",
        "en-US,en;q=0.9,zh-CN;q=0.8",
        "zh-TW,zh;q=0.9,en;q=0.8",
    ]

    # 随机生成 Accept 值
    ACCEPT_VALUES = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "text/html,application/xml;q=0.9,image/webp,*/*;q=0.8",
    ]

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
        self._crawl_mode = self.CRAWL_MODE_LINK  # 默认只爬取链接

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

    def _get_random_ua(self):
        """随机获取一个 User-Agent，用于伪装请求头"""
        return random.choice(self.USER_AGENTS)

    def _get_headers(self):
        """构建请求头，模拟真实浏览器，增强反爬能力"""
        return {
            "User-Agent": self._get_random_ua(),
            "Accept": random.choice(self.ACCEPT_VALUES),
            "Accept-Language": random.choice(self.ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def _fetch_page(self, session, url, timeout=15):
        """使用 session 获取页面 HTML 内容，带重试机制和反爬策略"""
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                response = session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=timeout,
                    allow_redirects=True
                )
                
                # 处理 403 Forbidden - 增加特殊处理
                if response.status_code == 403:
                    if attempt < max_retries - 1:
                        # 403时等待更长时间并更换请求头
                        wait_time = 5 + random.randint(3, 8)
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"HTTP错误 [403]: {url} - 网站可能已封禁您的IP或需要特殊访问权限")
                
                response.raise_for_status()
                response.encoding = response.apparent_encoding or "utf-8"
                return response.text
                
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    raise Exception(f"请求超时，已重试{max_retries}次: {url}")
                # 超时后等待随机时间
                wait_time = 3 + random.randint(2, 5)
                time.sleep(wait_time)
                
            except requests.exceptions.ConnectionError:
                if attempt == max_retries - 1:
                    raise Exception(f"无法连接到目标网址，请检查网址是否正确: {url}")
                time.sleep(3)
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else 0
                
                # 5xx 服务器错误可重试
                if 500 <= status_code < 600 and attempt < max_retries - 1:
                    wait_time = 4 + random.randint(2, 6)
                    time.sleep(wait_time)
                    continue
                    
                raise Exception(f"HTTP错误 [{status_code}]: {url}")
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"请求失败: {str(e)}")
                wait_time = 2 + random.randint(1, 4)
                time.sleep(wait_time)

        raise Exception(f"请求失败: {url}")

    def _parse_page(self, html, source_url):
        """通用页面解析：根据爬取模式提取链接或图片"""
        soup = BeautifulSoup(html, "lxml")
        results = []
        seen_urls = set()  # 用于去重，同时记录 link 和 image_url

        main_content = soup.find("body")
        if not main_content:
            return results

        base_url = "{0}://{1}".format(urlparse(source_url).scheme, urlparse(source_url).netloc)

        def is_duplicate(item):
            link = item.get("link", "")
            img = item.get("image_url", "")
            if link in seen_urls or img in seen_urls:
                return True
            return False

        def add_result(item):
            link = item.get("link", "")
            img = item.get("image_url", "")
            seen_urls.add(link)
            if img:
                seen_urls.add(img)
            results.append(item)

        def extract_img_url(img_tag, base_url):
            """从 img 标签提取图片 URL，支持多种懒加载方式"""
            # 懒加载属性优先级
            lazy_attrs = [
                "data-src", "data-original", "data-lazy-src", "data-lazy",
                "data-srcset", "data-image", "data-ks-image", "data-bg-src",
                "data-bg", "data-toggle", "data-url"
            ]
            
            for attr in lazy_attrs:
                src = img_tag.get(attr, "").strip()
                if src:
                    return src
            
            # 处理 srcset
            srcset = img_tag.get("srcset", "")
            if srcset:
                parts = srcset.split(",")
                for part in parts:
                    url = part.strip().split()[0]
                    if url and not url.startswith("data:"):
                        return url
            
            # 最后使用 src
            return img_tag.get("src", "").strip()

        def normalize_url(url, base):
            """规范化 URL"""
            if not url or url.startswith("data:") or url.startswith("//"):
                return None
            if url.startswith("//"):
                url = "https:" + url
            return urljoin(base, url)

        # 提取链接
        if self._crawl_mode in (self.CRAWL_MODE_LINK, self.CRAWL_MODE_MIXED):
            for link in main_content.find_all("a", href=True):
                href = link.get("href", "").strip()
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue

                full_url = urljoin(base_url, href)
                title = link.get_text(strip=True)
                if not title or len(title) < 2:
                    continue

                parent_text = ""
                parent = link.find_parent(["p", "div", "section", "article", "li", "td", "h1", "h2", "h3", "h4", "h5", "h6"])
                if parent:
                    parent_text = parent.get_text(separator=" ", strip=True)[:500]

                item = {
                    "title": title[:200],
                    "link": full_url[:500],
                    "content": parent_text[:1000],
                    "source_url": source_url[:500],
                    "type": "link",
                }
                if is_duplicate(item):
                    continue
                add_result(item)

        # 提取图片
        if self._crawl_mode in (self.CRAWL_MODE_IMAGE, self.CRAWL_MODE_MIXED):
            # 1. 提取 img 标签
            for img in main_content.find_all("img"):
                raw_url = extract_img_url(img, base_url)
                if not raw_url:
                    continue
                    
                full_url = normalize_url(raw_url, base_url)
                if not full_url:
                    continue

                alt_text = img.get("alt", "").strip()[:200]
                title_text = img.get("title", "").strip()[:200]
                img_title = alt_text if alt_text else (title_text if title_text else "图片")

                parent_text = ""
                parent = img.find_parent(["p", "div", "section", "article", "li", "td", "figure"])
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
                if is_duplicate(item):
                    continue
                add_result(item)
            
            # 2. 提取 picture 标签中的 source
            for picture in main_content.find_all("picture"):
                for source in picture.find_all("source"):
                    srcset = source.get("srcset", "")
                    if srcset:
                        first_url = srcset.split(",")[0].strip().split()[0]
                        full_url = normalize_url(first_url, base_url)
                        if full_url:
                            item = {
                                "title": "picture标签图片",
                                "link": full_url[:500],
                                "image_url": full_url[:500],
                                "content": "",
                                "source_url": source_url[:500],
                                "type": "image",
                            }
                            if not is_duplicate(item):
                                add_result(item)

            # 3. 提取 CSS 背景图 (style="background-image: url(...)")
            for elem in main_content.find_all(style=True):
                style = elem.get("style", "")
                bg_urls = re.findall(r'background-image\s*:\s*url\s*\([\'"]?([^\'")]+)[\'"]?\)', style)
                for bg_url in bg_urls:
                    full_url = normalize_url(bg_url.strip(), base_url)
                    if full_url:
                        item = {
                            "title": "背景图片",
                            "link": full_url[:500],
                            "image_url": full_url[:500],
                            "content": "",
                            "source_url": source_url[:500],
                            "type": "image",
                        }
                        if not is_duplicate(item):
                            add_result(item)

            # 4. 提取 data-bg 属性的图片（某些懒加载框架使用）
            for elem in main_content.find_all(attrs={"data-bg": True}):
                bg_url = elem.get("data-bg", "")
                full_url = normalize_url(bg_url, base_url)
                if full_url:
                    item = {
                        "title": "data-bg图片",
                        "link": full_url[:500],
                        "image_url": full_url[:500],
                        "content": "",
                        "source_url": source_url[:500],
                        "type": "image",
                    }
                    if not is_duplicate(item):
                        add_result(item)

            # 5. 提取 srcset 属性中的图片
            for img in main_content.find_all(srcset=True):
                srcset = img.get("srcset", "")
                parts = srcset.split(",")
                for part in parts:
                    url = part.strip().split()[0]
                    if url and not url.startswith("data:") and not url.startswith("//"):
                        full_url = urljoin(base_url, url)
                        item = {
                            "title": img.get("alt", "srcset图片")[:200] or "srcset图片",
                            "link": full_url[:500],
                            "image_url": full_url[:500],
                            "content": "",
                            "source_url": source_url[:500],
                            "type": "image",
                        }
                        if not is_duplicate(item):
                            add_result(item)

            # 6. 提取 figure 标签中的图片（常用于画廊）
            for figure in main_content.find_all("figure"):
                img = figure.find("img")
                if img:
                    raw_url = extract_img_url(img, base_url)
                    if raw_url:
                        full_url = normalize_url(raw_url, base_url)
                        if full_url:
                            figcaption = figure.find("figcaption")
                            title = figcaption.get_text(strip=True)[:200] if figcaption else "figure图片"
                            
                            item = {
                                "title": title,
                                "link": full_url[:500],
                                "image_url": full_url[:500],
                                "content": "",
                                "source_url": source_url[:500],
                                "type": "image",
                            }
                            if not is_duplicate(item):
                                add_result(item)

        # 如果没有提取到任何内容，返回页面基本信息
        if not results:
            text_content = main_content.get_text(separator=" ", strip=True)[:500]
            results.append({
                "title": soup.title.string[:200] if soup.title else "无标题",
                "link": source_url[:500],
                "content": text_content[:1000],
                "source_url": source_url[:500],
                "type": "page",
            })

        return results

    def _crawl_task(self, target_url, total_pages, interval_seconds, db_callback):
        """爬取任务主逻辑，在独立线程中运行"""
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

        def _emit_log(level, message):
            if db_callback and self._task_id:
                try:
                    db_callback({
                        'type': 'log',
                        'task_id': self._task_id,
                        'level': level,
                        'message': message,
                    })
                except Exception:
                    pass

        session = requests.Session()
        _emit_log('INFO', f'任务[{self._task_id}] 开始爬取: {target_url[:120]}, 共{total_pages}页, 间隔{interval_seconds}s')

        try:
            for page in range(1, total_pages + 1):
                if self._stop_flag.is_set():
                    self._status = "stopped"
                    self._elapsed_seconds = int(time.time() - self._start_time)
                    return

                self._current_page = page

                try:
                    html = self._fetch_page(session, target_url)
                except Exception as e:
                    self._error_message = f"第{page}页请求失败: {str(e)}"
                    self._status = "error"
                    self._elapsed_seconds = int(time.time() - self._start_time)
                    _emit_log('ERROR', self._error_message)
                    return

                try:
                    items = self._parse_page(html, target_url)
                except Exception as e:
                    self._error_message = f"第{page}页解析失败: {str(e)}"
                    self._status = "error"
                    self._elapsed_seconds = int(time.time() - self._start_time)
                    _emit_log('ERROR', self._error_message)
                    return

                if items and db_callback:
                    for item in items:
                        item["page_number"] = page
                    try:
                        saved_count = db_callback(items)
                        self._collected_count += saved_count
                        self._succeeded_pages += 1
                    except Exception as e:
                        self._error_message = f"第{page}页数据保存失败: {str(e)}"
                        self._status = "error"
                        self._elapsed_seconds = int(time.time() - self._start_time)
                        _emit_log('ERROR', self._error_message)
                        return
                elif not items:
                    _emit_log('WARNING', f'任务[{self._task_id}] 第{page}页未解析到数据')

                if page < total_pages and not self._stop_flag.is_set():
                    time.sleep(max(interval_seconds, 1))

        except Exception as e:
            self._error_message = f"爬取过程异常: {str(e)}"
            self._status = "error"
            _emit_log('ERROR', self._error_message)
        finally:
            session.close()
            if self._status == "running":
                self._status = "completed"
            self._elapsed_seconds = int(time.time() - self._start_time)
            # 完成任务后更新数据库状态
            if self._task_id and db_callback:
                try:
                    # 通知外部更新任务状态
                    db_callback({'type': 'complete', 'task_id': self._task_id, 'status': self._status})
                except Exception as e:
                    print(f"[Crawler] Update task status error: {e}")

    def start(self, target_url, total_pages, interval_seconds, db_callback, crawl_mode="link", task_id=None):
        """
        启动爬虫任务
        :param target_url: 目标网址
        :param total_pages: 总爬取页数
        :param interval_seconds: 请求间隔（秒）
        :param db_callback: 数据库保存回调函数，接收爬取结果列表
        :param crawl_mode: 爬取模式，可选值: "link"(只爬链接), "image"(只爬图片), "mixed"(混合模式)
        :param task_id: 任务ID，用于完成后更新数据库
        """
        if self._status == "running":
            return False, "爬虫已在运行中，请先停止当前任务"

        if not target_url or not target_url.startswith(("http://", "https://")):
            return False, "请输入有效的网址（以 http:// 或 https:// 开头）"

        if total_pages < 1 or total_pages > 100:
            return False, "爬取页数需在 1-100 之间"

        if interval_seconds < 1 or interval_seconds > 60:
            return False, "请求间隔需在 1-60 秒之间"

        # 设置爬取模式
        if crawl_mode in (self.CRAWL_MODE_LINK, self.CRAWL_MODE_IMAGE, self.CRAWL_MODE_MIXED):
            self._crawl_mode = crawl_mode
        else:
            self._crawl_mode = self.CRAWL_MODE_LINK

        self._task_id = task_id
        self._crawl_thread = threading.Thread(
            target=self._crawl_task,
            args=(target_url, total_pages, interval_seconds, db_callback),
            daemon=True
        )
        self._crawl_thread.start()
        return True, "爬虫任务已启动"

    def stop(self):
        """停止爬虫任务"""
        if self._status != "running":
            return False, "当前没有正在运行的爬虫任务"

        self._stop_flag.set()
        self._status = "stopping"
        return True, "停止信号已发送，等待当前页面完成后停止"

    def get_status(self):
        """获取爬虫当前状态信息"""
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
        """重置爬虫状态"""
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
        return True, "爬虫状态已重置"


crawler_engine = CrawlerEngine()