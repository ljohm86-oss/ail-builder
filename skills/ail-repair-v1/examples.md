# AIL Repair Skill v1 Examples

## Example 1: multiple profile mixed

Input fragment:

```text
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]
#PROFILE[ecom_min]
@PAGE[Home,/]
#UI[ecom:Header]
```

Repaired output:

```text
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]
```

## Example 2: multi-result wrapper

Input fragment:

```text
**Task 1**
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Hero]
---
**Task 2**
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Hero]
#UI[landing:Contact]
```

Repaired output:

```text
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Hero]
#UI[landing:Contact]
```

## Example 3: app_min boundary exceeded

Input fragment:

```text
#PROFILE[app_min]
@API[AUTH,/api/login]{>DB_AUTH[users]}
@PAGE[Home,/]
#UI[app:TopBar]
#UI[app:BottomTab]
#UI[app:List]
```

Repaired output:

```text
#PROFILE[app_min]
@PAGE[Home,/]
#UI[app:TopBar]
#UI[app:BottomTab]
#UI[app:List]
```

## Example 4: landing under-specified

Input fragment:

```text
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]
#UI[landing:Hero]
#UI[landing:Footer]
```

Requirement hint:

```text
做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们
```

Repaired output:

```text
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]
#UI[landing:Hero]
#UI[landing:FeatureGrid]
#UI[landing:FAQ]
#UI[landing:Contact]
#UI[landing:Footer]
#FLOW[CONTACT_SUBMIT]
```
