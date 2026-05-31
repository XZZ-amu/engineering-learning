# API 设计：让两个程序能对话的合约

## 1. 一句话本质

**API 是两个程序之间的合约：你按这个格式问，我按这个格式答，我们永远不需要知道对方的内部实现。**

所有 RESTful 规范、请求结构、错误码、版本管理，都是在把这份"合约"写得更清晰、更不容易产生歧义。

---

## 2. 为什么必须这样

想象没有统一 API 规范的世界：

Replicate 的图片生成接口叫 `/doGenerate`，下次叫 `/run_image`，参数有时叫 `prompt`，有时叫 `text_input`。你调通了今天的接口，明天他们改了实现，你的代码全坏掉。

更糟的是：你不知道失败是因为你的请求格式错了，还是他们服务器挂了，还是你的 API Key 过期了——返回的都是一串看不懂的文字。

**问题本质是：双方没有共同语言。** RESTful 不是某个公司发明的规矩，是行业被这些问题逼出来的共识——当所有人都说同一种语言，接入成本从"读源码"变成"读文档"。

---

## 3. 概念地图

```
API 合约
│
├── 你怎么说（请求 Request）
│   ├── 去哪里找 → URL（资源地址）
│   │   ├── 路径参数 /notes/{id}  → 指定某一个资源
│   │   └── 查询参数 ?page=2      → 过滤/排序/分页
│   ├── 你要干什么 → Method（动词）
│   │   └── GET / POST / PUT / DELETE
│   ├── 你是谁 → Headers（元信息）
│   │   └── Authorization, Content-Type
│   └── 你带了什么 → Body（内容）
│       └── 只有 POST/PUT 才有
│
└── 我怎么回（响应 Response）
    ├── 结果状态 → Status Code（2xx/4xx/5xx）
    ├── 返回内容 → Response Body（JSON）
    └── 特殊场景 → 分页、错误体
```

**版本管理**是在这整个合约上盖一个"时间戳"，让合约可以演进而不破坏已有调用方。

---

## 4. 逐个概念深入

### URL：你去哪里，找什么

RESTful 的核心思想：**URL 是名词（资源地址），Method 是动词（你要对它干什么）。**

```
好的设计：
GET    /images          → 获取图片列表
POST   /images          → 生成一张新图片
GET    /images/abc123   → 获取某张图片
DELETE /images/abc123   → 删除某张图片

差的设计：
GET  /getImages
POST /createImage
GET  /deleteImage?id=abc123   ← 用 GET 做删除，灾难
POST /doImageGeneration       ← 动词混进 URL
```

为什么不能把动词放 URL？因为 URL 代表"一个东西在哪"，不代表"对它做什么"——就像餐厅菜单只写"宫保鸡丁"，不写"请帮我做宫保鸡丁"。

**路径参数 vs 查询参数**——这两个经常混淆：

- `/images/abc123`：路径参数，指定的是**具体某一个**资源，ID 是资源身份的一部分
- `/images?style=anime&page=2`：查询参数，是对资源列表的**过滤和修饰**，不影响"去哪里"

判断用哪个：如果去掉这个参数，请求就指向不同的资源→路径参数。如果去掉只是结果变多/变少→查询参数。

---

### Method：你要干什么

```
GET    → 读，不改变任何数据（安全的，可以随便调）
POST   → 创建新资源（每次调都会产生新东西）
PUT    → 替换整个资源（把收藏的 note 全量更新）
PATCH  → 局部修改（只改 note 的标题）
DELETE → 删除
```

研发最常争的：**POST 还是 PUT/PATCH**？

简单判断：这次操作是"产生一个新东西"还是"修改一个已有的东西"？生成图片→POST（每次都产生新图）；修改图片的收藏状态→PATCH（修改已有资源的某个字段）。

---

### Headers：你是谁，你说的是什么语言

Headers 是请求的"元信息"，不是业务数据本身。最重要的两个：

```
Authorization: Bearer sk-abc123   → 你是谁（认证）
Content-Type: application/json    → 你带来的 body 是什么格式
```

**为什么认证放 Header 不放 URL？** 因为 URL 会出现在日志、浏览器历史、分享链接里。把 API Key 放 URL 等于把密码印在 T 恤上。

---

### Response：我怎么回你

**Status Code 是最重要的响应信息。** 在看 body 之前，先看状态码。

