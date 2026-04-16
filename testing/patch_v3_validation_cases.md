# Patch v3 Validation Cases

## Case 1

- requirement: 做一个售后页面，包含联系客服入口。
- expected stable hit:
  - `after_sales:Entry`
  - `after_sales:Support`

## Case 2

- requirement: 做一个售后页面，用户可以申请退款并联系客服。
- expected stable hit:
  - `after_sales:Refund`
  - `after_sales:Support`
  - `REFUND_FLOW`

## Case 3

- requirement: 做一个 app 原型，包含登录、接口调用、用户认证和聊天。
- expected boundary behavior:
  - suppress login/auth/api expansion
  - keep single-page `app_min`
  - prefer `app:TopBar`, `app:BottomTab`, `app:ChatWindow`

## Case 4

- requirement: 做一个简单的待办 app，支持新增任务和搜索联系人。
- expected stable hit:
  - `app:TopBar`
  - `app:BottomTab`
  - `app:List`
  - `app:Composer`
  - `app:SearchBar`

## Case 5

- requirement: 做一个 AI SaaS 官网，包含首页、功能介绍、客户评价。
- expected stable hit:
  - `landing:Header`
  - `landing:Hero`
  - `landing:FeatureGrid`
  - `landing:Testimonial`
  - `landing:CTA`
  - `landing:Footer`

## Case 6

- requirement: 做一个招聘官网，包含首页、职位展示、联系我们。
- expected stable hit:
  - `landing:Jobs`
  - `landing:Contact`
  - `CONTACT_SUBMIT`

## Case 7

- requirement: 做一个个人介绍网站，包含首页、项目作品、联系方式。
- expected stable hit:
  - `landing:Portfolio`
  - `landing:Contact`
  - `CONTACT_SUBMIT`
