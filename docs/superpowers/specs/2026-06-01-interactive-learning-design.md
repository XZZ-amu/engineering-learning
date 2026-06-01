# 教案交互层设计 Spec

## 概述

在现有 MkDocs Material 站点上增加两个交互能力：可点击选择题 + 学习状态追踪。纯前端实现，零后端。

## 目标

1. "考考你"环节从纯文本变成可交互的选择题（点选项 → 对/错 + 解析）
2. 每章末尾有状态按钮（读完了 / 还没懂），状态存 localStorage
3. 首页有进度总览面板，一眼看到学到哪了

## 选择题交互

### Markdown 格式约定

生成脚本输出的格式（在"考考你"部分）：

```markdown
???+ quiz "题目文本"
    - [ ] A. 选项一
    - [x] B. 正确选项
    - [ ] C. 选项三
    - [ ] D. 选项四
    
    ??? success "解析"
        解析文本，解释为什么 B 是对的。
```

- `[x]` 标记正确答案
- 每题 4 个选项，1 个正确
- 每章 2-3 道选择题

### 交互行为

1. 初始：4 个选项可点击，解析折叠隐藏
2. 用户点选项：
   - 点到正确选项 → 该选项变绿 ✓
   - 点到错误选项 → 该选项变红 ✗，正确选项同时变绿 ✓
3. 解析自动展开
4. 答完锁定，不可改选

### 实现方式

- MkDocs Material 的 `admonition` + `details` 扩展渲染基础 HTML 结构
- 自定义 `quiz.js` 劫持 `.quiz` 容器内的点击事件
- 自定义 `quiz.css` 定义对/错/锁定状态样式

## 状态按钮

### 每章底部

在每个教案 markdown 末尾注入：

```html
<div class="chapter-status" data-chapter="chapter-XX">
  <button class="status-btn done">✓ 读完了</button>
  <button class="status-btn stuck">✗ 还没懂</button>
</div>
```

### 交互行为

- 点"读完了" → 按钮变绿色实心，写 localStorage
- 点"还没懂" → 按钮变橙色实心，写 localStorage
- 可反复切换
- 刷新后保持状态

### localStorage 结构

```json
{
  "el-progress": {
    "chapter-05": "done",
    "chapter-06": "stuck"
  }
}
```

key 为 `el-progress`，value 为各章节状态对象。未读的章节不在对象中。

## 首页进度面板

在 `docs/index.md` 中放一个 `<div id="progress-panel">` 占位，JS 负责渲染：

```
P0 每天都会碰到          ■■□□  2/4
P1 做好产品必须懂        □□□□  0/4  
P2 从能做到做得好        □□□   0/3
```

- ■ 绿色 = done
- ■ 橙色 = stuck  
- □ 灰色 = 未读
- 每个方块可点击跳转到对应章节

## 需要改动的文件

| 文件 | 改动 |
|------|------|
| `docs/javascripts/quiz.js` | 新建，选择题交互逻辑 |
| `docs/javascripts/progress.js` | 新建，状态按钮 + 首页进度面板 |
| `docs/stylesheets/interactive.css` | 新建，交互组件样式 |
| `mkdocs.yml` | 引入自定义 JS/CSS |
| `prompts/chapter-system-prompt.md` | 修改"考考你"部分的格式要求 |
| `scripts/generate-chapters.py` | 每章末尾注入状态按钮 HTML |
| `docs/index.md` | 加进度面板占位 div |

## 不做的事情

- 不做后端
- 不做跨设备同步
- 不做答题正确率统计
- 不做间隔复习提醒
- 不做动画/过渡效果（保持简洁）

## 验收标准

1. 打开任意教案，选择题可点击，点错变红点对变绿，解析自动展开
2. 章末按钮点击后刷新页面状态保持
3. 首页能看到 11 章的进度状态，与 localStorage 一致
