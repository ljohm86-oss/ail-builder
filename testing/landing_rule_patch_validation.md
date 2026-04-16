# Landing Rule Patch Validation

## Scope

This note records the validation outcome of the landing LogoCloud/Testimonial disambiguation patch.

Patch intent:

- narrow `landing:LogoCloud` triggers
- avoid false LogoCloud matches for testimonial language
- keep compile behavior and benchmark policy unchanged

## Rule Change Summary

`landing:LogoCloud` is now triggered only by explicit logo/partner style phrases such as:

- `客户 Logo`
- `客户标识`
- `客户 logos`
- `logo`
- `logos`
- `合作伙伴`
- `合作伙伴 logo`
- `partners`
- `partner logos`
- `品牌墙`
- `客户墙`

The following phrases are treated as testimonial-first signals instead of LogoCloud:

- `客户评价`
- `用户评价`
- `用户反馈`
- `客户反馈`
- `testimonial`
- `testimonials`
- `customer review`
- `review block`
- `口碑`

## Directed Checks

Validated inputs:

1. `做一个官网，包含客户评价、FAQ、联系我们`
2. `做一个官网，包含客户 Logo、合作伙伴、联系我们`
3. `做一个官网，包含用户反馈、功能介绍、联系我们`
4. `做一个官网，包含 partners、logo wall、联系我们`

Observed behavior:

- cases 1 and 3:
  - hit `landing:Testimonial`
  - did not add `landing:LogoCloud`
- cases 2 and 4:
  - hit `landing:LogoCloud`
  - did not rely on testimonial recovery

## Raw Lane Evidence

Added raw samples:

- `RAW_L10`
- `RAW_L11`

Both intentionally used `landing:LogoCloud` for testimonial-like requirements.

Observed result after rerun:

- both were classified as `recoverable_coverage_gap`
- both repaired outputs added `landing:Testimonial`
- neither remained an active patch pressure signal

## Current Metrics

From the latest raw lane / evolution loop outputs:

- `raw_samples = 25`
- `initial_compile_rate = 52.0`
- `repair_success_rate = 100.0`
- `final_compile_rate = 100.0`
- `patch_validation.initial_compile_rate = 80.0`
- `patch_validation.final_compile_rate = 100.0`
- `active_patch_pressure_count = 0`

## Conclusion

This patch is validated.

- testimonial language is no longer silently accepted as LogoCloud intent
- logo/partner language still maps to `landing:LogoCloud`
- raw lane now reflects the improvement through recoverable coverage signals
- evolution loop no longer proposes a follow-up patch for this issue
