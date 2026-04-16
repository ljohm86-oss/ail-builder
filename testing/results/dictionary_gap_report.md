# Dictionary Gap Report

## Inputs
- raw_results: `/Users/carwynmac/ai-cl/testing/results/raw_model_outputs_results.json`
- real_requirements_results: `/Users/carwynmac/ai-cl/testing/results/real_requirements_results.json`
- benchmark_results: `/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json`

## Summary
- raw_samples: 23
- real_requirements: 30
- benchmark_release_decision: pass
- active_suggested_tokens: 0
- closed_gaps_detected: 6

## Unknown Components

## Unknown Flows

## Alias / Drift Normalized
### after_sales
- `SUPPORT_ESCALATE->COMPLAINT_DEESCALATE`: 1 (RAW_A3)
### app_min
- none
### ecom_min
- `ADD_CART->ADD_TO_CART`: 1 (RAW_E5)
- `ecom:Search->ecom:SearchResultGrid`: 1 (RAW_E3)
### landing
- `landing:Testimonials->landing:Testimonial`: 2 (RAW_L3, RAW_L9)
- `SUBMIT_CONTACT->CONTACT_SUBMIT`: 1 (RAW_L6)

## Under-specified Patterns
### after_sales
- `客服` -> `after_sales:Support`: 7 (raw=RAW_A1,RAW_A4; real=A1,A2,A3,A4,A5)
- `联系客服` -> `after_sales:Support`: 4 (raw=RAW_A1,RAW_A4; real=A3,A5)
### landing
- `客户评价` -> `landing:Testimonial`: 2 (raw=RAW_L9; real=L3)
- `职位展示` -> `landing:Jobs`: 1 (real=L5)
- `项目作品` -> `landing:Portfolio`: 1 (real=L6)
### app_min
- `新增任务` -> `app:Composer`: 2 (raw=RAW_P4; real=P2)
- `搜索联系人` -> `app:SearchBar`: 1 (real=P3)
- `编辑笔记` -> `app:Composer`: 1 (real=P4)

## Boundary Pressure
### after_sales
- after_sales lacks support/contact block: 4 (RAW_A1, RAW_A4)
### app_min
- app_min boundary auth/login/api pressure: 2 (RAW_P1, RAW_P2)
### landing
- landing lacks testimonial/review block: 1 (RAW_L9)

## Closed Gaps
- `after_sales:Support` [after_sales/ui] evidence=11 issues=under_specified
- `app:Composer` [app_min/ui] evidence=3 issues=under_specified
- `landing:Testimonial` [landing/ui] evidence=2 issues=under_specified
- `app:SearchBar` [app_min/ui] evidence=1 issues=under_specified
- `landing:Jobs` [landing/ui] evidence=1 issues=under_specified
- `landing:Portfolio` [landing/ui] evidence=1 issues=under_specified

## Suggested Tokens
- none
