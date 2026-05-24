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

### P0：需要深入的
1. **前端基础** — React 组件的工作方式、状态管理、数据流（因为桌面端在用）
2. **API 设计深入** — RESTful 规范、错误码、版本管理
3. **数据库基础** — SQL vs NoSQL、表结构设计、查询
4. **网络协议** — HTTP 请求/响应的完整过程、状态码含义

### P1：有余力时
5. **性能优化** — 前端性能、后端性能、常见瓶颈
6. **安全基础** — XSS、CSRF、SQL 注入（知道是什么就行）
7. **系统设计入门** — 怎么从零设计一个系统的思路

### P2：扩展视野
8. **开源生态** — npm/pip 包管理、开源协议、如何评估开源项目
9. **AI 工程** — LLM 调用、prompt engineering、embedding、RAG
10. **产品技术沟通** — 怎么写技术需求、怎么评估工期合理性

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

## 启动方式

```bash
cd ~/Projects/engineering-learning && claude --dangerously-skip-permissions
```

或者加 alias：
```bash
alias elccds='cd ~/Projects/engineering-learning && claude --dangerously-skip-permissions'
```
