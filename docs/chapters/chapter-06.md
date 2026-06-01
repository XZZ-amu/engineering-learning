# API 设计：让两个系统能说上话

## 1. 一句话本质

**API 是两个系统之间的合同：你按格式提问，我按格式回答，双方不需要知道对方内部怎么运作。**

这句话能推导出一切——为什么要规范 URL、为什么有状态码、为什么要版本管理。所有这些都是在回答同一个问题：怎么让"合同"足够清晰，让任何陌生人拿到文档就能用？

---

## 2. 为什么必须这样

想象没有 API 规范会发生什么。

你在用 Claude Code 调 Stability AI 生图，对方的接口是这样的：

```
/doGenerateImage?img_type=jpg&prompt_text=a cat
/getMyImages?user=123&fetch_all=true
/image_delete?id=456
```

第一个接口用 `img_type`，第二个用 `fetch_all`，第三个叫 `image_delete`。都能用，但你每次调新接口都得重新猜——参数叫什么？是 GET 还是 POST？出错了返回什么？

更严重的问题：你调了三个月，对方悄悄把 `/doGenerateImage` 改成了 `/generate`，你的产品直接崩了。

**没有规范，API 就是一盒随机巧克力——不知道咬开是什么。**

RESTful 就是业界为了解这个问题，大家约定好的一套写法。不是强制标准，是"大家都这么写，新人就能看懂"的协议。

---

## 3. 概念地图

```
API 合同
├── 怎么找到资源（URL 设计）
│   ├── 资源名（名词，不是动词）
│   ├── Path params（指定是哪一个）
│   └── Query params（过滤/排序/分页）
│
├── 想对资源做什么（HTTP 动词）
│   ├── GET    → 查
│   ├── POST   → 创建
│   ├── PUT    → 整体替换
│   └── DELETE → 删除
│
├── 请求里带什么（Request）
│   ├── Headers（身份证 + 说明语言）
│   └── Body（具体内容，POST/PUT 时用）
│
├── 回来得到什么（Response）
│   ├── Status Code（第一秒判断成功/失败）
│   └── Body（实际数据 + 分页信息）
│
└── 合同版本（Version）
    └── 接口变化时，不破坏老用户
```

这些概念不是并列的，是同一件事的不同侧面：URL 说"找谁"，动词说"干什么"，Headers 说"我是谁/用什么格式"，Body 说"具体内容"，Status Code 说"成没成"。

---

## 4. 逐个概念深入

### 资源 + URL 设计：用名词，不用动词

RESTful 的核心直觉：**URL 描述"东西是什么"，动词描述"对它做什么"**。

❌ 差的设计（动词混进 URL）：
```
POST /createImage
GET  /getImages
POST /deleteImage?id=123
```

✅ 好的设计（URL 是名词，动作靠 HTTP 方法区分）：
```
POST   /images          → 创建图片
GET    /images          → 查列表
GET    /images/123      → 查单个
DELETE /images/123      → 删除
```

Stability AI 的真实 API 就是这个结构：`POST /v1/generation/{engine_id}/text-to-image`。`generation` 是资源，`text-to-image` 是子类型，动作是 `POST`（创建一次生成任务）。

**路径里的 `{engine_id}` 是 Path Params**——它指定"是哪一个资源"，这个值是必须的、定位性的。

**URL 末尾的 `?style=anime&limit=20` 是 Query Params**——用来过滤、排序、分页，是可选的修饰条件。

区别口诀：找到谁 → path param；对谁做什么筛选 → query param。

---

### HTTP 动词：语义契约

| 动词 | 含义 | 幂等？ |
|------|------|--------|
| GET | 查，不改数据 | ✓ 多次调结果一样 |
| POST | 创建新资源 | ✗ 每次调创建新的 |
| PUT | 整体更新 | ✓ |
| PATCH | 局部更新 | 通常是 |
| DELETE | 删除 | ✓ |

**幂等**的意义：GET/DELETE 出错了可以放心重试。POST 出错了重试可能创建两条重复记录——这是网络超时时的常见 bug。

---

### 请求结构：Headers + Body

调 Replicate API 时，一个真实请求长这样：

```
POST https://api.replicate.com/v1/predictions

Headers:
  Authorization: Token r8_abc123...   ← 身份证
  Content-Type: application/json      ← 告诉对方 Body 是 JSON

Body:
{
  "version": "stability-ai/sdxl:...",
  "input": { "prompt": "a cat in space" }
}
```

**Headers** 是元信息，讲"我是谁、我们用什么语言沟通"。最常见的两个：
- `Authorization`：认证（API Key 或 Bearer Token，详见认证章节）
- `Content-Type`：Body 的格式，通常是 `application/json`

**Body** 是实际请求内容，只有 POST/PUT/PATCH 才有。GET 请求的"参数"全部放 Query Params 里，Body 是空的。

---

### 响应结构：Status Code 是第一信号

状态码是合同里最重要的一条：**不看 Body，只看状态码，就知道成功还是失败**。

```
2xx → 成功
  200 OK           → 查询/更新成功
  201 Created      → 创建成功（POST 后应该返回这个）
  204 No Content   → 删除成功，没有返回体

4xx → 你的问题
  400 Bad Request  → 参数格式错了
  401 Unauthorized → 没带 Token 或 Token 无效
  403 Forbidden    → 有 Token 但没权限
  404 Not Found    → 资源不存在
  429 Too Many Requests → 超频率限制

5xx → 对方的问题
  500 Internal Server Error → 服务器挂了
  503 Service Unavailable   → 服务暂时不可用
```

