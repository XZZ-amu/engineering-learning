# 数据库基础：SQL vs NoSQL、表结构、查询、索引

## 1. 一句话本质

**数据库在解决的根本问题：让数据以结构化的方式存活，并且能被精准、高效地找回来。**

所有概念——表、字段、主键、外键、索引、JOIN——都是围绕这两件事展开的：**存得有结构**，**取得有效率**。

---

## 2. 为什么必须这样

用 Excel 存数据不行吗？

短期完全可以。但用 Excel 管理 Mindloop 的用户数据，会出现这些问题：

- **并发崩溃**：两个用户同时保存，谁的算数？Excel 文件没有"同时写"的概念。
- **查找变全扫描**：找"收藏了模板 A 的用户"，只能从头翻每一行。10 万行就是 10 万次比较。
- **关系无法维护**：用户 ID 写在作品表里，用户被删了，作品表里那个 ID 指向谁？没人管。
- **类型无约束**：一列应该存日期，有人存了字符串"昨天"，Excel 照单全收。

数据库解决的就是这些：**并发控制、关系约束、高效查找、类型安全**。

---

## 3. 概念地图

```
根问题：存得有结构 + 取得有效率
          │
    ┌─────┴──────┐
  存结构        取效率
    │               │
  ┌─┴────────┐    ┌─┴────────┐
表结构设计   SQL   索引       查询
  │        vs      │         │
字段/类型  NoSQL   目录机制  SELECT
主键/外键          B-Tree   JOIN
关联关系            │       GROUP BY
一对多/多对多    迁移的代价  ORDER BY
```

SQL 和 NoSQL 是两种不同的"存结构"哲学：
- **SQL（关系型）**：强结构，先定表格再存数据，数据之间有关系约束
- **NoSQL（文档型）**：弱结构，每条记录自己决定有哪些字段，像 JSON 对象一堆放在一起

---

## 4. 逐个概念深入

### 表结构：定义数据的"形状"

Mindloop 的核心表：

```
users          works           generations
─────────      ─────────       ─────────────
id (PK)        id (PK)         id (PK)
email          user_id (FK)    work_id (FK)
created_at     title           prompt
               style_tag       model_version
               created_at      created_at
```

**主键（PK）**：每行的唯一身份证。用自增整数或 UUID，不用"用户名"做主键——用户名可能改，身份证不能改。

**外键（FK）**：`works.user_id` 指向 `users.id`，这是在告诉数据库"这两张表有关系，请帮我维护它"。如果对应的 user 被删了，数据库可以拒绝操作或级联删除，而不是留下一个悬空的 ID。

**关联关系**：
- **一对多**：一个用户有多个作品——`works` 表里存 `user_id` 就够了
- **多对多**：一个用户可以收藏多个作品，一个作品可以被多个用户收藏——需要一张中间表

```
favorites（中间表）
─────────────────
user_id (FK → users)
work_id (FK → works)
created_at
```

中间表是多对多关系的标准解法。不要试图在 `users` 表里存一列"收藏列表"——这是 Excel 思维，不是数据库思维。

---

### SQL vs NoSQL：不是好坏，是权衡

| | SQL（如 PostgreSQL） | NoSQL（如 MongoDB） |
|---|---|---|
| 结构 | 先建表再存数据，每行字段一致 | 每条文档字段可以不同 |
| 关系 | 外键约束，JOIN 查询 | 通常靠应用层维护 |
| 适合场景 | 有明确关系的业务数据 | 结构多变的内容、日志、配置 |
| Mindloop 里的例子 | 用户、作品、收藏 | 生成参数的历史记录（每次参数结构可能不同） |

**Mindloop 用 SQL 的理由**：用户和作品之间有明确的所有权关系，收藏有多对多关系，这些关系需要被数据库约束——而不是靠代码自律。

**什么时候考虑 NoSQL**：生成记录里的 `prompt_params` 字段，每个模型版本的参数结构都不一样，用 JSON 文档存更灵活。很多项目两者混用。

---

### 查询：精确描述"我要什么"

```sql
-- 查某用户最近 50 张图
SELECT * FROM works
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 50;

-- 按风格标签筛选
SELECT * FROM works
WHERE style_tag = 'cyberpunk'
ORDER BY created_at DESC;

-- 热门排行榜（收藏数最多的作品）
SELECT works.id, works.title, COUNT(favorites.work_id) AS fav_count
FROM works
JOIN favorites ON works.id = favorites.work_id
GROUP BY works.id, works.title
ORDER BY fav_count DESC
LIMIT 20;
```

**JOIN 的本质**：把两张表按关联条件拼在一起查。`works JOIN favorites ON works.id = favorites.work_id` 就是：把作品表和收藏表里 ID 对得上的行拼成一行。

**GROUP BY 的本质**：先按某列分组，再对每组做聚合（COUNT、SUM、AVG）。热门排行榜就是：按作品 ID 分组，数每组里有多少收藏记录。

这几个查询会"慢"吗？看数据量和有没有索引。

---

### 索引：书的目录，不是书的内容

不加索引，查询是什么体验？

```
WHERE user_id = 123
→ 数据库从第 1 行翻到最后一行，逐行比较
→ 100 万行就比较 100 万次
→ 这叫"全表扫描"
```

加了索引之后：

```
WHERE user_id = 123
→ 数据库查索引（B-Tree 结构，像二分查找）
→ 直接定位到 user_id=123 的所有行
→ 100 万行里找到 50 条，可能只需要几十次比较
```

索引是把某列的值单独提取出来，做成一个排好序的数据结构（B-Tree）。代价是：**每次写入都要同时更新索引**，所以索引不是越多越好。

