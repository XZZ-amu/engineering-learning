---
created: 2026-06-01
tags:
  - note
---
TL;DR：「开发基础知识」拆成 7 个模块：开发环境、项目初始化与脚手架、包管理器、仓库结构、文件类型、Lint / Format / Type Check、软件工程最佳实践，不教大家写某个具体功能，而是帮助大家建立“现代软件项目是怎么组织、运行、协作和保持质量的”基本地图。

# 软件开发基础知识地图

## 1. 开发环境

### 1.1 开发环境是什么

* 开发环境是开发者用来编写、运行、调试、测试项目的一整套工具和配置
* 它通常包括：
    * 操作系统：macOS、Windows、Linux
    * 代码编辑器：VS Code、WebStorm、Neovim 等
    * 运行时：Node.js、Bun、Python、Java、Go 等
    * 包管理器：npm、pnpm、yarn、bun 等
    * 版本管理工具：Git
    * 命令行环境：Terminal、PowerShell、iTerm 2、Warp 等
    * 浏览器与调试工具：Chrome DevTools、Firefox DevTools
    * 项目依赖：框架、库、插件、构建工具
    * 环境变量：`.env`、`.env.local` 等

### 1.2 为什么开发环境很重要

* 确保项目能在本地稳定运行
* 降低“我这里能跑，你那里不行”的概率
* 让团队成员使用一致的工具版本
* 方便 onboarding，新人能快速启动项目
* 为 CI/CD、测试、部署提供一致基础

### 1.3 本地开发环境常见组成

| 类型 | 示例 | 作用 |
|---|---|---|
| 编辑器 | VS Code / WebStorm / Neovim | 编写代码 |
| Runtime | Node.js / Bun / Python | 执行代码 |
| Package Manager | npm / pnpm / yarn / bun | 安装和管理依赖 |
| Version Control | Git | 代码版本管理 |
| Shell | zsh / bash / PowerShell | 执行命令 |
| Browser DevTools | Chrome DevTools | 调试前端页面 |
| Database | SQLite / PostgreSQL / MySQL | 本地数据存储 |
| Container | Docker | 隔离和复现环境 |

### 1.4 版本管理：Runtime 版本

需要讲：

* 为什么 Node.js 版本要统一
* LTS 版本是什么
* Node 版本不一致可能导致：
    * 依赖安装失败
    * 构建失败
    * API 不兼容
    * lockfile 变化
    * CI 能过但本地失败，或反过来

常见工具：

* `nvm`
* `fnm`
* `volta`
* `asdf`
* `mise`

项目中常见文件：

```txt
.nvmrc
.node-version
.tool-versions
package.json
```

示例：

```txt
20.11.1
```

建议讲法：

* 项目不应该只靠口头约定 Node 版本
* 应该把 Runtime 版本写入仓库
* README 里应该说明如何安装和切换版本

### 1.5 编辑器配置

可以讲：

* 为什么编辑器也属于开发环境
* 统一编辑器配置能减少格式差异
* 常见配置：
    * 缩进：2 spaces / 4 spaces
    * 换行符：LF / CRLF
    * 文件编码：UTF-8
    * 行尾空格处理
    * 自动格式化
    * 推荐插件

常见文件：

```txt
.editorconfig
.vscode/settings.json
.vscode/extensions.json
```

