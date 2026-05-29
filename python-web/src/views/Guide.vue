<template>
  <div class="page">
    <NavBar />
    <div class="content">
      <div class="page-header">
        <h1 class="page-title">系统使用说明</h1>
        <p class="page-sub">全面了解 CrawlMaster 爬虫管理系统的各项功能与操作流程</p>
      </div>

      <div class="guide-layout">
        <aside class="guide-sidebar">
          <div class="sidebar-card">
            <div class="sidebar-title">目录导航</div>
            <nav class="sidebar-nav">
              <a
                v-for="section in sections"
                :key="section.id"
                class="sidebar-link"
                :class="{ active: activeSection === section.id }"
                @click.prevent="scrollToSection(section.id)"
              >
                <span class="sidebar-num">{{ section.num }}</span>
                <span>{{ section.title }}</span>
              </a>
            </nav>
          </div>
        </aside>

        <div class="guide-main">
          <div
            v-for="section in sections"
            :key="section.id"
            :id="section.id"
            class="guide-section"
          >
            <div class="section-header" @click="toggleSection(section.id)">
              <div class="section-header-left">
                <span class="section-num">{{ section.num }}</span>
                <h2 class="section-title">{{ section.title }}</h2>
              </div>
              <div class="section-header-right">
                <svg
                  class="section-chevron"
                  :class="{ expanded: expandedSections.has(section.id) }"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </div>
            </div>

            <transition name="collapse">
              <div v-if="expandedSections.has(section.id)" class="section-body">
                <div class="section-intro" v-if="section.intro">{{ section.intro }}</div>

                <!-- 系统介绍 -->
                <template v-if="section.id === 'intro'">
                  <div class="feature-highlights">
                    <div class="highlight-card">
                      <div class="highlight-icon highlight-crawler">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M11 8v6"/><path d="M8 11h6"/>
                        </svg>
                      </div>
                      <h4>爬虫任务管理</h4>
                      <p>支持创建爬虫任务、数据采集、监控任务三种类型，配置并发数、请求间隔、代理组等参数</p>
                    </div>
                    <div class="highlight-card">
                      <div class="highlight-icon highlight-task">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                          <rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 12h6"/><path d="M12 9v6"/>
                        </svg>
                      </div>
                      <h4>定时任务调度</h4>
                      <p>支持按分钟设置执行周期，自动定时运行采集任务，灵活控制采集频率</p>
                    </div>
                    <div class="highlight-card">
                      <div class="highlight-icon highlight-data">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                      </div>
                      <h4>数据查看与导出</h4>
                      <p>数据预览、清洗、导出完整链路，支持多格式数据输出</p>
                    </div>
                    <div class="highlight-card">
                      <div class="highlight-icon highlight-proxy">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        </svg>
                      </div>
                      <h4>代理池与反爬</h4>
                      <p>内置代理池管理，支持代理组配置，保障采集过程中的 IP 可用性</p>
                    </div>
                  </div>

                  <div class="info-block">
                    <div class="info-block-header">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
                      </svg>
                      <span>系统架构概览</span>
                    </div>
                    <p>CrawlMaster 采用前后端分离架构，前端基于 <strong>Vue 3 + Element Plus</strong> 构建，后端基于 <strong>Python Flask</strong>。系统包含任务管理、数据管理、代理管理、系统监控四大核心模块，提供从任务创建到数据导出的完整工作流。任务模板支持保存和复用常用配置，代理池管理支持多代理组配置，系统日志记录所有运行详情。</p>
                  </div>
                </template>

                <!-- 爬虫任务创建 -->
                <template v-if="section.id === 'task-create'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>进入任务管理页面</h4>
                        <p>在顶部导航栏中，将鼠标悬停在 <strong>「任务管理」</strong> 上，在下拉菜单中点击 <strong>「任务列表」</strong> 进入任务管理页面。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>点击新建任务</h4>
                        <p>在任务列表页面，点击右上角的 <strong>「新建任务」</strong> 按钮，进入任务创建表单页面。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>选择模板（可选）</h4>
                        <p>表单顶部提供 <strong>「从模板创建」</strong> 选择器，可从已有模板中加载配置。系统内置多种常用模板，选择后可自动填充各项配置参数，无需手动填写。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">4</div>
                      <div class="step-content">
                        <h4>填写任务配置</h4>
                        <div class="step-detail-list">
                          <p><strong>任务名称</strong>：为任务设置一个易于识别的名称，如「新闻头条采集」。</p>
                          <p><strong>目标 URL</strong>：输入需要采集的目标网页地址，当前版本仅支持单个 URL 输入。</p>
                          <p><strong>执行周期（分钟）</strong>：设置任务的自动执行间隔，如设置为 30 表示每 30 分钟自动运行一次，设为 0 则仅手动触发。</p>
                          <p><strong>爬取页数</strong>：设置每次执行时最多爬取的页面数量上限。</p>
                          <p><strong>并发数</strong>：设置同时进行的并发请求数量，并发数越高速度越快，但也会增加服务器压力。</p>
                          <p><strong>请求间隔（秒）</strong>：每次请求之间等待的秒数，用于避免请求过于频繁被目标网站封禁。</p>
                          <p><strong>最大重试次数</strong>：请求失败后的自动重试次数，默认为 3 次。</p>
                          <p><strong>重试间隔（秒）</strong>：重试之间的等待时间。</p>
                        </div>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">5</div>
                      <div class="step-content">
                        <h4>选择任务类型与爬取模式</h4>
                        <div class="step-detail-list">
                          <p><strong>任务类型</strong>：支持「爬虫任务」「数据采集」「监控任务」三种类型，根据采集场景选择。</p>
                          <p><strong>爬取模式</strong>：支持「链接模式」「图片模式」「混合模式」，根据需要采集的内容类型选择。</p>
                          <p><strong>代理组</strong>：如有需要，可指定使用哪个代理组来执行任务，留空则不使用代理。</p>
                          <p><strong>请求头</strong>：以 JSON 格式填写自定义请求头，如 User-Agent、Cookie 等。</p>
                        </div>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">6</div>
                      <div class="step-content">
                        <h4>保存任务</h4>
                        <p>完成所有配置后，点击页面底部的 <strong>「创建任务」</strong> 按钮。任务创建成功后将自动跳转回任务列表，此时任务状态为「已停止」，需要手动启动。</p>
                      </div>
                    </div>
                  </div>

                  <div class="tip-block">
                    <div class="tip-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
                      </svg>
                    </div>
                    <div class="tip-content">
                      <strong>提示</strong>：建议优先使用模板创建任务，模板中已预置了常用的采集规则和配置，可大幅减少手动配置的工作量。
                    </div>
                  </div>
                </template>

                <!-- 任务启动停止 -->
                <template v-if="section.id === 'task-run'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>进入任务列表</h4>
                        <p>通过导航栏 <strong>「任务管理」→「任务列表」</strong> 进入任务列表页面，查看所有已创建的任务。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>查看任务卡片信息</h4>
                        <p>每个任务卡片上方会展示关键信息：<strong>任务 ID</strong>、<strong>目标 URL</strong>、<strong>更新/创建时间</strong>（有更新记录显示「更新于」，刚创建的任务显示「创建于」）、<strong>耗时</strong>、<strong>数据量</strong>、<strong>爬取模式</strong>、<strong>页数</strong>、<strong>并发</strong>、<strong>调度周期</strong>、<strong>请求间隔</strong>及<strong>代理组</strong>等；<strong>成功率</strong>仍以进度条形式展示在下方。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>启动任务</h4>
                        <p>点击任务卡片上的 <strong>「启动」</strong> 按钮。新任务将直接开始运行；对于已经执行过的任务，启动时会复制为新任务记录再运行，以保留历史执行数据。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">4</div>
                      <div class="step-content">
                        <h4>重新启动任务</h4>
                        <p>对于已完成或失败的任务，除「启动」外还会显示 <strong>「重新启动」</strong> 按钮。重新启动会在<strong>当前任务</strong>上再次执行采集，不会新建任务记录，适合在同一任务上快速重跑。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">5</div>
                      <div class="step-content">
                        <h4>停止任务</h4>
                        <p>运行中的任务可点击 <strong>「停止」</strong> 按钮立即终止采集，已采集的数据不会丢失。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">6</div>
                      <div class="step-content">
                        <h4>查看任务详情</h4>
                        <p>点击任务名称，进入 <strong>任务详情页</strong>，可查看任务的完整配置信息、采集进度、已采集数据量、运行日志、版本历史等详细数据。</p>
                      </div>
                    </div>
                  </div>

                  <div class="status-indicators">
                    <div class="status-card status-running">
                      <span class="status-dot running"></span>
                      <span class="status-label">运行中</span>
                      <span class="status-desc">任务正在执行采集</span>
                    </div>
                    <div class="status-card status-stopped">
                      <span class="status-dot stopped"></span>
                      <span class="status-label">待执行</span>
                      <span class="status-desc">任务已创建，等待启动</span>
                    </div>
                    <div class="status-card status-error">
                      <span class="status-dot error"></span>
                      <span class="status-label">异常</span>
                      <span class="status-desc">任务执行中遇到错误</span>
                    </div>
                    <div class="status-card status-completed">
                      <span class="status-dot completed"></span>
                      <span class="status-label">已完成</span>
                      <span class="status-desc">任务已成功完成全部采集</span>
                    </div>
                  </div>

                  <div class="tip-block">
                    <div class="tip-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
                      </svg>
                    </div>
                    <div class="tip-content">
                      <strong>提示</strong>：如果任务配置了「定时调度」，系统会在设定的时间自动启动任务，无需手动操作。任务列表中的状态会实时更新。
                    </div>
                  </div>
                </template>

                <!-- 模板使用 -->
                <template v-if="section.id === 'templates'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>进入模板管理页面</h4>
                        <p>通过导航栏 <strong>「任务管理」→「任务模板」</strong> 进入模板管理页面，查看系统内置模板和自定义模板列表。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>浏览与筛选模板</h4>
                        <p>模板按类别分组管理，支持筛选 <strong>「全部」</strong>、<strong>「通用」</strong>、<strong>「电商」</strong>、<strong>「资讯」</strong>、<strong>「监控」</strong> 五个类别。可勾选「仅常用」仅显示标记为常用的模板。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>使用模板创建任务</h4>
                        <p>找到合适的模板后，点击模板卡片上的 <strong>「使用此模板」</strong> 按钮，系统将自动跳转到新建任务页面，并预填充模板中的全部配置项（如目标 URL、执行周期、爬取模式、并发数等），仅需修改目标 URL 即可快速创建任务。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">4</div>
                      <div class="step-content">
                        <h4>创建自定义模板</h4>
                        <p>点击页面右上角的 <strong>「创建模板」</strong> 按钮，填写模板名称、描述、选择类别，并配置各项采集参数，即可创建自定义模板。创建完成后可在新建任务时选择使用。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">5</div>
                      <div class="step-content">
                        <h4>管理常用模板</h4>
                        <p>点击模板卡片上的星标按钮可将模板标记为「常用」，方便快速筛选和定位高频使用的模板配置。</p>
                      </div>
                    </div>
                  </div>

                  <div class="tip-block">
                    <div class="tip-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
                      </svg>
                    </div>
                    <div class="tip-content">
                      <strong>提示</strong>：模板可以大幅提高批量创建相似任务的效率。建议将常用网站的采集配置保存为模板，下次使用时直接加载即可，无需重新配置。
                    </div>
                  </div>
                </template>

                <!-- 数据查看导出 -->
                <template v-if="section.id === 'data-export'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>数据预览</h4>
                        <p>通过导航栏 <strong>「数据管理」→「数据预览」</strong> 进入数据预览页面。选择对应的任务后，系统将展示该任务已采集到的所有数据记录，以表格形式呈现。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>数据筛选与搜索</h4>
                        <p>在数据预览页面顶部，可以使用搜索框对数据进行关键词检索，或使用列过滤器按字段值进行精确筛选，快速定位目标数据。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>数据清洗</h4>
                        <p>通过 <strong>「数据管理」→「数据清洗」</strong> 进入数据清洗页面。可对采集数据进行去重、空值处理、格式标准化、文本清洗等操作，确保数据质量。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">4</div>
                      <div class="step-content">
                        <h4>数据导出</h4>
                        <p>通过 <strong>「数据管理」→「数据导出」</strong> 进入数据导出页面。选择需要导出的任务和字段，选择导出格式（支持 JSON、CSV、Excel），点击导出按钮即可下载数据文件。</p>
                      </div>
                    </div>
                  </div>

                  <div class="export-formats">
                    <div class="format-card">
                      <div class="format-badge json">JSON</div>
                      <p>结构化数据格式，适合程序读取和 API 对接</p>
                    </div>
                    <div class="format-card">
                      <div class="format-badge csv">CSV</div>
                      <p>表格数据格式，通用性强，Excel / WPS 可直接打开</p>
                    </div>
                    <div class="format-card">
                      <div class="format-badge xlsx">Excel</div>
                      <p>富格式电子表格，支持样式、公式和多 Sheet</p>
                    </div>
                  </div>
                </template>

                <!-- 日志查看 -->
                <template v-if="section.id === 'logs'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>进入系统日志页面</h4>
                        <p>通过导航栏 <strong>「系统监控」→「系统日志」</strong> 进入系统日志页面，查看系统运行过程中的所有日志记录。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>日志筛选</h4>
                        <p>日志页面顶部提供筛选工具，可按 <strong>日志级别</strong>（DEBUG / INFO / WARNING / ERROR）、<strong>时间范围</strong>、<strong>来源模块</strong> 等维度进行过滤，快速定位关注的信息。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>查看任务日志</h4>
                        <p>在任务详情页中也可以查看该任务专属的运行日志，包括请求记录、解析结果、错误堆栈等信息，便于排查单个任务的问题。</p>
                      </div>
                    </div>
                  </div>

                  <div class="log-levels">
                    <div class="level-badge level-debug">
                      <span class="level-dot debug"></span>
                      <span>DEBUG</span>
                      <span class="level-desc">详细调试信息</span>
                    </div>
                    <div class="level-badge level-info">
                      <span class="level-dot info"></span>
                      <span>INFO</span>
                      <span class="level-desc">一般运行信息</span>
                    </div>
                    <div class="level-badge level-warning">
                      <span class="level-dot warning"></span>
                      <span>WARNING</span>
                      <span class="level-desc">警告信息</span>
                    </div>
                    <div class="level-badge level-error">
                      <span class="level-dot error"></span>
                      <span>ERROR</span>
                      <span class="level-desc">错误信息</span>
                    </div>
                  </div>
                </template>

                <!-- 系统设置 -->
                <template v-if="section.id === 'settings'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>进入系统设置页面</h4>
                        <p>点击导航栏右上角的 <strong>齿轮图标</strong>（⚙），或点击用户名旁边的设置按钮，进入系统设置页面。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>个人资料设置</h4>
                        <p>在 <strong>「个人资料」</strong> 标签页中，可以设置昵称、头像 URL、个人简介等信息，完善个人账户资料。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>安全设置</h4>
                        <p>在 <strong>「安全设置」</strong> 标签页中，可以修改登录密码。需要先输入当前密码，再输入新密码并确认，完成密码更新。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">4</div>
                      <div class="step-content">
                        <h4>通知设置</h4>
                        <p>在 <strong>「通知设置」</strong> 标签页中，可配置任务完成通知、异常告警通知等方式，支持站内通知和邮件通知（需先绑定邮箱）。</p>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 主题切换 -->
                <template v-if="section.id === 'theme'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>进入主题设置</h4>
                        <p>在系统设置页面的 <strong>「主题设置」</strong> 标签页中，可以查看和切换系统主题。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>选择主题</h4>
                        <p>系统提供以下多种精心设计的主题方案：</p>
                        <div class="theme-grid">
                          <div class="theme-card">
                            <div class="theme-swatch pure-black"></div>
                            <div class="theme-info">
                              <strong>极简曜黑</strong>
                              <span>纯粹极致黑</span>
                            </div>
                          </div>
                          <div class="theme-card">
                            <div class="theme-swatch space-gray"></div>
                            <div class="theme-info">
                              <strong>深空青灰</strong>
                              <span>冷调星空灰</span>
                            </div>
                          </div>
                          <div class="theme-card">
                            <div class="theme-swatch default-blue"></div>
                            <div class="theme-info">
                              <strong>默认蓝紫</strong>
                              <span>经典蓝紫渐变</span>
                            </div>
                          </div>
                          <div class="theme-card">
                            <div class="theme-swatch ice-blue"></div>
                            <div class="theme-info">
                              <strong>极地冰蓝</strong>
                              <span>清冷极地蓝</span>
                            </div>
                          </div>
                          <div class="theme-card">
                            <div class="theme-swatch night-rose"></div>
                            <div class="theme-info">
                              <strong>暗夜玫瑰</strong>
                              <span>深邃玫瑰红</span>
                            </div>
                          </div>
                          <div class="theme-card">
                            <div class="theme-swatch purple-gold"></div>
                            <div class="theme-info">
                              <strong>轻奢紫金</strong>
                              <span>奢华紫金调</span>
                            </div>
                          </div>
                          <div class="theme-card">
                            <div class="theme-swatch cyber-aurora"></div>
                            <div class="theme-info">
                              <strong>赛博极光</strong>
                              <span>未来赛博风</span>
                            </div>
                          </div>
                          <div class="theme-card">
                            <div class="theme-swatch elegant-white"></div>
                            <div class="theme-info">
                              <strong>雅致白</strong>
                              <span>纯净优雅白</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>应用主题</h4>
                        <p>点击任意主题卡片即可即时切换，主题设置会自动保存到本地存储，下次登录时自动加载。主题也会同步到后端服务器，保持多端一致。</p>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 开发与部署 -->
                <template v-if="section.id === 'dev-env'">
                  <div class="step-list">
                    <div class="step-item">
                      <div class="step-marker">1</div>
                      <div class="step-content">
                        <h4>统一配置文件</h4>
                        <p>前端 API 地址在 <strong>python-web/.env</strong> 中配置，远程与本地只需注释切换，无需修改多个文件。</p>
                        <div class="step-detail-list">
                          <p><strong>远程后端</strong>：<code>VITE_API_BASE_URL=https://crawler-vue3.onrender.com/api</code></p>
                          <p><strong>本地后端</strong>：<code>VITE_API_BASE_URL=http://127.0.0.1:5000/api</code></p>
                        </div>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">2</div>
                      <div class="step-content">
                        <h4>切换后重启前端</h4>
                        <p>修改 <code>.env</code> 后必须<strong>重启</strong> <code>npm run dev</code>，并在浏览器中硬刷新（Ctrl+Shift+R），否则可能仍使用旧地址。</p>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">3</div>
                      <div class="step-content">
                        <h4>确认当前连接的后端</h4>
                        <p>打开浏览器开发者工具 → Network，查看接口完整 URL：</p>
                        <div class="step-detail-list">
                          <p>以 <code>crawler-vue3.onrender.com</code> 开头 → 远程后端</p>
                          <p>以 <code>127.0.0.1:5000</code> 开头 → 本地后端</p>
                        </div>
                      </div>
                    </div>
                    <div class="step-item">
                      <div class="step-marker">4</div>
                      <div class="step-content">
                        <h4>本地联调启动顺序</h4>
                        <p>先启动后端 <code>cd python && python app.py</code>，再启动前端 <code>cd python-web && npm run dev</code>，访问 <code>http://localhost:3000</code>。</p>
                      </div>
                    </div>
                  </div>

                  <div class="tip-block">
                    <div class="tip-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
                      </svg>
                    </div>
                    <div class="tip-content">
                      <strong>注意</strong>：请勿创建 <code>.env.local</code>，Vite 会优先读取它并覆盖 <code>.env</code> 中的配置，导致切换无效。
                    </div>
                  </div>
                </template>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavBar from '../components/NavBar.vue'

