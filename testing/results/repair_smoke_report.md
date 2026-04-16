# Repair Smoke Report

## Summary
- total_cases: 8
- repair_success: 8
- repair_failed: 0
- success_rate: 100.0%

## Case Results

### R1
- requirement: 做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_status: PASS
- pre_issues: multiple_profiles; structure_invalid; unknown_component=ecom:Header
- post_issues: none

### R2
- requirement: 做一个轻量商城，包含首页商品列表、商品详情、购物车
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_status: PASS
- pre_issues: multiple_profiles; structure_invalid; unknown_component=ecom:Header,ecom:ProductGrid,ecom:ProductDetail,ecom:CartPanel; unsupported_constructs
- post_issues: none

### R3
- requirement: 做一个产品营销页，包含 Hero、功能亮点、联系我们
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_status: PASS
- pre_issues: alias_component=landing:Testimonials->landing:Testimonial
- post_issues: none

### R4
- requirement: 做一个官网联系页，支持用户提交联系表单
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_status: PASS
- pre_issues: alias_flow=SUBMIT_CONTACT->CONTACT_SUBMIT
- post_issues: none

### R5
- requirement: 做一个 AI Chat App 原型，包含顶部栏、底部 tab、聊天列表、聊天窗口
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_status: PASS
- pre_issues: boundary_exceeded=app_min contains auth or multi-page backend-like constructs
- post_issues: none

### R6
- requirement: 做一个联系人 App 原型，包含顶部栏、底部 tab、联系人列表、个人卡片
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_status: PASS
- pre_issues: boundary_exceeded=app_min expanded into multi-page structure
- post_issues: none

### R7
- requirement: 做一个 AI SaaS 官网，包含首页、功能介绍、团队、FAQ、联系我们
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_status: PASS (no repair needed)
- pre_issues: none
- post_issues: none

### R8
- requirement: 做一个售后入口，包含退款申请、投诉提交、升级处理入口
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_status: PASS (no repair needed)
- pre_issues: none
- post_issues: none
