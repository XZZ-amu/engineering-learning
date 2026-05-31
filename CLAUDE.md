# 工程知识学习项目

为产品设计师定制的工程基础教材。目标不是学会写代码，而是达到能跟研发平等对话、管理 AI 团队的水平。

## 用户画像

- 产品设计师，不懂代码
- 已经在用 Claude Code 做 vibe coding（有 Mindloop 项目实践经验）
- 目标：达到开发实习生水平，能跟研发平等对话
- 学习方式偏好：先问问题摸底 → 用生活类比解释 → 用 Mindloop 真实案例举例 → 出题验证

## 学习目标

从"听不懂研发在说什么"到"能判断技术方案对不对、能问出有效问题"。

## 已掌握（不需要重复）

以下内容已经在 Mindloop 项目实践中学过且验证通过：

### Git（已吃透）
- 核心：commit、push、pull、clone、branch、merge、PR、conflict、diff、Issue
- 日常：stage、stash、revert vs reset、tag、.gitignore、fork
- 进阶：cherry-pick、rebase、squash、worktree、GitHub Actions

### 代码架构（已掌握核心）
- 五大原则：职责分离、编排器、配置集中、DRY、分层
- 七种模式：编排器、分层、事件驱动、客户端-服务端、插件、微服务、管道
- 角色术语：前端/后端/中间件/数据库/缓存/队列/网关
- Native vs WebView
- 设计模式基础：单例、工厂、观察者、策略、装饰器、适配器、发布-订阅
- 选架构的五个维度

### 部署与运维（已掌握）
- 部署本质、服务器类型、Docker/容器
- 网络基础：localhost/内网/公网、域名+DNS、HTTPS
- CI/CD、灰度发布、回滚、负载均衡
- 环境区分、日志、监控/报警/健康检查

### Spec 与开发流程（已掌握）
- 写代码前的六步流程
- Spec 怎么读、审 Spec 的检查清单
- 技术债、重构的概念

## 待学习（按优先级）

> 课表围绕 AI 创作产品（文生图/视频）的核心链路设计：
> "用户提交请求 → 异步调 AI → 拿到大文件 → 展示给用户"

### P0：每天都会碰到的
1. **异步任务与队列** — 任务提交、轮询/推送、超时重试、状态机 (#5)
2. **API 设计** — RESTful 规范、请求/响应结构、错误码、版本管理 (#6)
3. **文件与存储** — 上传、OSS/S3、CDN、缩略图、格式转换 (#7)
4. **前端状态与数据流（React）** — 组件、状态管理、渲染、hooks (#8)

### P1：做好产品必须懂的
5. **AI 工程基础** — 模型调用、prompt 结构、采样参数、工作流 (#9)
6. **数据库基础** — SQL vs NoSQL、表结构设计、查询、索引 (#10)
7. **认证与付费** — 登录机制、Token、OAuth、用量计费、订阅 (#11)
8. **WebSocket 与实时通信** — 长连接、推送、生成进度、断线重连 (#12)

### P2：从能做到做得好
9. **系统设计** — 从零画出 AI 创作产品的技术蓝图 (#13)
10. **性能与体验优化** — 懒加载、缓存策略、骨架屏、队列优先级 (#14)
11. **安全基础** — 内容安全、API 防滥用、用户数据保护 (#15)

## 教材要求

- 每个知识点用 Mindloop 或真实产品案例举例
- 用生活类比解释概念，不用技术黑话
- 每个章节末尾有"考考你"环节（选择题或简答）
- 内容存在 `chapters/` 目录下，每个知识点一个 markdown 文件
- 适合 10-15 分钟一个章节的阅读量

## 已有教材（在 Mindloop 项目的面试目录里）

以下文档已经写好，不需要重复：
- `软件工程全流程指南.md`
- `Git完整知识指南.md`
- `代码架构与开发前准备指南.md`
- `部署与运维指南.md`
- `工程基础学习路线图.md`

位置：`~/Documents/Obsidian/笔记引发思考/00-项目/面试/mindloop/`

## 任务拆分

每个待学习的知识点 = 一个 GitHub Issue = 一个教材章节。
AI 按 Issue 逐个生成教材，存入 `chapters/` 目录。

## 自动任务

每次对话开始时，先跑一下 `python3 scripts/generate-chapters.py`，检查有没有待生成的教案。如果有，生成完再跟用户打招呼；如果没有（输出"没有待生成的 Issue"），直接进入对话。

## 启动方式

```bash
cd ~/Projects/engineering-learning && claude --dangerously-skip-permissions
```

或者加 alias：
```bash
alias elccds='cd ~/Projects/engineering-learning && claude --dangerously-skip-permissions'
```
