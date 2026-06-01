# P0-4：前端状态与数据流（React）

## 1. 一句话本质

**React 在解决一个根本问题：UI 是状态的函数——当状态变了，界面自动跟着变，而不是你手动去改每一个 DOM 节点。**

用公式写就是：`UI = f(state)`。理解这句话，后面所有概念都是它的推论。

---

## 2. 为什么必须这样

假设 Mindloop 有一个"生成进度"界面：用户点击生成，出现 loading 圈，进度到 50% 显示进度条，完成后显示图片，失败了显示报错。

如果没有"状态驱动 UI"的思路，你要这么写：
```js
// 手动操控 DOM：找到元素、改它、再找下一个、再改……
document.getElementById('spinner').style.display = 'block'
document.getElementById('progress').innerText = '50%'
document.getElementById('result').style.display = 'none'
```

四个状态切换，你要手动追踪每一个元素在每一个时机的状态。如果你漏了一个 `display = 'none'`，就 bug 了。而且状态越多，组合爆炸——10 个 UI 元素、5 种状态，你根本管不住。

React 的解法是：**你只管状态，界面由状态推导出来。** 状态对了，界面自然对。

---

## 3. 概念地图

```
UI = f(state) ← 根本逻辑
│
├── 状态在哪里？
│   ├── 组件内部 → State（useState）
│   └── 从父组件传入 → Props
│
├── 状态怎么流动？
│   └── 单向数据流：父 → 子（Props 传下去，事件冒上来）
│
├── 状态变了，UI 怎么更新？
│   └── 重新渲染（render）→ React 自动 diff，只改有变化的部分
│
├── 状态以外的"副作用"怎么处理？
│   └── Hooks（useEffect / useCallback / useMemo）
│
└── 状态需要很多组件共享怎么办？
    ├── 轻量 → Context
    ├── 中量 → Zustand
    └── 重量 → Redux
```

这张图说明：所有概念不是并列的，它们是从同一个根问题"状态变了 UI 怎么跟着变"长出来的不同分支。

---

## 4. 逐个概念深入

### 组件：UI 的最小单位

把 Mindloop 的参数面板想象成乐高：`<PromptInput>`、`<ModelSelector>`、`<SizeSlider>` 各自独立，拼在一起组成 `<GeneratePanel>`。

**为什么拆？** 不拆的话，一个组件几百行，改一个 slider 要在几百行里找到它，而且改坏了会影响旁边的东西。拆开之后，每个组件只关心自己的状态和 UI，改 slider 就只进 `<SizeSlider>`。

**拆的标准**：一个组件做一件事。能独立复用、独立测试，就拆对了。

---

### Props vs State：外面给的 vs 自己管的

| | Props | State |
|---|---|---|
| 谁控制 | 父组件传入 | 组件自己 |
| 能改吗 | 不能（只读） | 能（用 setState）|
| 类比 | 函数的参数 | 函数内部的变量 |

Mindloop 参数面板里：`modelName="GPT-4"` 是 Props（父组件选好了传进来），`isExpanded` 是 State（面板自己知道自己有没有展开）。

**判断方法**：这个数据需要被外部控制吗？需要 → Props。只有组件自己关心 → State。

---

### 单向数据流：为什么数据只能从上往下

React 规定：数据只能从父组件通过 Props 流向子组件，子组件想改父组件的数据，只能通过"父组件传下来的回调函数"往上通知。

```
父组件（持有 state）
  ↓ props 传下去
子组件（只读 props）
  ↑ 调用 onXxx() 往上通知
```

**为什么不能双向流？** 如果子组件能直接改父组件的 state，一个 state 被多处改，你根本不知道是谁改的，bug 追不到。单向流意味着：状态的唯一来源（source of truth）在上面，谁改了它，一定是通过显式的函数调用，可追溯。

---

### 渲染：状态变了发生什么

`useState` 的 `setState` 触发重新渲染，React 重新执行组件函数，生成新的 UI 描述，再跟上一次对比（diff），只把有差异的地方更新到真实 DOM。

你不需要理解 diff 算法的细节。你只需要知道：**状态变 → 组件函数重跑 → React 帮你更新界面**。这是 React 的核心契约。

---

### Hooks：状态之外的问题

`useState` 管状态，但有些事不是"状态"，是"副作用"——比如请求接口、订阅事件、操作 DOM。这些不能放在渲染逻辑里，否则每次重新渲染都会触发。Hooks 是 React 提供的"副作用接入口"。

**useEffect**：在渲染完成后执行某件事。
```js
useEffect(() => {
  fetch('/api/generate') // 渲染完再请求，不阻塞界面
}, [taskId]) // taskId 变了才重新执行
```
第二个参数是依赖数组——"只有这些值变了，才重跑这个副作用"。空数组 `[]` = 只跑一次（组件挂载时）。

**useMemo / useCallback**：性能优化工具，不是必须一开始就用。
- `useMemo`：缓存一个计算结果，避免每次渲染重算
- `useCallback`：缓存一个函数引用，避免每次渲染生成新函数