示例 `.editorconfig`：

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true
```

### 1.6 环境变量

需要讲：

* 环境变量是什么
* 为什么不能把密钥写进代码
* `.env` 文件的作用
* 本地环境、测试环境、生产环境的区别

常见文件：

```txt
.env
.env.local
.env.development
.env.production
.env.example
```

建议重点：

* `.env` 通常不提交
* `.env.example` 应该提交，用于说明需要哪些变量
* 不要把 token、password、secret key 提交进 Git
* 前端框架一般要求特定前缀：
    * Vite：`VITE_`
    * Next.js：`NEXT_PUBLIC_`

示例：

```env
VITE_API_BASE_URL=https://api.example.com
VITE_APP_ENV=development
```

### 1.7 命令行基础

建议讲：

* 什么是 Terminal / Shell
* 常见基础命令：
    * `pwd`：查看当前目录
    * `ls`：列出文件
    * `cd`：切换目录
    * `mkdir`：创建目录
    * `touch`：创建文件
    * `cat`：查看文件内容
    * `rm`：删除文件
    * `cp`：复制
    * `mv`：移动或重命名
* 路径概念：
    * 绝对路径
    * 相对路径
    * 当前目录 `.`
    * 上级目录 `..`
    * 用户目录 `~`

### 1.8 浏览器调试工具

前端开发建议补充：

* Elements：查看 DOM 和 CSS
* Console：查看日志和执行 JS
* Network：查看请求、响应、资源加载
* Sources：断点调试
* Application：查看 localStorage、sessionStorage、cookies、cache
* Performance：性能分析
* Lighthouse：性能和可访问性检查

### 1.9 开发环境常见问题

* Node 版本不一致
* 包管理器混用
* lockfile 冲突
* 本地环境变量缺失
* 系统路径配置错误
* 依赖安装后仍然报错，需要清理缓存或重新安装
* Windows 和 macOS 换行符差异
* 文件大小写在不同系统上的表现不一致
* 端口被占用
* 本地和 CI 环境不一致

---

## 2. 项目初始化与脚手架

### 2.1 项目初始化是什么

* 项目初始化是从空目录创建一个可运行项目的过程。
* 它通常包括：
    * 创建目录结构
    * 创建配置文件
    * 创建入口文件
    * 初始化 `package.json`
    * 安装基础依赖
    * 添加启动、构建、检查脚本
    * 配置 Git 忽略规则
    * 添加 README
* 项目初始化的目标是让项目从一开始就具备可运行、可维护、可协作的基础。

### 2.2 脚手架是什么

* 脚手架是自动生成项目初始结构和基础代码的工具。
* 它不会直接完成业务功能，而是帮你搭好项目骨架。
* 常见生成内容：
    * 目录结构
    * 示例源码
    * `package.json`
    * `tsconfig.json`
    * 构建配置
    * Lint 配置
    * `.gitignore`
    * README
    * 基础依赖和 scripts

### 2.3 常见脚手架命令

#### 前端常见：

```bash
pnpm create vite
npm create vite
npx create-next-app
pnpm create vue
pnpm create astro
npx create-expo-app
```

#### 这些命令通常会让你选择：

* 项目名
* 框架
* 语言
* 是否使用 TypeScript
* 是否使用 ESLint
* 是否使用 Tailwind CSS
* 是否初始化 Git
* 是否安装依赖

### 2.4 脚手架通常生成什么

| 类型 | 示例 | 作用 |
|---|---|---|
| 源码目录 | `src/` | 存放项目源码 |
| 静态资源 | `public/` | 存放原样拷贝的资源 |
| 依赖声明 | `package.json` | 记录依赖和脚本 |
| TypeScript 配置 | `tsconfig.json` | 控制类型检查和编译选项 |
| 构建配置 | `vite.config.ts` | 控制开发服务器和打包行为 |
| Lint 配置 | `eslint.config.js` | 代码质量检查 |
| Git 忽略规则 | `.gitignore` | 避免提交无用文件 |
| 文档 | `README.md` | 说明如何启动和使用项目 |
| 示例代码 | `App.tsx`, `main.tsx` | 提供可运行入口 |

---

### 2.5 脚手架、模板、boilerplate、starter 的区别

| 概念 | 含义 | 例子 |
|---|---|---|
| Scaffold | 脚手架工具或生成过程 | `pnpm create vite` |
| Template | 模板文件集合 | React + TypeScript 模板 |
| Boilerplate | 样板代码 | 可复制的初始项目代码 |
| Starter | 启动模板 | GitHub 上的 `react-starter` |

---

### 2.6 使用脚手架创建项目的流程

```txt
准备 Node.js 和包管理器
  ↓
运行脚手架命令
  ↓
选择模板和选项
  ↓
生成项目目录
  ↓
安装依赖
  ↓
启动开发服务器
  ↓