**Mindloop 该加哪些索引？**

```sql
-- 高频查询：某用户的作品
CREATE INDEX idx_works_user_id ON works(user_id);

-- 高频查询：按风格标签筛选
CREATE INDEX idx_works_style_tag ON works(style_tag);

-- 热门排行榜：收藏表关联
CREATE INDEX idx_favorites_work_id ON favorites(work_id);
```

**判断要不要加索引的简单原则**：这列经常出现在 `WHERE`、`JOIN ON`、`ORDER BY` 里吗？是的话加。这张表主要是被写入（日志表），很少被查询？别加太多。

---

### 数据迁移（Migration）：为什么改表结构要小心

代码改了可以回滚。表结构改了，里面的数据怎么办？

场景：Mindloop 上线后，`works` 表没有 `style_tag` 字段，现在要加。

**问题一**：已有的 100 万条作品记录，`style_tag` 该是什么值？空的？还是有默认值？

**问题二**：加字段期间，有用户正在保存作品。表结构在变，代码在写，可能冲突。

**问题三**：如果这次迁移写错了（比如把字段类型改成了不兼容的类型），数据会损坏，而且可能无法简单回滚。

这就是为什么研发不会随手 `ALTER TABLE`，而是写 Migration 脚本——版本化的、可追踪的表结构变更，就像 Git 管理代码变更一样。

---

## 5. 研发在争什么

**争论 1：用 UUID 还是自增 ID 做主键？**

- 自增 ID（1, 2, 3...）：简单、查询快、但暴露了数据量（用户 ID 是 100，说明注册用户不多）
- UUID（`a3f2b1c4-...`）：随机、不暴露、但字符串比较比整数比较慢
- 没有标准答案，大多数项目用自增 ID，有安全需求的用 UUID

**争论 2：把数据"平铺"还是"嵌套"？**

生成记录里的参数，到底用多列存，还是用一列 JSON 存？

```sql
-- 平铺（SQL 风格）
prompt TEXT, seed INT, cfg_scale FLOAT, steps INT

-- 嵌套（JSON 风格）
params JSONB  -- {"prompt": "...", "seed": 42, "cfg_scale": 7.5}
```

平铺可以建索引，可以精确查询；JSON 灵活，字段可以随时加减。研发通常的做法：固定会被查询的字段单独建列，其余灵活参数放 JSON。

**争论 3：索引加多少？**

写多读少的场景（比如日志）：少加索引，不然每次写入都要更新索引，写得越来越慢。读多写少的场景（比如作品列表）：大方加索引，查询优先。

---

## 6. 考考你

???+ quiz "Mindloop 要上线「按风格标签 + 时间排序」的筛选功能。研发说查询很慢，你来判断原因并建议加什么索引。"
    - [ ] A. 给 `works.title` 加索引，因为用户经常搜标题
    - [ ] B. 给 `works.user_id` 加索引，因为每次查询都要过滤用户
    - [x] C. 给 `works.style_tag` 和 `works.created_at` 加索引，因为查询的 WHERE 和 ORDER BY 用的是这两列
    - [ ] D. 不需要加索引，优化 SQL 语句就够了

    ??? success "解析"
        索引要加在查询实际使用的列上。这个查询是 `WHERE style_tag = 'cyberpunk' ORDER BY created_at DESC`，所以需要在这两列上建索引。`title` 和 `user_id` 在这个查询里没有出现，加了也不会提速。"优化 SQL 语句"对全表扫描的改善有限，索引才是根本解法。

???+ quiz "Mindloop 新增「用户可以关注其他用户」功能。应该怎么设计表结构？"
    - [ ] A. 在 `users` 表里加一列 `following_ids`，存被关注的用户 ID 列表
    - [ ] B. 在 `users` 表里加两列：`followers_count` 和 `following_count`，存数字就够了
    - [x] C. 新建一张 `follows` 中间表，包含 `follower_id` 和 `following_id` 两个外键字段
    - [ ] D. 复制一份 `users` 表，专门存关注关系

    ??? success "解析"
        用户关注用户是典型的多对多关系（A 可以关注多个人，B 可以被多个人关注）。多对多的标准做法是新建中间表，每一行代表一条"A 关注了 B"的关系记录。选项 A 是把列表塞进一列，无法被数据库有效查询和约束；选项 B 只存了数字，无法查"A 关注了哪些人"；选项 D 是冗余设计，会导致数据不一致。

???+ quiz "上线 3 个月后，Mindloop 要给 `generations` 表新增一列 `model_version`。研发说要写 Migration 脚本，而不是直接改表。为什么？"
    - [ ] A. 因为数据库不允许直接修改已有表的结构
    - [ ] B. 因为 Migration 脚本能让新字段自动填上合理的默认值，而直接改表做不到
    - [ ] C. 因为团队规定必须写脚本，是流程要求
    - [x] D. 因为表结构变更会影响已有数据和线上运行的代码，Migration 脚本让这个变更可版本化、可追踪、可在出错时回滚，就像 Git 管理代码一样

    ??? success "解析"
        Migration 的本质是把表结构的变更也纳入版本控制。已有 100 万条记录，新字段的默认值是什么？新代码和旧代码在迁移期间同时运行怎么兼容？出错了怎么回退？这些都需要 Migration 脚本来管理。它不是技术限制，也不只是流程规定，而是被"数据改错了很难恢复"这个现实问题逼出来的解法。

---

<div class="chapter-status" data-chapter="chapter-04">
  <button class="status-btn done">✓ 读完了</button>
  <button class="status-btn stuck">✗ 还没懂</button>
</div>