**什么时候用它们？** 先不用，遇到明显性能问题再加。过早优化是噪音。

---

### 状态该放哪里：本地 vs 全局

这是最核心的判断题。

**判断逻辑**：
```
这个状态只有一个组件需要？→ 放在本地（useState）
两三个相邻组件需要？→ 提升到共同父组件（state lifting）
很多不相关的组件都需要？→ 全局状态管理
```

Mindloop 的例子：
- 参数面板的"是否展开"→ 本地 State（只有面板自己关心）
- 当前生成任务的进度 → 全局（参数面板、进度条、画廊都要知道）
- 用户登录信息 → 全局（几乎所有地方都用到）

**全局方案怎么选：**

| 方案 | 适合场景 | 代价 |
|---|---|---|
| Context | 低频变化的全局数据（主题、用户信息） | 性能差，Context 变了所有订阅者重渲染 |
| Zustand | 中等复杂度、高频变化的状态 | 几乎没有，轻量好用 |
| Redux | 超复杂、需要时间旅行调试、大团队协作 | 模板代码多，上手成本高 |

**Mindloop 用什么？** Zustand。生成任务状态、图片库状态、用户设置——这些跨组件共享、会频繁变化，Zustand 刚好合适。Context 放主题颜色、语言这种不常变的配置。

---

### 条件渲染和列表渲染

这两个直接从"UI = f(state)"推导出来，不是新概念。

```jsx
// 条件渲染：状态不同，UI 不同
{status === 'loading' && <Spinner />}
{status === 'success' && <ImageResult src={result} />}
{status === 'error' && <ErrorMessage msg={error} />}

// 列表渲染：数据是数组，UI 也是数组
{images.map(img => <ImageCard key={img.id} src={img.url} />)}
```

`key` 不能漏：React 靠 key 判断列表里哪个元素是新的、哪个是旧的。用 `index` 当 key 会在重排序时出 bug，用数据的唯一 ID。

---

### 异步数据：loading/error/success 三态模式

这是 Mindloop 里最常见的场景。生成图片、加载画廊，全是异步操作。

把异步状态抽象成三个字段：

```js
const [status, setStatus] = useState('idle') // idle | loading | success | error
const [data, setData] = useState(null)
const [error, setError] = useState(null)
```

UI 根据 `status` 渲染不同内容。这是固定模式，遇到异步操作就这么写，不要即兴发挥。

**受控组件**：表单的值受 State 控制。`<input value={prompt} onChange={e => setPrompt(e.target.value)} />`。输入框的值 = state，用户输入 = 触发 setState。这样你随时能拿到最新值，还能做校验。

---

## 5. 研发在争什么

**争论一：状态应该提升到哪一层？**

提太高：每次状态变化，整棵子树重新渲染，性能差。提太低：需要共享时传不上去，prop drilling（props 一层一层往下传）烦死人。

没有标准答案，看变化频率 × 共享范围。

**争论二：要不要用 Redux？**

主张用 Redux 的：规范、可预测、调试工具强。反对的：样板代码太多，Zustand 三行能搞定的事 Redux 要写二十行。现在大多数新项目选 Zustand，除非团队 > 20 人、状态非常复杂。

**争论三：useEffect 的依赖数组要不要写全？**

React 官方要求写全（ESLint 规则会警告）。但有时候写全了会导致无限循环——因为每次渲染产生新的函数引用，被依赖，触发重跑，再渲染……这时候需要 `useCallback` 稳定引用。这是 hooks 最难的地方，不是概念问题，是实践中会踩的坑。

---

## 6. 考考你

**题一：用你自己的话说，React 的核心逻辑是什么？**（不许用"框架"、"库"这种词，说底层逻辑）

---

**题二：Mindloop 的画廊页面，研发在讨论"图片列表的数据放哪里"。方案 A：放在 `<Gallery>` 组件的本地 State。方案 B：放在 Zustand 全局 store。**

你问了几个问题后，发现：这份图片数据只有画廊页面用，其他页面不需要；但画廊里有三个子组件（缩略图列表、放大预览、下载按钮）都需要读它。

你会建议哪个方案？为什么？

---

**题三：研发写了下面这段伪代码，你觉得有什么风险？**

```js
// 用户每次输入 prompt，就立刻请求 API 检查语法
useEffect(() => {
  fetch('/api/check-syntax', { body: prompt })
}, [prompt])
```

用你对 useEffect 的理解，说出这个设计的问题。

---

**题四：你接手了一个老组件，发现里面有 20 个 useState，管着参数面板的所有状态（prompt、model、width、height、style、seed……），加上 loading/error/result。研发说"状态太多，组件太重"。**

你能说出这是哪个问题的症状，以及一个可能的解法方向吗？（不需要写代码，说思路）

<div class="chapter-status" data-chapter="chapter-08">
  <button class="status-btn done">✓ 读完了</button>
  <button class="status-btn stuck">✗ 还没懂</button>
</div>