```
2xx → 成功
  200 OK           → 普通成功
  201 Created      → 创建成功（POST 之后）
  204 No Content   → 成功但没有返回体（DELETE 之后）

4xx → 你的问题
  400 Bad Request  → 你的请求格式/参数有问题
  401 Unauthorized → 没认证（没带 token 或 token 错）
  403 Forbidden    → 认证了但没权限
  404 Not Found    → 资源不存在
  429 Too Many Requests → 超频率限制（调 AI API 常见）

5xx → 我的问题
  500 Internal Server Error → 服务器炸了
  503 Service Unavailable   → 服务暂时不可用
```

**4xx 和 5xx 的区别很关键**：4xx 是你需要修改请求再试，5xx 是你等一会儿重试就行。

**错误 body 的设计**——好的错误体应该告诉你"怎么修":

```json
好的错误体：
{
  "error": {
    "code": "INVALID_PROMPT",
    "message": "Prompt cannot be empty",
    "param": "prompt"
  }
}

差的错误体：
{ "success": false }   ← 完全不知道哪里错了
```

**分页**——当列表可能有几千条时，不能一次全返回：

```
请求：GET /images?page=2&per_page=20
响应：
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 347,
    "has_next": true
  }
}
```

---

### 版本管理：合约可以升级，但不能突然变卦

你发布了 `/images` 接口，一百个用户在用。现在你要改返回格式。如果直接改，所有用户的代码都坏掉——这叫 **Breaking Change**（破坏性变更）。

解法：**版本号放 URL**。

```
/v1/images    ← 老版本继续跑，不动
/v2/images    ← 新版本，新格式
```

什么时候必须升版本？当你**删除了字段、改了字段名、改了字段类型**时。新增字段通常不需要——调用方会忽略它们不认识的字段。

Stability AI、Replicate 都这么做，这不是谨慎，是基本职业素养。

---

### 认证：先验明正身（预告）

现在先知道两个：

- **API Key**：一串固定字符串，放 Header。简单，适合服务器对服务器调用。`Authorization: Bearer sk-xxxxx`
- **Bearer Token**：用户登录后拿到的临时令牌。适合"用户调自己的数据"场景。

Replicate 用 API Key，你调 Mindloop 自己的后端会用 Bearer Token。认证章节会展开讲。

---

## 5. 研发在争什么

**争一：错误码用 HTTP Status Code 还是自定义业务码？**

有人说：HTTP 状态码够用了，400 就是客户端错；有人说：业务太复杂，需要 `code: 10023` 这种细粒度的业务错误码。

代价：纯 HTTP 状态码简洁，但难以区分"参数格式错"和"参数值不合法"；业务码灵活，但客户端要维护一张错误码映射表，文档要一直跟着更新。

**实际结论**：两者结合——HTTP 状态码告诉你"谁的问题"，body 里的 code 告诉你"具体什么问题"。

---

**争二：分页用 page/per_page 还是 cursor-based？**

`page=2` 方式直观，但数据在翻页时新增了记录，你第 2 页可能会看到第 1 页的内容（漏或重）。

Cursor-based（游标分页）：`after=abc123`，意思是"给我 abc123 这条之后的数据"，不受新增数据影响。代价是不能跳页（不能直接跳到第 50 页）。

**判断标准**：数据是静态/不频繁更新的（历史订单）→ page/per_page 够用；数据实时变化（信息流、生成记录）→ cursor-based 更稳。

---

**争三：资源嵌套 URL 要深还是浅？**

```
深：/users/123/collections/456/images/789
浅：/images/789
```

深 URL 语义清晰，但 URL 太长，而且改了用户模型就要改 URL。浅 URL 简洁，但需要在 body 里传关联关系。

**实际结论**：超过两级嵌套就该考虑拆平——`/collections/456/images` 可以，`/users/123/collections/456/images/789` 就过了。

---

## 6. 考考你

**Q1：用你自己的话，一句话解释 API 规范解决的核心问题是什么？**

（提示：不是"让接口更好看"，而是关于"谁的责任是什么"）

---

**Q2：你在给 Mindloop 设计"AI 生成笔记摘要"功能的 API，研发给了你这个方案：**

```
POST /generateSummary
Body: { "note_id": "abc123" }
返回: { "result": "ok", "data": "这是摘要内容" }
```

**你觉得哪里可以改？为什么？**

（提示：URL 的问题、返回的问题各想一个）

---

**Q3：你在接入 Replicate API 生成图片，请求发出去，收到了 `403` 状态码。你的第一反应是重试还是检查代码？为什么？如果是 `503` 呢？**

---

**Q4：Mindloop 上线了 `/v1/images` 接口，有用户在用。现在要新增一个 `style` 字段到返回体。需要升版本到 v2 吗？如果是把 `created_at` 从时间戳改成 ISO 字符串格式呢？**