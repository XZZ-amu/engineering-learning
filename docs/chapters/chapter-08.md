# P0-4：前端状态与数据流（React）

## 1. 一句话本质

**React 在解决一个问题：UI 是状态的函数——当状态变了，界面自动跟着变，而不是手动操纵每个 DOM 节点。**

这句话推导出一切：

- 有状态，所以需要 State
- 状态从外面传进来，所以需要 Props
- 状态变化要可预测，所以需要单向数据流
- 状态要复用逻辑，所以需要 Hooks
- 状态要跨组件共享，所以需要状态管理方案

---

## 2. 为什么必须这样

假设没有 React，你手动写 JS 操纵 DOM：

```js
// 用户改了模型选择 → 你要手动找到 N 个地方去更新
document.getElementById('model-label').innerText = newModel
document.getElementById('cost-display').innerText = calcCost(newModel)
document.getElementById('submit-btn').disabled = isLoading
// ……每次状态变化，你要记住所有要更新的地方
```

漏掉一个，界面就不一致。随着产品功能增加，这个"记忆负担"以平方速度增长。

React 的回答是：**别管怎么更新，告诉我"现在的状态是什么"，我来决定界面长什么样。**

状态变了，React 重新跑一次渲染函数，界面自动对齐。你只需要管好状态，不需要管 DOM。

---

## 3. 概念地图

```
                    UI = f(state)
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
    状态从哪来        状态怎么变         状态放哪里
        │                │                 │
   Props（外部）    useState / Hooks    本地 vs 全局
   State（内部）    useEffect（副作用）      │
        │                │          ┌──────┴──────┐
        └────────────────┘       Context      Zustand/Redux
                │
        单向数据流（父 → 子）
                │
        组件树（积木拼装）
                │
        ┌───────┴────────┐
    条件渲染           列表渲染
    受控表单           异步状态
```

这些概念不是并列的功能清单，而是同一个问题（管理状态驱动界面）在不同子场景下的解法。

---

## 4. 逐个概念深入

### 组件：UI 的最小独立单位

组件就是一个函数：吃进去 Props，吐出来 JSX。

```jsx
function ModelSelector({ value, onChange }) {
  return <select value={value} onChange={e => onChange(e.target.value)}>...</select>
}
```

**为什么是函数而不是类？** 因为"UI 是状态的函数"这个比喻用函数表达最直接，没有隐藏状态，输入确定输出就确定。

**拆组件的判断标准**：这块逻辑/UI 会在别处复用吗？这块状态跟其他状态是否独立？是就拆。Mindloop 里的 PromptInput、ModelSelector、SizeSlider 都是独立积木，因为它们各自管自己的事。

---

### Props vs State：外部合同 vs 内部记忆

- **Props**：父组件传进来的，组件自己不能改。像函数参数。
- **State**：组件内部管理的，可以改，改了就重渲染。像函数内的局部变量（但会被记住）。

关键判断：**这个数据的"所有权"在哪里？**

Mindloop 参数面板：`currentModel` 的所有权在父组件（因为生成按钮也需要它），所以用 Props 传给 ModelSelector。但 ModelSelector 内部的 `isDropdownOpen` 只有它自己关心，放 State。

---

### 单向数据流：为什么数据只能从上往下

如果允许子组件直接修改父组件的状态，那状态可以从任意方向流动，你就不知道一个状态是被谁改的——调试变成噩梦。

React 的规矩：**数据向下流（Props），事件向上传（回调函数）。**

```
父组件（持有 model 状态）
    │ props: value={model}
    ▼
ModelSelector
    │ 用户选了新模型
    │ props: onChange={setModel}  ← 调用父给的回调
    ▲
父组件更新状态 → 重新渲染子组件
```

看起来绕，但带来了可预测性：状态改变一定是从回调触发的，顺着回调就能找到原因。

---

### Hooks：复用状态逻辑的方式

**useState** — 给组件一块内部记忆

```jsx
const [isLoading, setIsLoading] = useState(false)
// 点击生成 → setIsLoading(true) → 组件重渲染 → 显示进度条
```

**useEffect** — 处理"有副作用的事"（不是渲染本身，而是渲染之后要做的事）

```jsx
useEffect(() => {
  fetchGenerationStatus(taskId)  // 轮询生成进度
}, [taskId])  // taskId 变了才重新执行
```

依赖数组是关键：告诉 React "只在这些值变化时重新跑副作用"。忘写依赖 → 无限循环；多写不必要的依赖 → 性能浪费。

**useCallback / useMemo** — 防止不必要的重新计算

这两个是性能优化手段，不是必须一开始就用。

- `useCallback`：记住一个函数引用，避免每次渲染都创建新函数（传给子组件时有意义）
- `useMemo`：记住一个计算结果，避免每次渲染都重算

经验法则：**先不用，遇到明显性能问题再加。**

---

### 状态管理方案：按规模选工具

```
状态规模        方案          适合场景
────────────────────────────────────────
单个组件内      useState      DropdownOpen, inputValue
跨几个组件      Context       当前主题、用户登录态
全局复杂状态    Zustand       生成任务队列、图库缓存
大型团队项目    Redux         需要严格的状态变更记录
```

**Context 的问题**：Context 一变，所有消费它的组件都重渲染。如果把频繁变化的状态（比如生成进度 0-100%）放 Context，整个树都在抖。

**Zustand 的优势**：只有订阅了某个状态片段的组件才重渲染。Mindloop 用 Zustand 管生成任务队列——进度条更新不会让参数面板重渲染。

**判断标准**：这个状态需要被多少个不相邻的组件访问？只有跨组件树共享时才需要全局状态，别滥用。

---

### 异步状态：loading / error / success 三态模式

