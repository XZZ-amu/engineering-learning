# 参考项目

AI 辅助学习领域的开源项目调研，按相关度排序。

---

## Tier 1：跟我们直接相关

### DeepTutor（24K+ 星）
https://github.com/HKUDS/DeepTutor

Agent 原生的个性化教学系统。上传文档后生成互动学习环境：对话、测验、协同写作、可视化。有"Book Engine"能把文档编译成活教材。

**核心设计**：三层记忆系统（会话级/主题级/长期）追踪学习者状态。TutorBot 能后台自主运行。

**我们能学什么**：学习者状态追踪的分层思路。"活教材"编译器概念跟我们 Issue→教案 的管道类似。

---

### Mr. Ranedeer AI Tutor（29K+ 星，已停更）
https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor

整个产品就是一段 GPT-4 prompt。用户配置深度等级（1-10）、学习风格、沟通方式、推理框架，GPT-4 按配置教任何主题。

**核心设计**：个性化 = 结构化配置（深度 + 风格 + 语气），不需要复杂代码。

**我们能学什么**：生成 prompt 里加"深度"参数。我们的 CLAUDE.md 已经在做类似的事（定义用户画像），可以更形式化。

---

### AI-Shifu（290 星）
https://github.com/ai-shifu/ai-shifu

"Write Once, Teach Personally"——创作者写一次教学意图，AI 展开成个性化学习体验。按学习者画像调整解释方式、交互探测、评估。

**核心设计**：分离"教学意图"和"交付形式"。高层框架快速组装课程，AI 展开成具体内容。

**我们能学什么**：验证了我们 Issue→教案 管道的方向。他们的"快速课程组装"跟我们几乎一模一样。

---

## Tier 2：值得参考的设计

### Tutor-GPT / Bloom（900+ 星）
https://github.com/plastic-labs/tutor-gpt

基于 Theory-of-Mind 的 AI 导师。动态推理学习者需求，自动更新 prompt 来最佳服务。命名来自 Bloom 的 Two Sigma Problem（1对1 辅导提升 2 个标准差）。

**我们能学什么**：自适应 prompt——系统随学习者理解程度实时调整教学策略。我们的"已掌握"列表是静态版本，可以进化。

---

### Human Skill Tree（546 星）
https://github.com/24kchengYe/human-skill-tree

33 个即插即用的 AI Agent 技能，把 AI 变成有教学结构的学习伙伴。基于认知科学研究（间隔重复、主动回忆）。

**核心发现**：研究表明 AI 教学在有教学结构时效果提升 48-127%。没有结构的 AI 对话式学习效果很差。

**我们能学什么**：科学验证了我们的结构化方法（类比+案例+考考你）是对的。技能树可视化可以启发我们的学习路线图。

---

### Skill-Anything（267 星）
https://github.com/SYuan03/Skill-Anything

一条命令把任何来源（PDF/视频/网页/GitHub 仓库）变成 12 段式互动学习包：摘要、笔记、术语表、速查表、测验、闪卡、练习、学习路径。

**我们能学什么**：标准化输出结构。我们目前 6 段式（本质→反面→地图→深入→争论→考考你），可以考虑加闪卡或速查表。

---

### ChatTutor（1.1K+ 星）
https://github.com/HugeCatLab/ChatTutor

有电子白板的 AI 导师。不只文字聊天，AI 能调用可视化工具（画图、思维导图、数学画布、代码执行）。

**我们能学什么**：纯文本教学对技术主题不够。架构图、时序图、流程图能显著提升理解。我们的 ASCII 图是轻量版。

---

### PageLM（1.6K+ 星）
https://github.com/CaviraOSS/PageLM

开源 NotebookLM 替代品。把学习材料变成测验、闪卡、Cornell 笔记、AI 播客、互动对话。一份文档 → 10+ 种学习形态。

**我们能学什么**：输出格式多样化。同一内容的不同形态（读、答、听、辩）能提升记忆留存。

---

### CodeABC（72 星）
https://github.com/he-yufeng/CodeABC

"读代码不学代码"——给非程序员用的 AI 代码阅读器。丢一个项目文件夹，生成纯白话的项目手册。hover 任何一行代码都有生活化解释。

**我们能学什么**：产品哲学完全对齐我们的目标（让不懂代码的人理解技术）。hover 标注 UX 可以启发我们教案里代码段的解释方式。

---

## Tier 3：了解即可

| 项目 | 星数 | 一句话 |
|------|------|--------|
| [GenMentor](https://github.com/GeminiLight/gen-mentor) | 72 | 五 Agent 协作的目标导向学习框架（WWW 2025 Oral） |
| [EduChat](https://github.com/ECNU-ICALK/EduChat) | 934 | 华东师大的教育专用 LLM，"先思考再教学" |
| [OATutor](https://github.com/CAHLR/OATutor) | 209 | 用贝叶斯知识追踪估算掌握度（CHI'23） |
| [AnkiAIUtils](https://github.com/thiswillbeyourgithub/AnkiAIUtils) | 856 | AI 给 Anki 卡片加解释/助记/插图 |
| [LearnHouse](https://github.com/learnhouse/learnhouse) | 1.6K | 集成 AI 的开源 LMS |

---

## 关键结论

1. **我们的 Issue→教案 管道方向正确**（AI-Shifu 验证）
2. **有教学结构的 AI 学习效果是无结构的 2-3 倍**（Human Skill Tree 引用的研究）
3. **最大的进化空间**：学习者状态追踪（从静态"已掌握"列表 → 动态追踪理解程度）
4. **次要进化**：输出形式多样化（选择题交互、闪卡、图解）