const sections = [
  { id: 'intro', num: '01', title: '系统介绍', intro: 'CrawlMaster 是一款企业级爬虫管理系统，提供可视化的爬虫任务创建、调度、监控和数据管理能力，帮助用户高效完成 Web 数据采集工作。' },
  { id: 'task-create', num: '02', title: '爬虫任务创建流程', intro: '通过任务管理模块，您可以轻松创建和管理爬虫采集任务。以下是完整的任务创建操作步骤：' },
  { id: 'task-run', num: '03', title: '任务启动与停止', intro: '创建任务后，需要对任务进行启动、停止等生命周期管理。以下是任务运行管理的操作步骤：' },
  { id: 'templates', num: '04', title: '模板使用流程', intro: '任务模板可以帮助您快速复用采集配置，大幅提高任务创建效率。以下是模板的使用方法：' },
  { id: 'data-export', num: '05', title: '数据查看与导出', intro: '采集完成的数据可以进行预览、清洗和导出。以下是数据处理全流程的操作步骤：' },
  { id: 'logs', num: '06', title: '日志查看', intro: '系统日志和任务日志记录了运行的详细信息，是排查问题和监控状态的重要工具。' },
  { id: 'settings', num: '07', title: '系统设置使用', intro: '系统设置模块提供个人资料、安全、通知等个性化配置功能。以下是各项设置的操作步骤：' },
  { id: 'theme', num: '08', title: '主题切换使用', intro: '系统内置多套精心设计的主题方案，支持一键切换，满足不同视觉偏好。以下是主题切换的操作步骤：' },
  { id: 'dev-env', num: '09', title: '开发与 API 配置', intro: '本地开发与远程部署时，通过单一配置文件切换后端地址。以下是环境配置说明：' }
]