4xx 和 5xx 的区别至关重要：4xx 是你的问题，改请求参数；5xx 是对方的问题，等一会重试。Claude Code 调 API 报错时，第一件事就是看这个数字。

**Response Body 的结构**，好的 API 会保持一致：

```json
// 成功
{ "data": { "id": "gen_123", "url": "https://..." }, "meta": {...} }

// 失败
{ "error": { "code": "invalid_prompt", "message": "Prompt 超过最大长度" } }
```

**分页**：查列表时数据可能有几千条，不能一次全返回。标准做法是返回 `cursor` 或 `page` 信息：

```json
{
  "data": [...],
  "pagination": { "next_cursor": "abc", "has_more": true }
}
```

---

### 版本管理：为什么要 /v1/

你发布了 API，有 100 个用户在调。三个月后你要改一个参数名——旧用户立刻全崩。

版本管理解决的问题：**让新旧合同同时有效，用户自己选什么时候升级**。

最常见做法是 URL 里加版本号：`/v1/images`、`/v2/images`。v1 和 v2 可以并行运行一段时间，给用户迁移窗口。

Stability AI 就是这么做的——`/v1/generation/...` 里有明确的 v1。Replicate 的 API 也是 `/v1/predictions`。

版本出现在 URL 里是最直观的，但也有人放在 Header 里（`API-Version: 2024-01`，Stripe 就这么做）。URL 版本更显眼，Header 版本更"RESTful纯粹"，两种都可以——但要选一种，整个产品统一。

---

## 5. 研发在争什么

**争议一：PUT 还是 PATCH？**

PUT 要求传整个对象，PATCH 只传要改的字段。实践中很多团队嫌麻烦，全用 POST——"反正也能用"。代价是失去语义，调用方不知道什么时候会覆盖什么。

**争议二：错误信息给多少细节？**

返回 `"error": "invalid input"` 是安全的，但调用方不知道哪里错了。返回 `"error": "prompt contains banned words: [xxx]"` 是友好的，但可能泄露内部逻辑。安全要求高的场景（金融、医疗）倾向于模糊错误信息，开发者工具倾向于详细。

**争议三：嵌套 URL 要嵌套多深？**

`/users/123/collections/456/images/789` 在语义上很清晰，但太深了之后会变成噩梦——改一层结构，所有深层 URL 都失效。实践中很多团队只嵌套一层：`/collections/456`，然后用 query param 过滤 `?user_id=123`。

**争议四：API 版本放 URL 还是 Header？**

放 URL（`/v2/`）：直观、可以直接粘贴 URL 测试、浏览器可见。  
放 Header（`API-Version: 2`）：URL 保持"干净"，理论上更 RESTful。  
现实中放 URL 更常见，因为对开发者更友好。

---

## 6. 考考你

???+ quiz "你在为 Mindloop 设计「收藏一篇笔记」的 API，应该怎么设计？"
    - [ ] A. `POST /addFavorite?noteId=123`
    - [ ] B. `GET /favorites/add/123`
    - [x] C. `POST /notes/123/favorites`
    - [ ] D. `PUT /notes/favorite?id=123`
    
    ??? success "解析"
        C 是正确的。"收藏"可以理解为在 note 下创建一个 favorite 资源，所以用 POST，路径是 `/notes/{id}/favorites`。
        
        A 的问题是把动词（add）混进了 URL，违反 REST 命名规范。
        
        B 的问题是用 GET 触发了"创建"操作——GET 语义是查询，不应该有副作用，更不应该写数据。
        
        D 的问题是 PUT 语义是"整体替换"，而收藏是创建一个新关系，应该用 POST。

???+ quiz "你调 Replicate API 生成图片，返回了 429 状态码。你应该怎么处理？"
    - [ ] A. 检查 prompt 参数格式，可能传错了
    - [ ] B. 换一个 API Key，当前的可能已经失效
    - [x] C. 等待一段时间后重试，当前请求频率超限了
    - [ ] D. 这是服务器故障，联系 Replicate 客服
    
    ??? success "解析"
        429 是 `Too Many Requests`，属于 4xx——这是"你的问题"，具体是调用太频繁超过了速率限制。
        
        正确处理是等待（通常 response header 里有 `Retry-After` 告诉你等多少秒），然后重试。
        
        A 是 400 的处理方式（参数格式错误）。B 是 401 的处理方式（认证失败）。D 是 5xx 的处理方式（服务器故障）。看到错误第一件事，永远是先看状态码数字。

???+ quiz "Mindloop 要在现有 API 里把「笔记」的 `title` 字段改名为 `name`，且有外部用户在调这个接口。最合理的做法是？"
    - [ ] A. 直接改，通知用户更新代码
    - [ ] B. 在同一个接口里同时支持 `title` 和 `name` 两个字段，永久兼容
    - [x] C. 发布 `/v2/notes`，v2 里用 `name`，v1 保留一段时间后废弃
    - [ ] D. 不能改，API 一旦发布字段名就不能变
    
    ??? success "解析"
        C 是标准做法。版本管理的核心价值就是这个——让破坏性变更（breaking change）在新版本里发生，给旧用户迁移时间，而不是强制所有人同步升级。
        
        A 会直接破坏所有已接入的用户，是最差选择。
        
        B 听起来友好，但长期维护两个字段会造成混乱，而且"永久兼容"意味着技术债永远还不清。
        
        D 是过度保守，API 设计可以演进，版本管理就是为了解决这个问题。

<div class="chapter-status" data-chapter="chapter-02">
  <button class="status-btn done">✓ 读完了</button>
  <button class="status-btn stuck">✗ 还没懂</button>
</div>