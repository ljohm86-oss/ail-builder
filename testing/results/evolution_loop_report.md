# Evolution Loop Report

## Summary
- raw_samples: 50
- real_requirements: 30
- benchmark_release_decision: fail
- active_suggested_tokens: 0
- closed_signals_count: 11
- recoverable_patterns_count: 4
- active_patch_pressure_count: 0

## By Cohort
- legacy_raw: total=27, initial_compile_rate=29.63, final_compile_rate=100.0
- patch_validation: total=13, initial_compile_rate=92.31, final_compile_rate=100.0
- clean_control: total=10, initial_compile_rate=100.0, final_compile_rate=100.0

## Closed Signals
### after_sales:Support
- profile: after_sales
- signal_type: closed_gap
- evidence_count: 11
- reason: High frequency requirement phrase '联系客服' appears in under_specified samples

### app:Composer
- profile: app_min
- signal_type: closed_gap
- evidence_count: 3
- reason: High frequency requirement phrase '新增任务' appears in under_specified samples

### landing:Testimonial
- profile: landing
- signal_type: closed_gap
- evidence_count: 2
- reason: High frequency requirement phrase '客户评价' appears in under_specified samples

### landing:Testimonials->landing:Testimonial
- profile: landing
- signal_type: alias_normalized
- evidence_count: 2
- reason: Alias/drift already normalized: landing:Testimonials->landing:Testimonial

### SUPPORT_ESCALATE->COMPLAINT_DEESCALATE
- profile: after_sales
- signal_type: alias_normalized
- evidence_count: 1
- reason: Alias/drift already normalized: SUPPORT_ESCALATE->COMPLAINT_DEESCALATE

### app:SearchBar
- profile: app_min
- signal_type: closed_gap
- evidence_count: 1
- reason: High frequency requirement phrase '搜索联系人' appears in under_specified samples

### ADD_CART->ADD_TO_CART
- profile: ecom_min
- signal_type: alias_normalized
- evidence_count: 1
- reason: Alias/drift already normalized: ADD_CART->ADD_TO_CART

### ecom:Search->ecom:SearchResultGrid
- profile: ecom_min
- signal_type: alias_normalized
- evidence_count: 1
- reason: Alias/drift already normalized: ecom:Search->ecom:SearchResultGrid

### SUBMIT_CONTACT->CONTACT_SUBMIT
- profile: landing
- signal_type: alias_normalized
- evidence_count: 1
- reason: Alias/drift already normalized: SUBMIT_CONTACT->CONTACT_SUBMIT

### landing:Jobs
- profile: landing
- signal_type: closed_gap
- evidence_count: 1
- reason: High frequency requirement phrase '职位展示' appears in under_specified samples

### landing:Portfolio
- profile: landing
- signal_type: closed_gap
- evidence_count: 1
- reason: High frequency requirement phrase '项目作品' appears in under_specified samples


## Recoverable Patterns
### recoverable_coverage_gap
- profile: landing
- evidence_count: 10
- cohorts: legacy_raw, patch_validation
- sample_ids: RAW_L10, RAW_L11, RAW_L12, RAW_L13, RAW_L14, RAW_L15, RAW_L16, RAW_L17, RAW_L20, RAW_L21

### recoverable_support_gap
- profile: after_sales
- evidence_count: 5
- cohorts: clean_control, legacy_raw, patch_validation
- sample_ids: RAW_A1, RAW_A4, RAW_A5, RAW_A6, RAW_A7

### recoverable_app_boundary_violation
- profile: app_min
- evidence_count: 3
- cohorts: legacy_raw
- sample_ids: RAW_P1, RAW_P2, RAW_P7

### recoverable_coverage_gap
- profile: app_min
- evidence_count: 3
- cohorts: legacy_raw, patch_validation
- sample_ids: RAW_P4, RAW_P5, RAW_P6


## Active Patch Pressure
- none
