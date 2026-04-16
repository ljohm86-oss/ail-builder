# Token Patch v2 Draft

## Closed In Patch v1
- `landing:Testimonial`
- `after_sales:Support`
- `app:Composer`

这些 token 已经在系统中生效，不再应当作为新的 gap 重复建议。

## Patch v2 Candidates

### 1. `app:SearchBar`
- Profile: `app_min`
- Priority: 1
- Why: 联系人类原型开始出现“搜索联系人”需求，当前缺少直接表达。
- Evidence: `P3`
- Minimal patch:
  - generator 允许生成 `app:SearchBar`
  - diagnostic 视为合法 token
  - repair 可在 `app_min + 搜索联系人` 时补齐
  - compile 只渲染一个最小输入栏

### 2. `landing:Jobs`
- Profile: `landing`
- Priority: 2
- Why: 招聘官网需求里出现“职位展示”，当前 landing 没有对应区块。
- Evidence: `L5`
- Minimal patch:
  - generator 允许生成 `landing:Jobs`
  - diagnostic 视为合法 token
  - repair 可在 `landing + 职位展示` 时补齐
  - compile 渲染简单职位卡片列表

### 3. `landing:Portfolio`
- Profile: `landing`
- Priority: 3
- Why: 个人站 / 工作室官网出现“项目作品”，当前 landing 缺少作品展示区块。
- Evidence: `L6`
- Minimal patch:
  - generator 允许生成 `landing:Portfolio`
  - diagnostic 视为合法 token
  - repair 可在 `landing + 项目作品` 时补齐
  - compile 渲染简单项目卡片网格

## Deferred Alias / Normalization Items
这些更像别名归一化，不建议和 Patch v2 的新 token 混在一起：
- `landing:Testimonials` -> `landing:Testimonial`
- `ecom:Search` -> `ecom:SearchResultGrid`
- `SUBMIT_CONTACT` -> `CONTACT_SUBMIT`
- `ADD_CART` -> `ADD_TO_CART`
- `SUPPORT_ESCALATE` -> `COMPLAINT_DEESCALATE`

## Recommended Order
1. `app:SearchBar`
2. `landing:Jobs`
3. `landing:Portfolio`
