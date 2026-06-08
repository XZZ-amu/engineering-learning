# 工程知识学习

为产品设计师定制的工程基础学习站。

这个仓库不是为了把产品设计师训练成工程师，而是帮助非代码背景的人理解现代软件产品背后的关键工程逻辑：能听懂研发讨论，能判断方案 tradeoff，能在产品设计阶段提前识别技术约束。

内容围绕 AI 创作产品的核心链路展开：

```txt
用户提交请求
  -> 异步调度 AI 任务
  -> 生成图片/视频等大文件
  -> 存储、分发、展示给用户
  -> 处理登录、付费、进度、安全、性能等真实产品问题
```

## 适合谁

- 产品设计师、产品经理、独立创作者
- 不以写代码为主要目标，但需要和研发高质量协作的人
- 正在用 Claude Code / Codex / Cursor 等 AI 编程工具做产品原型的人
- 想从“知道术语”进到“能判断技术方案是否合理”的人

不适合：

- 想系统学习编程语言语法的人
- 想找完整工程模板或可直接复用业务代码的人
- 已经有扎实工程经验、只需要查 API 文档的人

## 学习方式

每个章节都尽量遵循同一套结构：

1. 用一句话说明这个领域在解决什么根本问题
2. 解释如果没有这种设计，会发生什么
3. 把概念组织成一张关系图，而不是词典式罗列
4. 结合 AI 创作产品或 Mindloop 的真实场景解释取舍
5. 给出研发经常争论的方案分歧
6. 用选择题检查是否真的理解

目标不是背术语，而是能输出自己的判断。例如：当研发说“这个生成任务要走队列，不能同步等结果”时，你能理解这背后是在处理耗时任务、并发、失败重试和用户体验之间的取舍。

## 内容结构

当前课程按优先级分为三层。

### P0：每天都会碰到

- 异步任务与队列
- API 设计
- 文件与存储
- 前端状态与数据流

### P1：做好产品必须懂

- AI 工程基础
- 数据库基础
- 认证与付费
- WebSocket 与实时通信

### P2：从能做到做得好

- 系统设计
- 性能与体验优化
- 安全基础

已生成的章节放在 [`docs/chapters`](docs/chapters) 目录，并通过 MkDocs 生成站点。

## 在线阅读

站点地址：

https://xzz-amu.github.io/engineering-learning/

## 本地预览

先安装依赖：

```bash
pip install -r requirements.txt
```

启动本地文档站：

```bash
mkdocs serve
```

然后打开：

```txt
http://127.0.0.1:8000/
```

## 自动生成教案

这个仓库支持从 GitHub Issues 自动生成章节。

基本流程：

1. 在 GitHub Issues 中创建一个学习主题
2. 给 Issue 打上 `待生成` label
3. 运行生成脚本
4. 脚本调用 Claude API 生成教案
5. 生成内容保存到 `docs/chapters/`
6. 更新 `mkdocs.yml` 导航
7. 提交并推送到 GitHub
8. GitHub Pages 自动部署

运行脚本：

```bash
python3 scripts/generate-chapters.py
```

需要提前准备：

- 已安装并登录 GitHub CLI：`gh auth login`
- 可用的 Anthropic API 环境变量：`ANTHROPIC_API_KEY`
- 如果使用自定义 API 网关，可配置 `ANTHROPIC_BASE_URL`
- 如果需要指定模型，可配置 `ANTHROPIC_DEFAULT_SONNET_MODEL`

## 目录说明

```txt
.
├── docs/
│   ├── index.md                 # 文档站首页
│   ├── chapters/                # 教案章节
│   ├── javascripts/             # 测验、学习进度等交互脚本
│   ├── stylesheets/             # 交互样式
│   └── references.md            # 参考资料
├── prompts/
│   └── chapter-system-prompt.md # 生成教案使用的系统提示词
├── scripts/
│   └── generate-chapters.py     # 从 Issue 生成章节的脚本
├── mkdocs.yml                   # MkDocs 站点配置
└── requirements.txt             # Python 依赖
```

## 部署

仓库配置了 GitHub Actions。

当 `main` 分支里的 `docs/**` 或 `mkdocs.yml` 发生变化时，会自动构建 MkDocs 站点并部署到 GitHub Pages。

也可以在 GitHub Actions 页面手动触发部署。

## 当前状态

这是一个个人学习仓库，重点是沉淀面向产品设计师的工程理解框架。

当前还不是通用课程产品，已知限制包括：

- 没有完整的新手引导路径
- 自动生成流程偏个人工作流
- 部分章节仍需要继续校对和补案例
- 章节质量依赖 Issue 描述和生成提示词质量

后续可以继续补：

- 更清晰的学习路线
- 每章的阅读状态和复盘入口
- 面向不同角色的学习建议
- 更稳定的自动生成与校对流程
