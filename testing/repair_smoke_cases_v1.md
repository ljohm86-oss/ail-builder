# Repair Smoke Cases v1

## Case R1
Case ID: R1
Requirement:
做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们
Broken AIL:
```ail
#PROFILE[landing]
#PROFILE[ecom_min]
@PAGE[Home,/]
#UI[landing:Header]
#UI[landing:Hero]
#UI[ecom:Header]
```
Expected Repair Goal:
保留 landing，删除 ecom_min，并补齐功能介绍、FAQ、联系我们
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes

## Case R2
Case ID: R2
Requirement:
做一个轻量商城，包含首页商品列表、商品详情、购物车
Broken AIL:
```ail
**Task 1**
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]
#UI[landing:Hero]
---
**Task 2**
#PROFILE[ecom_min]
@PAGE[Home,/]
#UI[ecom:Header]
#UI[ecom:ProductGrid]
@PAGE[Product,/product/:id]
#UI[ecom:ProductDetail]
@PAGE[Cart,/cart]
#UI[ecom:CartPanel]
```
Expected Repair Goal:
提取更匹配 requirement 的 ecom_min 段，去掉 wrapper
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes

## Case R3
Case ID: R3
Requirement:
做一个产品营销页，包含 Hero、功能亮点、联系我们
Broken AIL:
```ail
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]
#UI[landing:Hero]
#UI[landing:Testimonials]
#UI[landing:Footer]
```
Expected Repair Goal:
删除或替换未知组件，并补齐 FeatureGrid 与 Contact
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes

## Case R4
Case ID: R4
Requirement:
做一个官网联系页，支持用户提交联系表单
Broken AIL:
```ail
#PROFILE[landing]
@PAGE[Contact,/contact]
#UI[landing:Contact]
#FLOW[SUBMIT_CONTACT]
```
Expected Repair Goal:
将未知 flow 修成 CONTACT_SUBMIT
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes

## Case R5
Case ID: R5
Requirement:
做一个 AI Chat App 原型，包含顶部栏、底部 tab、聊天列表、聊天窗口
Broken AIL:
```ail
#PROFILE[app_min]
@API[AUTH,/api/login]{>DB_AUTH[users]}
@PAGE[Login,/login]
@PAGE[Home,/]
#UI[app:TopBar]
#UI[app:BottomTab]
#UI[app:List]
#UI[app:ChatWindow]
```
Expected Repair Goal:
删除 auth 与 login 页，收敛成单页 app_min 原型
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes

## Case R6
Case ID: R6
Requirement:
做一个联系人 App 原型，包含顶部栏、底部 tab、联系人列表、个人卡片
Broken AIL:
```ail
#PROFILE[app_min]
@PAGE[Home,/]
#UI[app:TopBar]
#UI[app:BottomTab]
#UI[app:List]
@PAGE[Profile,/profile]
#UI[app:Card]
```
Expected Repair Goal:
收敛为单页 app_min，把 Card 合并回主页面
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes

## Case R7
Case ID: R7
Requirement:
做一个 AI SaaS 官网，包含首页、功能介绍、团队、FAQ、联系我们
Broken AIL:
```ail
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]
#UI[landing:Hero]
#UI[landing:Footer]
```
Expected Repair Goal:
补齐 FeatureGrid、Team、FAQ、Contact 和 CONTACT_SUBMIT
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes

## Case R8
Case ID: R8
Requirement:
做一个售后入口，包含退款申请、投诉提交、升级处理入口
Broken AIL:
```ail
#PROFILE[after_sales]
@PAGE[AfterSales,/after-sales]
#UI[after_sales:Entry]
```
Expected Repair Goal:
补齐 Refund、Complaint、REFUND_FLOW、COMPLAINT_DEESCALATE
Expected Post-Repair Diagnosis:
- valid: yes
- compile_recommended: yes