const expandedSections = ref(new Set(['intro']))
const activeSection = ref('intro')

function toggleSection(id) {
  if (expandedSections.value.has(id)) {
    expandedSections.value.delete(id)
  } else {
    expandedSections.value.add(id)
  }
  expandedSections.value = new Set(expandedSections.value)
}

function scrollToSection(id) {
  activeSection.value = id
  if (!expandedSections.value.has(id)) {
    expandedSections.value.add(id)
    expandedSections.value = new Set(expandedSections.value)
  }
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

onMounted(() => {
  const hash = window.location.hash?.replace('#', '')
  if (hash && sections.some(s => s.id === hash)) {
    scrollToSection(hash)
  }
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--bg-primary);
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px;
}

.page-header {
  margin-bottom: 36px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
  margin-bottom: 8px;
}

.page-sub {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 400;
}

.guide-layout {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.guide-sidebar {
  width: 220px;
  flex-shrink: 0;
  position: sticky;
  top: 92px;
}

.sidebar-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 20px;
  backdrop-filter: blur(20px);
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 16px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.sidebar-link:hover {
  color: var(--text-primary);
  background: var(--card-hover-bg);
}

.sidebar-link.active {
  color: var(--active-color);
  background: var(--active-bg);
  font-weight: 600;
}

.sidebar-num {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  min-width: 20px;
}

.sidebar-link.active .sidebar-num {
  color: var(--accent-primary);
}

.guide-main {
  flex: 1;
  min-width: 0;
}

.guide-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  margin-bottom: 16px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  transition: border-color 0.3s ease;
}

.guide-section:hover {
  border-color: rgba(var(--accent-rgb), 0.2);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s ease;
}

.section-header:hover {
  background: var(--card-hover-bg);
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.section-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--active-bg);
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.2px;
}