打开浏览器验证项目能跑
```

#### 示例：

```bash
pnpm create vite my-app
cd my-app
pnpm install
pnpm dev
```

---

### 2.7 团队内部脚手架的价值

* 团队内部脚手架可以统一：
  * 技术栈
  * 目录结构
  * 包管理器
  * TypeScript 配置
  * Lint / Format 配置
  * Git hooks
  * CI 配置
  * 请求封装
  * UI 组件库
  * 权限方案
  * 埋点方案
  * 发布流程

---

### 2.8 脚手架的风险和误区

* 误区 1：脚手架生成的代码都不用理解。
    * 实际上生成的配置迟早需要维护。
* 误区 2：脚手架越全越好。
    * 过度内置功能会违反 YAGNI。
* 误区 3：用了脚手架项目就一定规范。
    * 后续维护和团队执行同样重要。
* 误区 4：所有项目都应该用同一个脚手架。
    * 不同项目规模和目标不同，模板也应该不同。
* 误区 5：脚手架可以永远不升级。
    * 工具链会变化，脚手架也需要维护。

---

## 3. 包管理器

### 3.1 包管理器是什么

* 包管理器用于安装、更新、删除、锁定项目依赖
* 前端常见包管理器：
    * npm
    * yarn
    * pnpm ⭐
    * bun ⭐  (已经被 Anthropic 收购)
  * npm / pnpm / yarn / bun 对比
    | 工具 | 特点 | 适合场景 |
    |---|---|---|
    | npm | Node 官方默认，生态兼容好 | 通用项目 |
    | pnpm | 节省磁盘、安装快、依赖隔离更严格 | monorepo、大型前端项目 |
    | yarn | 历史悠久，workspace 支持成熟 | 老项目或已有团队规范 |
    | bun | Runtime + package manager + test runner | 新项目、追求速度的实验项目 |

### 3.2 为什么需要包管理器

* 项目依赖越来越多，不可能手动下载和维护
* 依赖之间还会有依赖，也就是 transitive dependencies
* 包管理器可以帮助解决：
    * 下载依赖
    * 解析版本
    * 生成 lockfile
    * 执行 scripts
    * 管理 workspace
    * 发布 package

### 3.3 `package.json`

#### 前端项目的核心配置文件

#### 常见字段：

| 字段 | 作用 |
|---|---|
| `name` | 包名或项目名 |
| `version` | 当前版本 |
| `private` | 是否禁止发布 |
| `scripts` | 项目命令 |
| `dependencies` | 生产依赖 |
| `devDependencies` | 开发依赖 |
| `peerDependencies` | 宿主依赖 |
| `engines` | Node / 包管理器版本约束 |
| `type` | 模块类型，常见为 `module` |
| `exports` | package 对外导出 |
| `workspaces` | monorepo workspace 配置 |

#### 示例：

```json
{
  "name": "my-app",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^6.0.0"
  }
}
```

### 3.4 依赖类型

| 类型 | 示例 | 说明 |
|---|---|---|
| `dependencies` | `react`, `axios` | 应用运行时需要 |
| `devDependencies` | `typescript`, `vite`, `eslint` | 只在开发、构建、测试时需要 |
| `peerDependencies` | `react` in component library | 要求使用方提供 |
| `optionalDependencies` | 平台相关包 | 安装失败也不一定阻断 |
| `bundledDependencies` | 少见 | 发布时一起打包 |

### 3.5 版本号和 SemVer

#### SemVer 是语义化版本

格式：

```txt
MAJOR.MINOR.PATCH
```

例如：

```txt
2.4.1
```

#### 含义：

* `MAJOR`：破坏性更新
* `MINOR`：新增功能，理论上向后兼容
* `PATCH`：问题修复，理论上向后兼容

#### 常见版本范围：

| 写法 | 含义 |
|---|---|
| `1.2.3` | 精确版本 |
| `^1.2.3` | 允许升级 minor 和 patch |
| `~1.2.3` | 允许升级 patch |
| `>=1.2.3` | 大于等于 |
| `latest` | 最新版本，不建议在项目中依赖 |
| `*` | 任意版本，不建议使用 |

### 3.6 lockfile

#### 常见 lockfile：

| 包管理器 | Lockfile |
|---|---|
| npm | `package-lock.json` |
| yarn | `yarn.lock` |
| pnpm | `pnpm-lock.yaml` |
| bun | `bun.lock` 或 `bun.lockb` |

#### 注意：

* 团队应该统一包管理器
* lockfile 记录实际安装的依赖版本
* 应用项目应该提交 lockfile
* 不同包管理器的 lockfile 不要混用
* lockfile 冲突不要盲目删除，最好理解后解决

### 3.7 `node_modules`

* `node_modules` 是依赖安装目录
* 不应该提交到 Git
* 体积通常很大
* 不同包管理器的 `node_modules` 结构不完全一样
* 依赖安装异常时常见处理：
    * 删除 `node_modules`
    * 删除 lockfile 需要谨慎
    * 清理缓存
    * 重新安装

### 3.8 常用命令

#### 以 `pnpm` 为例：

```bash
pnpm install
pnpm add react
pnpm add -D typescript
pnpm remove lodash
pnpm update
pnpm run dev
pnpm run build
pnpm run lint
pnpm exec tsc --noEmit
```

#### `npm` 对应：

```bash
npm install
npm install react
npm install -D typescript
npm uninstall lodash
npm run dev
```

### 3.9 Scripts

#### `package.json` 里的 `scripts` 是项目命令入口

#### 常见脚本：

```json
{
  "scripts": {
    "dev": "vite",
    "start": "node server.js",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "format": "prettier . --write",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "clean": "rimraf dist"
  }
}
```

需要讲：

* 用 scripts 封装项目常用操作
* CI 通常也会直接调用 scripts

### 3.10 Workspaces 和 Monorepo

* workspace 允许一个仓库管理多个 package
  * monorepo 是多个项目或 package 放在同一个仓库中
    * 常见结构：
        * `apps/web`
        * `apps/admin`
        * `packages/ui`
        * `packages/utils`
        * `packages/config`
    * 企业项目常用 monorepo
    * 共享组件、工具函数、配置更方便
    * 也会带来构建、依赖边界、版本管理复杂度

---

## 4. 仓库结构

### 4.1 仓库是什么

* 仓库是项目代码、配置、文档、历史记录的集合
* 通常由 Git 管理
* 一个好的仓库结构应该让人快速知道：
    * 入口在哪里
    * 源码在哪里
    * 配置在哪里
    * 构建产物在哪里
    * 文档在哪里
    * 测试在哪里
    * 如何启动项目

### 4.2 常见前端项目结构

```txt
my-app/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── routes/
│   ├── services/
│   ├── stores/
│   ├── styles/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── tests/
├── docs/
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── vite.config.ts
├── eslint.config.js
├── README.md
└── .gitignore
```

### 4.3 常见目录说明

| 目录 | 作用 |
|---|---|
| `src/` | 项目源码 |
| `public/` | 静态资源，通常原样拷贝 |
| `assets/` | 图片、字体、图标等资源 |
| `components/` | 可复用 UI 组件 |
| `pages/` | 页面级组件 |
| `routes/` | 路由配置 |
| `hooks/` | React hooks |
| `services/` | API 请求和外部服务封装 |
| `stores/` | 状态管理 |
| `utils/` | 通用工具函数 |
| `styles/` | 全局样式、主题变量 |
| `tests/` | 测试文件 |
| `docs/` | 项目文档 |
| `scripts/` | 自动化脚本 |
| `config/` | 共享配置或工具配置 |

### 4.4 根目录配置文件

| 文件 | 作用 |
|---|---|
| `package.json` | 项目信息、依赖、脚本 |
| `README.md` | 项目说明和启动指南 |
| `.gitignore` | Git 忽略规则 |
| `.env.example` | 环境变量示例 |
| `tsconfig.json` | TypeScript 配置 |
| `vite.config.ts` | Vite 构建配置 |
| `eslint.config.js` | ESLint 配置 |
| `prettier.config.js` | Prettier 配置 |
| `.editorconfig` | 编辑器统一配置 |
| `commitlint.config.js` | Commit message 规范 |
| `Dockerfile` | 容器构建说明 |
| `.github/workflows/*` | GitHub Actions CI 配置 |

### 4.5 入口文件

* 前端项目常见入口：
    * `index.html`
    * `src/main.tsx`
    * `src/App.tsx`
* Node 服务端项目常见入口：
    * `src/index.ts`
    * `src/server.ts`
    * `main` 字段

### 4.6 构建产物

#### 常见构建产物：

```txt
dist/
build/
.next/
out/
coverage/
```

#### 注意：

* 构建产物通常不提交
* 它们可以由源码重新生成
* CI/CD 通常会在流水线里重新构建

### 4.7 文档

#### 常见文档：

* `README.md`
* `CHANGELOG.md`
* `CONTRIBUTING.md`
* `docs/architecture.md`
* `docs/development.md`
* `docs/deployment.md`
* `docs/adr/*`

#### 说明：

* README 面向“第一次接触项目的人”
* 架构文档面向“理解系统设计的人”
* ADR 记录重要技术决策，不是流水账

### 4.8 仓库结构设计原则

* 高内聚：相关文件放在一起
* 低耦合：模块之间依赖清晰
* 入口清晰：新人能快速找到启动点
* 配置集中：公共配置不要散落
* 边界明确：组件、业务、服务、工具函数分层
* 可演进：结构能随着项目变大继续扩展

### 4.9 按类型组织 vs 按功能组织

#### 按类型组织：
* ```txt
  src/
  ├── components/
  ├── hooks/
  ├── services/
  └── utils/
  ```

* 优点：
  * 初学者容易理解
  * 小项目清晰

* 缺点：
  * 大项目中一个功能会分散在很多目录里

#### 按功能组织：

* ```txt
  src/
  ├── features/
  │   ├── auth/
  │   │   ├── components/
  │   │   ├── api.ts
  │   │   ├── hooks.ts
  │   │   └── types.ts
  │   └── chat/
  │       ├── components/
  │       ├── api.ts
  │       ├── hooks.ts
  │       └── types.ts
  └── shared/
  ```

* 优点：
  * 业务边界更清楚
  * 更适合中大型项目

* 缺点：
  * 对模块边界设计能力要求更高

### 4.10 Monorepo 结构

#### 常见 Monorepo 结构：
```txt
repo/
├── apps/
│   ├── web/
│   └── admin/
├── packages/
│   ├── ui/
│   ├── config/
│   ├── utils/
│   └── eslint-config/
├── docs/
├── package.json
├── pnpm-workspace.yaml
└── turbo.json
```

#### 注意：

* `apps/` 通常是可运行应用
* `packages/` 通常是可复用库
* shared package 不应该反向依赖 app
* 工程复杂度更高，需要更严格的边界管理

---

## 5. 文件类型

### 5.1 为什么要讲文件类型

* 不同文件扩展名代表不同用途
* 编辑器、构建工具、运行时会根据扩展名处理文件
* 文件类型决定：
    * 能不能被执行
    * 如何被编译
    * 如何被打包
    * 是否能被浏览器直接识别
    * 是否需要 loader 或 plugin

### 5.2 常见代码文件

| 文件类型 | 用途 |
|---|---|
| `.js` | JavaScript 文件 |
| `.jsx` | 包含 JSX 的 JavaScript |
| `.ts` | TypeScript 文件 |
| `.tsx` | 包含 JSX 的 TypeScript |
| `.mjs` | ES Module JavaScript |
| `.cjs` | CommonJS JavaScript |
| `.json` | JSON 数据或配置 |
| `.html` | HTML 页面 |
| `.css` | CSS 样式 |
| `.scss` / `.sass` | Sass 预处理样式 |
| `.less` | Less 预处理样式 |
| `.vue` | Vue 单文件组件 |
| `.svelte` | Svelte 组件 |

### 5.3 `.js` / `.jsx` / `.ts` / `.tsx`

#### 重点：

* `.js`：普通 JavaScript
* `.jsx`：JavaScript + JSX
* `.ts`：TypeScript，不包含 JSX
* `.tsx`：TypeScript + JSX

#### 常见误区：

* React component 如果写 JSX，TypeScript 项目里通常用 `.tsx`
* 纯工具函数不需要 `.tsx`，用 `.ts` 即可
* 不要所有文件都无脑用 `.tsx`

### 5.4 `.mjs` / `.cjs`

#### 需要讲：

* Node.js 生态里有两种模块系统：
    * ESM：`import` / `export`
    * CommonJS：`require` / `module.exports`
* `.mjs` 通常表示 ESM
* `.cjs` 通常表示 CommonJS
* `package.json` 里的 `"type": "module"` 会影响 `.js` 的解析方式

#### 示例：

```js
// ESM
import path from "node:path"

export function hello() {}
```

```js
// CommonJS
const path = require("node:path")

module.exports = { hello }
```

### 5.5 配置文件

常见配置文件：

| 文件 | 作用 |
|---|---|
| `tsconfig.json` | TypeScript 编译配置 |
| `vite.config.ts` | Vite 配置 |
| `eslint.config.js` | ESLint 配置 |
| `prettier.config.js` | Prettier 配置 |
| `tailwind.config.ts` | Tailwind CSS 配置 |
| `postcss.config.js` | PostCSS 配置 |
| `vitest.config.ts` | Vitest 配置 |
| `playwright.config.ts` | Playwright 配置 |

### 5.6 数据和文档文件

| 文件类型 | 用途 |
|---|---|
| `.json` | 配置或结构化数据 |
| `.yaml` / `.yml` | 配置文件，常用于 CI/CD |
| `.md` | Markdown 文档 |
| `.mdx` | Markdown + JSX |
| `.csv` | 表格数据 |
| `.xml` | 标记数据，部分老系统常见 |

### 5.7 图片、字体、媒体文件

| 类型 | 示例 | 说明 |
|---|---|---|
| 位图 | `.png`, `.jpg`, `.webp`, `.avif` | 照片、复杂图像 |
| 矢量图 | `.svg` | 图标、插画、可缩放图形 |
| 字体 | `.woff`, `.woff2`, `.ttf`, `.otf` | Web 字体 |
| 视频 | `.mp4`, `.webm` | 视频资源 |
| 音频 | `.mp3`, `.wav`, `.ogg` | 音频资源 |

重点：

* 图标优先考虑 SVG
* Web 图片优先考虑 WebP / AVIF，但要注意兼容性
* 字体文件会影响加载性能
* 大媒体文件不宜直接放进普通代码仓库

### 5.8 隐藏文件和 dotfiles

以 `.` 开头的文件通常是配置文件

示例：

```txt
.gitignore
.env
.eslintrc
.prettierrc
.editorconfig
.npmrc
```

需要讲：

* macOS / Linux 中点开头文件默认隐藏
* 很多工具依赖 dotfiles
* 不要因为看不见就以为不存在

### 5.9 Git 相关文件

| 文件 / 目录 | 作用 |
|---|---|
| `.git/` | Git 仓库内部数据，不要手动改 |
| `.gitignore` | 忽略不需要提交的文件 |
| `.gitattributes` | 统一换行符、语言统计、diff 规则 |
| `.gitmodules` | Git submodule 配置 |

### 5.10 应该提交和不该提交的文件

#### 通常应该提交：

* 源码
* 配置
* 文档
* lockfile
* 测试
* 静态小资源
* `.env.example`

#### 通常不该提交：

* `node_modules/`
* `dist/`
* `.env`
* 日志文件
* 本地 IDE 缓存
* 系统文件，如 `.DS_Store`
* coverage 结果
* 临时文件

---

## 6. Lint、Format、Type Check

### 6.1 Lint 是什么

#### Lint 是静态分析代码的过程它不运行代码，而是检查代码中潜在的问题

* 常见工具：
    * ESLint
    * Stylelint
    * Biome
    * Oxlint

#### Lint 可以发现：

* 未使用变量
* 错误的 import
* 可能的 bug
* 不符合团队规范的写法
* React hooks 规则问题
* 可访问性问题
* 复杂度过高
* 不安全写法

### 6.2 Format 是什么

#### Format 是自动格式化代码关注代码长什么样，而不是逻辑对不对
* 常见工具：
    * Prettier
    * Biome
    * dprint

#### Format 负责：

* 缩进
* 换行
* 空格
* 引号
* 分号
* 尾逗号
* 最大行宽

### 6.3 Type Check 是什么

#### Type Check 是类型检查
* TypeScript 项目中通常使用：

#### 示例命令：
```bash
tsc --noEmit
```

它负责检查：

* 类型是否匹配
* 函数参数是否正确
* 返回值是否符合声明
* 对象字段是否存在
* 泛型使用是否正确
* `null` / `undefined` 风险

### 6.4 Lint / Format / Type Check 的区别

| 类型 | 关注点 | 工具示例 | 是否修改代码 |
|---|---|---|---|
| Format | 代码样式 | Prettier / Biome | 可以自动修改 |
| Lint | 代码质量和规则 | ESLint / Biome / Oxlint | 部分可自动修复 |
| Type Check | 类型正确性 | TypeScript | 通常不修改 |
| Test | 行为正确性 | Vitest / Jest / Playwright | 不修改 |

### 6.5 ESLint

#### ESLint 是 JavaScript / TypeScript 生态中最常用的 Lint 工具

* 规则系统
* plugin
* shareable config
* parser
* flat config
* auto fix

#### 常见插件：

* `@typescript-eslint`
* `eslint-plugin-react`
* `eslint-plugin-react-hooks`
* `eslint-plugin-jsx-a11y`
* `eslint-plugin-import`
* `eslint-plugin-unicorn`

#### 示例命令：

```bash
pnpm eslint .
pnpm eslint . --fix
```

### 6.6 Prettier

#### Prettier 是最常用的代码格式化工具

* Prettier 解决格式争论
* 不建议把大量格式规则交给人工 code review
* 保存时自动格式化
* CI 里检查格式

#### 示例命令：

```bash
pnpm prettier . --check
pnpm prettier . --write
```

### 6.7 Biome

#### Biome 是一个新兴的 Lint / Format 工具，特点：

* 同时支持 format 和 lint
* 速度快
* 配置相对集中
* 适合新项目尝试

### 6.8 Git Hooks

#### 常见工具：

* Husky
* lint-staged
* lefthook
* simple-git-hooks

#### 常见用途：

* commit 前自动格式化
* commit 前跑 lint
* commit message 检查
* 避免明显错误进入仓库

#### 示例流程：

```txt
git commit
  ↓
pre-commit hook
  ↓
lint-staged
  ↓
format / lint staged files
  ↓
commit success or fail
```

### 6.9 CI 中的检查

#### CI 是 Continuous Integration（持续集成）的缩写

#### 核心观点：

* 本地 hook 是第一道防线
* CI 是最终质量门禁
* 重要规则必须在 CI 中执行

### 6.10 常见误区

* 误区 1：Lint 只是格式化
    * 实际上格式化是 Format，Lint 更关注潜在问题和规范
* 误区 2：TypeScript 通过就说明代码没 bug
    * 类型正确不等于业务正确
* 误区 3：只要本地能跑就可以合并
    * 团队项目需要 CI 检查
* 误区 4：规则越多越好
    * 太多无意义规则会增加维护成本
* 误区 5：所有 Lint warning 都可以忽略
    * warning 太多会导致团队对问题麻木

---

## 7. 软件工程最佳实践概念

### 7.1 KISS

#### KISS：Keep It Simple, Stupid

#### 核心思想：

* 能简单就不要复杂
* 不要为了“显得高级”引入不必要抽象
* 优先选择团队能理解、能维护的方案

#### 例子：

```ts
// 复杂写法
const getUserDisplayName = (user?: User) =>
  pipe(
    user,
    option.fromNullable,
    option.map((u) => u.profile),
    option.map((p) => p.nickname),
    option.getOrElse(() => "Anonymous"),
  )
```

```ts
// 简单写法
function getUserDisplayName(user?: User) {
  return user?.profile?.nickname ?? "Anonymous"
}
```

#### 总结

* 简单不是粗糙
* 简单是减少不必要的认知成本
* 简单代码更容易 debug、review、测试和交接

### 7.2 DRY

#### DRY：Don’t Repeat Yourself

#### 核心思想：

* 避免同一知识在多个地方重复维护
* 重复代码会导致修改时漏改、不一致

#### 注意：

* DRY 不是“看到两段代码相似就立刻抽象”
* 过早抽象会让代码变难懂
* 要区分：
    * 代码长得像
    * 业务规则真的相同

### 7.3 YAGNI

#### YAGNI：You Aren’t Gonna Need It

#### 核心思想：

* 不要为了未来可能需要的功能提前设计复杂系统
* 先解决真实需求

#### 例子：

* 当前只有 1 个登录方式，不一定要先设计完整 plugin auth system
* 当前只有 1 个主题，不一定要先做复杂 theme marketplace
* 当前只有 1 种导出格式，不一定要先抽象 export engine

### 7.4 SOLID

| 原则 | 含义 | 简单解释 |
|---|---|---|
| S | Single Responsibility Principle | 一个模块只承担清晰职责 |
| O | Open / Closed Principle | 对扩展开放，对修改关闭 |
| L | Liskov Substitution Principle | 子类型能替换父类型 |
| I | Interface Segregation Principle | 不要强迫使用者依赖不需要的接口 |
| D | Dependency Inversion Principle | 依赖抽象，不依赖具体实现 |

### 7.5 单一职责

#### 核心思想：

* 一个函数、组件、模块应该有清晰边界
* 不要让一个文件同时负责：
    * UI 展示
    * 数据请求
    * 数据转换
    * 权限判断
    * 埋点
    * 错误处理
    * 缓存策略

#### 例子

* bad smell
  ```txt
  UserPage.tsx
    既负责请求用户数据
    又负责处理权限
    又负责渲染 UI
    又负责提交表单
    又负责埋点
    又负责格式化数据
  ```
* 可以拆成：
  ```txt
  UserPage.tsx
  useUserQuery.ts
  UserProfileCard.tsx
  UserPermissionPanel.tsx
  formatUser.ts
  trackUserEvent.ts
  ```

### 7.6 关注点分离

#### 常见分离：

* UI 和业务逻辑分离
* 数据请求和展示组件分离
* 配置和代码分离
* domain logic 和 framework glue 分离
* server state 和 client state 分离

#### 例子：

```txt
组件负责展示
Hook 负责状态和副作用
Service 负责请求
Utils 负责纯函数转换
```

---

## 8. 知识点清单

### 开发环境

* 操作系统差异：macOS / Windows / Linux
* Terminal / Shell 基础
* PATH 是什么
* Node.js / Bun / Python 等 Runtime
* Runtime 版本管理
* 编辑器和插件
* `.editorconfig`
* 环境变量
* `.env` 和 `.env.example`
* Chrome DevTools
* 本地端口和服务
* Docker / Dev Container 简介
* 常见环境问题排查

### 项目初始化与脚手架

* 项目初始化是什么
* 从空目录到可运行项目的过程
* 脚手架是什么
* 常见脚手架命令：`create vite` / `create-next-app` / `create vue` / `create astro` / `create-expo-app`
* 脚手架生成内容：目录结构、`package.json`、`tsconfig.json`、构建配置、Lint 配置、`.gitignore`、README
* Scaffold / Template / Boilerplate / Starter 区别
* 使用脚手架创建项目的流程
* 团队内部脚手架的价值
* 脚手架的风险和误区

### 包管理器

* 包管理器的作用
* npm / yarn / pnpm / bun 区别
* `package.json`
* dependencies / devDependencies / peerDependencies
* SemVer
* `^` / `~`
* lockfile
* `node_modules`
* scripts
* workspace
* monorepo
* 依赖安全和依赖治理

### 仓库结构

* Git repository
* 根目录文件
* `src/`
* `public/`
* `assets/`
* `components/`
* `pages/`
* `routes/`
* `services/`
* `utils/`
* `hooks/`
* `stores/`
* `tests/`
* `docs/`
* `scripts/`
* `config/`
* 构建产物目录
* 单仓库 vs monorepo
* 按类型组织 vs 按功能组织

### 文件类型

* `.js`
* `.jsx`
* `.ts`
* `.tsx`
* `.mjs`
* `.cjs`
* `.json`
* `.yaml`
* `.md`
* `.mdx`
* `.html`
* `.css`
* `.scss`
* `.svg`
* `.png`
* `.webp`
* `.env`
* `.gitignore`
* `.editorconfig`
* 配置文件
* 构建产物文件

### Lint / Format / Type Check

* Lint 是什么
* Format 是什么
* Type Check 是什么
* ESLint
* Prettier
* Biome
* Stylelint
* `tsc --noEmit`
* Auto fix
* 保存时格式化
* pre-commit hook
* lint-staged
* CI 检查
* warning 和 error 策略

### 软件工程最佳实践

* KISS
* DRY
* YAGNI
* SOLID
* Single Responsibility
* Separation of Concerns
* Composition over Inheritance
* Encapsulation
* High Cohesion / Low Coupling
* Abstraction
* Premature Optimization
* Convention over Configuration
* Principle of Least Surprise
* Fail Fast
* Progressive Enhancement
* Code Review
* Testing
* Documentation
* Debugging
* Security
* Dependency Hygiene