生成图片是个异步过程，UI 必须处理三种状态：

```jsx
const [status, setStatus] = useState('idle')  // idle | loading | success | error
const [result, setResult] = useState(null)
const [error, setError] = useState(null)

// 渲染时按状态分支
if (status === 'loading') return <ProgressBar />
if (status === 'error') return <ErrorMessage msg={error} />
if (status === 'success') return <GeneratedImage src={result} />
return <GenerateButton onClick={startGeneration} />
```

**常见错误**：用 `isLoading` 布尔值，忘了处理 error 状态，结果失败了界面还转圈。用枚举字符串强制自己想清楚所有分支。

---

### 受控组件：表单的状态也归 React 管

```jsx
// 受控：React 是 source of truth
<input value={prompt} onChange={e => setPrompt(e.target.value)} />

// 非受控：DOM 是 source of truth（React 不知道当前值）
<input ref={inputRef} />
```

Mindloop 的 prompt 输入框必须是受控组件——因为生成按钮要读当前 prompt 值、字数限制要实时计算。如果用非受控，每次点生成才去 DOM 取值，就丢失了"UI 是状态函数"的好处。

---

## 5. 研发在争什么

**争 1：状态该放多高？**

"把所有状态提到顶层"让数据流清晰，但导致顶层组件肥大，任何改动都要穿越整棵树。"状态就近放置"让组件独立，但共享时要提升（lifting state up），重构成本高。

没有标准答案。一般策略：先就近，真的要共享时再提升或移到全局。

**争 2：用 Context 还是 Zustand？**

Context 是 React 内置，零依赖，够简单。Zustand 有细粒度订阅，性能更好。

小项目用 Context 没问题。但如果你的 Context value 是个频繁更新的对象，Zustand 能救你很多性能调试时间。

**争 3：useEffect 依赖数组怎么写？**

eslint 规则要求写全所有依赖，但有时候"我就是不想在某个值变化时重跑"——这时候研发会争是否该绕过 lint 规则，用 `useRef` 存旧值，还是重新设计数据流。大多数时候需要重新设计，不是绕过规则。

**争 4："把所有状态放一起" vs "按职责拆分"**

```jsx
// 反面教材：一个组件管所有事
function GenerationPanel() {
  const [prompt, setPrompt] = useState('')
  const [model, setModel] = useState('gpt-4')
  const [size, setSize] = useState('1024x1024')
  const [isLoading, setIsLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [galleryItems, setGalleryItems] = useState([])
  const [selectedItem, setSelectedItem] = useState(null)
  // 200行后……没人知道改哪里会影响什么
}
```

按职责拆后，`<ParamPanel>` 管输入参数，`<GenerationStatus>` 管进度，`<Gallery>` 管图库。每个组件只订阅自己关心的状态，改动影响范围可控。

---

## 6. 考考你

???+ quiz "Mindloop 的图片画廊需要展示当前选中图片的大图（任意页面都能触发）。这个"selectedImage"状态应该放在哪里？"
    - [ ] A. 放在 Gallery 组件的 useState 里
    - [ ] B. 放在每个图片缩略图组件的 useState 里
    - [x] C. 放在全局状态（Zustand 或 Context）里
    - [ ] D. 放在最顶层 App 组件的 useState 里，通过 Props 逐层传递
    
    ??? success "解析"
        大图查看是一个跨组件的 UI 状态——任意地方的图片都能触发它，而显示大图的 Modal 组件在组件树的另一个位置。这种"不相邻组件需要共享"的场景正是全局状态的用武之地（C）。
        
        A 错：Gallery 组件不持有 Modal，关闭按钮无法修改这个状态。B 错：每个缩略图各自管自己不合理。D 是技术上可行但实际上最糟糕的——Props 要穿越十几层组件（prop drilling），这正是全局状态要解决的问题。

???+ quiz "以下代码有什么问题？"
    ```jsx
    function ProgressBar({ taskId }) {
      const [progress, setProgress] = useState(0)
      
      useEffect(() => {
        const timer = setInterval(() => {
          fetchProgress(taskId).then(p => setProgress(p))
        }, 500)
        return () => clearInterval(timer)
      }, [])  // 依赖数组为空
    }
    ```
    - [ ] A. 没问题，空依赖数组表示只运行一次，正确
    - [x] B. taskId 变化时不会重新开始轮询，会一直轮询旧任务
    - [ ] C. 应该把 setProgress 也加进依赖数组
    - [ ] D. 应该用 useState 替代 useEffect 来处理轮询
    
    ??? success "解析"
        空依赖数组 `[]` 意味着这个 effect 只在组件挂载时运行一次，永远不会因为 taskId 变化而重新执行。如果用户取消当前任务开始新任务，taskId 变了，但轮询还在盯着旧 taskId——进度条会显示错误数据。
        
        正确写法是把 `taskId` 加进依赖数组 `[taskId]`，这样每次 taskId 变化，旧 interval 会被清除（cleanup 函数），新 interval 重新开始。C 错：`setProgress` 是稳定引用，不需要加。

???+ quiz "用户在参数面板输入 prompt，同时底部状态栏实时显示字数。字数计算是个耗时操作（需要处理 emoji、中文等）。应该怎么优化？"
    - [ ] A. 把字数计算移到 useEffect 里，异步执行
    - [ ] B. 用 useState 单独存 charCount，每次 prompt 变化时手动更新
    - [x] C. 用 useMemo 缓存计算结果，只在 prompt 变化时重新算
    -


<div class="chapter-status" data-chapter="chapter-08">
  <button class="status-btn done">✓ 读完了</button>
  <button class="status-btn stuck">✗ 还没懂</button>
</div>