.section-chevron {
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  transition: transform 0.3s ease;
}

.section-chevron.expanded {
  transform: rotate(180deg);
}

.section-body {
  padding: 0 24px 24px;
}

.section-intro {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 24px;
  padding: 14px 18px;
  background: rgba(var(--accent-rgb), 0.04);
  border-radius: 10px;
  border-left: 3px solid var(--accent-primary);
}

.feature-highlights {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}

.highlight-card {
  background: rgba(var(--accent-rgb), 0.04);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.25s ease;
}

.highlight-card:hover {
  background: var(--card-hover-bg);
  border-color: rgba(var(--accent-rgb), 0.18);
  transform: translateY(-2px);
}

.highlight-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.highlight-icon svg {
  width: 20px;
  height: 20px;
  color: #fff;
}

.highlight-crawler { background: linear-gradient(135deg, #4c6ef5, #7c3aed); }
.highlight-task { background: linear-gradient(135deg, #10b981, #059669); }
.highlight-data { background: linear-gradient(135deg, #f59e0b, #d97706); }
.highlight-proxy { background: linear-gradient(135deg, #06b6d4, #0ea5e9); }

.highlight-card h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.highlight-card p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.info-block {
  background: rgba(var(--accent-rgb), 0.04);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 18px 20px;
}

.info-block-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.info-block-header svg {
  width: 18px;
  height: 18px;
  color: var(--accent-primary);
}

.info-block-header span {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.info-block p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.step-item {
  display: flex;
  gap: 16px;
  padding: 18px 0;
  border-bottom: 1px solid var(--border-color);
}

.step-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.step-item:first-child {
  padding-top: 0;
}

.step-marker {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: var(--btn-shadow);
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.step-content p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 2px;
}

.step-content p:last-child {
  margin-bottom: 0;
}

.step-detail-list {
  margin-top: 6px;
}

.step-detail-list p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
  padding-left: 12px;
  border-left: 2px solid var(--border-color);
  margin-bottom: 6px;
}

.tip-block {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding: 16px 18px;
  background: rgba(var(--accent-rgb), 0.05);
  border: 1px solid rgba(var(--accent-rgb), 0.1);
  border-radius: 10px;
}

.tip-icon {
  flex-shrink: 0;
}

.tip-icon svg {
  width: 20px;
  height: 20px;
  color: var(--accent-primary);
}

.tip-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.tip-content strong {
  color: var(--accent-primary);
}

.status-indicators {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 24px 0;
}

.status-card {
  background: rgba(var(--accent-rgb), 0.04);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 14px;
  text-align: center;
  transition: all 0.2s ease;
}

.status-card:hover {
  border-color: rgba(var(--accent-rgb), 0.2);
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-bottom: 8px;
}

.status-dot.running { background: #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5); }
.status-dot.stopped { background: var(--text-muted); }
.status-dot.error { background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.5); }
.status-dot.completed { background: #4c6ef5; box-shadow: 0 0 8px rgba(76, 110, 245, 0.5); }

.status-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.status-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.export-formats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 24px 0;
}

.format-card {
  background: rgba(var(--accent-rgb), 0.04);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 16px;
  transition: all 0.2s ease;
}

.format-card:hover {
  border-color: rgba(var(--accent-rgb), 0.2);
  transform: translateY(-2px);
}

.format-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.format-badge.json { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.format-badge.csv { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.format-badge.xlsx { background: rgba(76, 110, 245, 0.15); color: #4c6ef5; }

.format-card p {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.log-levels {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 24px 0;
}

.level-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 12px;
  background: rgba(var(--accent-rgb), 0.04);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.level-badge:hover {
  border-color: rgba(var(--accent-rgb), 0.2);
}

.level-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.level-dot.debug { background: #6b7280; }
.level-dot.info { background: #3b82f6; box-shadow: 0 0 6px rgba(59, 130, 246, 0.4); }
.level-dot.warning { background: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.4); }
.level-dot.error { background: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.4); }

.level-desc {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-muted);
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-top: 10px;
}

.theme-card {
  background: rgba(var(--accent-rgb), 0.04);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.25s ease;
}

.theme-card:hover {
  border-color: rgba(var(--accent-rgb), 0.25);
  transform: translateY(-2px);
}

.theme-swatch {
  height: 48px;
}

.theme-swatch.pure-black { background: linear-gradient(135deg, #050505 30%, #1a1a1a); }
.theme-swatch.space-gray { background: linear-gradient(135deg, #0f172a 30%, #1e293b); }
.theme-swatch.default-blue { background: linear-gradient(135deg, #0d1117 30%, #4c6ef5); }
.theme-swatch.ice-blue { background: linear-gradient(135deg, #0c1119 30%, #38bdf8); }
.theme-swatch.night-rose { background: linear-gradient(135deg, #1c1412 30%, #d4877a); }
.theme-swatch.purple-gold { background: linear-gradient(135deg, #0f0d14 30%, #a855f7); }
.theme-swatch.cyber-aurora { background: linear-gradient(135deg, #0a0e17 30%, #06b6d4); }
.theme-swatch.elegant-white { background: linear-gradient(135deg, #f8fafc 30%, #e2e8f0); border-bottom: 1px solid rgba(0,0,0,0.06); }

.theme-info {
  padding: 12px 14px;
}

.theme-info strong {
  display: block;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 3px;
}

.theme-info span {
  font-size: 11px;
  color: var(--text-muted);
}

.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 2000px;
}

@media (max-width: 960px) {
  .guide-layout {
    flex-direction: column;
  }

  .guide-sidebar {
    width: 100%;
    position: static;
  }

  .sidebar-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 6px;
  }

  .sidebar-link {
    font-size: 12px;
    padding: 7px 10px;
  }

  .feature-highlights,
  .status-indicators,
  .export-formats,
  .log-levels {
    grid-template-columns: repeat(2, 1fr);
  }

  .theme-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .feature-highlights,
  .status-indicators,
  .export-formats,
  .log-levels,
  .theme-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 22px;
  }
}
</style>