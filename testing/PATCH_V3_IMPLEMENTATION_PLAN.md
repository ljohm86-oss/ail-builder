# Patch V3 Implementation Plan

## 1. Goal

Patch v3 is a rule-tightening patch, not a token patch.

The goal is to improve:

- generator coverage stability
- repair completion stability
- boundary enforcement for `app_min` and `after_sales`

This patch should reduce:

- `under_specified`
- repeated support/contact misses in `after_sales`
- repeated app boundary drift toward `auth/login/api`

This patch should not introduce new tokens, new profiles, or compiler architecture changes.

## 2. Scope

### In Scope

- tighten `after_sales` support phrase mapping
- tighten `app_min` boundary suppression rules
- tighten `landing` coverage rules for installed tokens
- tighten `app_min` coverage rules for installed tokens
- update local testing logic only if needed to reflect the tighter rules

### Out of Scope

- new token patch
- new profile
- benchmark policy change
- compiler redesign
- major renderer changes
- protocol changes

## 3. Candidate Rules To Tighten

### after_sales

Observed signal:

- `after_sales:Support` remains a high-frequency closed gap
- boundary pressure still shows `after_sales lacks support/contact block`
- phrases like `客服`, `联系客服`, `support` still trigger under-specification

Rules to tighten:

- Generator should more aggressively add `after_sales:Support` when requirement contains:
  - `客服`
  - `联系客服`
  - `support`
  - `人工客服`
  - `在线客服`
- Repair should always add `after_sales:Support` if requirement contains the phrases above and profile is `after_sales`
- If requirement includes `退款 + 客服`, keep:
  - `after_sales:Refund`
  - `after_sales:Support`
- If requirement includes `换货 + 客服`, keep:
  - `after_sales:Exchange`
  - `after_sales:Support`

Expected effect:

- fewer `under_specified` after-sales samples
- lower boundary pressure for support/contact coverage

### app_min boundary

Observed signal:

- `app_min boundary auth/login/api pressure` is still present
- raw lane still contains samples drifting toward:
  - login
  - auth
  - API
  - business-like multi-page workflows

Rules to tighten:

- Generator should more strongly suppress:
  - `login`
  - `auth`
  - `authentication`
  - `权限`
  - `API`
  - `接口`
  - `后台`
  - `多页面业务系统`
- Generator should always collapse `app_min` to:
  - exactly one `@PAGE[Home,/]`
  - `app:TopBar`
  - `app:BottomTab`
  - optional `app:List`
  - optional `app:Card`
  - optional `app:ChatWindow`
  - optional `app:Composer`
  - optional `app:SearchBar`
- Repair should delete:
  - auth/login page blocks
  - `@API[...]`
  - DB/API-oriented business expansion
  - extra pages beyond `/`
- Repair should preserve or restore the minimal single-page mobile shell

Expected effect:

- lower app boundary pressure
- fewer app samples drifting into unsupported app/business patterns

### landing coverage

Observed signal:

- `landing:Testimonial`, `landing:Jobs`, `landing:Portfolio` are installed but still appear in closed-gap under-spec evidence

Rules to tighten:

- Generator should more consistently add `landing:Testimonial` when requirement contains:
  - `客户评价`
  - `用户评价`
  - `testimonial`
  - `testimonials`
  - `口碑`
- Generator should more consistently add `landing:Jobs` when requirement contains:
  - `职位展示`
  - `招聘`
  - `岗位`
  - `careers`
- Generator should more consistently add `landing:Portfolio` when requirement contains:
  - `项目作品`
  - `案例展示`
  - `作品集`
  - `portfolio`
  - `案例`
- Repair should add these blocks when profile is `landing` and the matching phrases are present

Expected effect:

- lower landing under-specification for these installed tokens

### app_min coverage

Observed signal:

- `app:Composer` and `app:SearchBar` are installed but still appear as closed-gap under-spec signals

Rules to tighten:

- Generator should more consistently add `app:Composer` when requirement contains:
  - `新增任务`
  - `编辑`
  - `输入`
  - `composer`
  - `编辑笔记`
- Generator should more consistently add `app:SearchBar` when requirement contains:
  - `搜索联系人`
  - `搜索`
  - `search`
- Repair should add these blocks when profile is `app_min` and the phrases are present, while still keeping single-page shape

Expected effect:

- lower app under-specification for installed coverage tokens

## 4. Files Expected To Change

Expected files to touch in Patch v3:

- `/Users/carwynmac/ai-cl/skills/ail-generator-v1.2/SKILL.md`
- `/Users/carwynmac/ai-cl/skills/ail-repair-v1/SKILL.md`
- `/Users/carwynmac/ai-cl/testing/raw_model_outputs_runner.py`
- `/Users/carwynmac/ai-cl/testing/real_requirements_runner.py`
- `/Users/carwynmac/ai-cl/testing/repair_smoke_runner.py`
- `/Users/carwynmac/ai-cl/testing/evolution_loop_runner.py`

Files to avoid unless absolutely necessary:

- `/Users/carwynmac/ai-cl/ail_engine_v5.py`
- `/Users/carwynmac/ai-cl/benchmark/**`

## 5. Validation Plan

Run at minimum:

```bash
bash /Users/carwynmac/ai-cl/testing/run_raw_model_outputs.sh
bash /Users/carwynmac/ai-cl/testing/run_evolution_loop.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

Optional but recommended:

```bash
bash /Users/carwynmac/ai-cl/testing/run_real_requirements.sh
```

Metrics to watch:

- raw lane `under_specified` count
- raw lane `after_sales:Support` misses
- raw lane `app_min_boundary_exceeded` count
- evolution loop:
  - `generator_rule_patch` count
  - `boundary_rule_patch` count
  - whether `after_sales:Support` remains high-priority
  - whether `app:Composer` / `app:SearchBar` / `landing:*` coverage candidates decrease
- benchmark:
  - `release_decision` must remain `pass`

Success criteria:

- `under_specified` should decrease or at least not rise
- `after_sales:Support` generator-rule pressure should decrease
- `app_min` boundary pressure should decrease
- benchmark remains `pass`

## 6. Non-Goals

- do not add new tokens
- do not add new profiles
- do not change benchmark policy
- do not redesign compiler
- do not introduce new page families

## 7. Recommended Execution Order

1. Tighten `after_sales` support phrase mapping in generator and repair rules.
2. Tighten `app_min` boundary suppression rules in generator and repair rules.
3. Tighten installed-token coverage rules for `landing` and `app_min`.
4. Re-run raw lane and evolution loop; compare candidate pressure.
5. Run benchmark last to confirm no release regression.
