# Writing Test Matrix (2026-04-28)

This document defines the current regression and exploratory test matrix for the `writing` branch in AIL Builder.

It is intentionally practical:
- use it to verify copy, story, and book flows after CLI changes
- use it to confirm out-of-scope boundaries stay tight
- use it to reproduce bundle, clipboard, and shell-wrapper issues

## Scope

The current `writing` branch covers these operator-facing commands:
- `writing packs`
- `writing check`
- `writing intent`
- `writing scaffold`
- `writing brief`
- `writing expand`
- `writing review`
- `writing bundle`

The current supported lanes are:
- `copy_min`
- `story_min`
- `book_min`

The current branch should reject:
- one-shot finished long-form novel asks
- publication-ready full-book asks
- legal-contract or high-stakes professional-document generation
- platform, CMS, workflow-system, or editor-app requests

## Recommended Test Environments

Prioritize these environments:
- macOS + `zsh`
- Windows + PowerShell
- Windows + `cmd` or Git Bash

For each run, record:
- `git log --oneline -3`
- `python --version` or `python3 --version`
- shell type
- whether `PYTHONPATH` was set explicitly

## Fast Sanity Pass

Run these first when you want a short health check:

```bash
python -m cli writing check "写一个产品发布公告，包含发布时间、核心亮点和行动号召。" --json
python -m cli writing check "直接写完一部长篇 20 万字奇幻小说。" --json
python -m cli writing expand "写一个科幻小说开头，包含主要冲突。" --deep --json
python -m cli writing review "写一个企业产品宣传文案，包含首页主标题、卖点和 CTA。" --text "Help operators cut reporting time in half. Request pricing today." --emit-summary
python -m cli writing bundle "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --deep --zip --copy-summary --emit-summary
```

Expected result:
- copy release-announcement request maps to `copy_min`
- long-form one-shot novel request maps to `out_of_scope`
- `expand --deep` returns `expand_mode = second_draft_pass`
- `review --emit-summary` returns alignment fields quickly
- `bundle` returns without hanging and emits a compact summary

## Classification Matrix

### `copy_min`

```text
写一个企业产品宣传文案，包含首页主标题、卖点和 CTA。
写一个产品发布公告，包含发布时间、核心亮点和行动号召。
写一个新品上新通知，适合官网和社媒同步发布。
```

Expected:
- `status = ok`
- `support_level = Supported`
- `expected_profile = copy_min`
- `writing_pack = Copy / Messaging Pack`

### `story_min`

```text
写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。
写一个科幻故事开头，突出悬念和人物处境。
设计一个悬疑小说人物关系和五章结构。
```

Expected:
- `status = ok`
- `support_level = Supported`
- `expected_profile = story_min`
- `writing_pack = Story / Fiction Outline Pack`

### `book_min`

```text
写一本非虚构商业书目录和章节目标，帮助创业者搭建销售系统。
规划一本数据分析入门书的目录、章节目标和读者转化。
写一本个人成长类书籍的大纲和章节路线。
```

Expected:
- `status = ok`
- `support_level = Supported`
- `expected_profile = book_min`
- `writing_pack = Book / Nonfiction Blueprint Pack`

### Out Of Scope

```text
直接写完一部长篇 20 万字奇幻小说。
给我生成一本可以直接出版的完整商业书全文。
写一个完整法律合同并保证可直接生效。
```

Expected:
- `status = out_of_scope`
- `support_level = Out of Scope`
- `expected_profile = out_of_scope`
- `boundary_findings` should clearly explain why the ask crossed the current writing surface

## Intent Tests

Write intent:

```bash
python -m cli writing intent \
  --audience "indie founders" \
  --format-mode story \
  --genre "science fantasy" \
  --style-direction "clear cinematic" \
  --target-length "chapter_outline" \
  --tone-keyword calm \
  --tone-keyword tense \
  --json
```

Read intent:

```bash
python -m cli writing intent --json
```

Then run:

```bash
python -m cli writing scaffold "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --json
```

Expected:
- saved intent is readable
- scaffold includes the relevant intent context
- switching from story asks to book asks should not blindly leak story-only assumptions into the new scaffold

## Scaffold Tests

### Copy scaffold

```bash
python -m cli writing scaffold "写一个企业产品宣传文案，包含首页主标题、卖点和 CTA。" --json
```

Expected fields:
- `headline`
- `message_architecture`
- `sections`
- `draft_tasks`

### Story scaffold

```bash
python -m cli writing scaffold "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --json
```

Expected fields:
- `story_core`
- `character_cards`
- `chapter_tree`
- `scene_tasks`

### Book scaffold

```bash
python -m cli writing scaffold "写一本非虚构商业书目录和章节目标，帮助创业者搭建销售系统。" --json
```

Expected fields:
- `table_of_contents`
- `chapter_cards`
- `research_gaps`

## Brief Tests

```bash
python -m cli writing brief "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --emit-prompt
python -m cli writing brief "写一个企业产品宣传文案，包含首页主标题、卖点和 CTA。" --json
```

Expected:
- `model_prompt` is present
- the prompt includes requirement, scaffold anchors, and boundary framing
- the emitted text is usable as a handoff prompt for an external model

## Expand Tests

### Base expand

```bash
python -m cli writing expand "写一个企业产品宣传文案，包含首页主标题、卖点和 CTA。" --json
python -m cli writing expand "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --json
python -m cli writing expand "写一本非虚构商业书目录和章节目标，帮助创业者搭建销售系统。" --json
```

### Deep expand

```bash
python -m cli writing expand "写一个科幻小说开头，包含主要冲突。" --deep --json
python -m cli writing expand "规划一本数据分析书籍目录和章节目标。" --deep --json
```

Expected:
- base expand returns `expand_mode = first_draft_pass`
- deep expand returns `expand_mode = second_draft_pass`
- base expand returns `expand_depth = base`
- deep expand returns `expand_depth = deep`
- `expand_variant` is present and deterministic for the same requirement
- `expanded_text` should not collapse into obvious repetition

## Review Tests

### Strong draft

```bash
python -m cli writing review "写一个企业产品宣传文案，包含首页主标题、卖点和 CTA。" --text "Help operators cut reporting time in half. The workflow is faster, clearer, and easier to roll out across the team. Request pricing today." --json
```

### Weak draft

```bash
python -m cli writing review "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --text "She walked into a room. It was quiet." --json
```

### Drifted draft

```bash
python -m cli writing review "写一本非虚构商业书目录和章节目标，帮助创业者搭建销售系统。" --text "The moonlight fell over the ruined tower as the prince drew his blade." --json
```

Expected:
- stronger drafts should score higher than weak or drifted drafts
- drifted drafts should surface clearer `drift_findings`
- `next_pass_prompt` should remain usable as a targeted revision instruction

## Bundle Tests

### Base bundle

```bash
python -m cli writing bundle "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --deep --output-dir /tmp/writing-bundle --json
```

### Zip bundle

```bash
python -m cli writing bundle "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --deep --zip --output-dir /tmp/writing-bundle --json
```

### Copy archive path

```bash
python -m cli writing bundle "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --deep --zip --copy-archive-path --output-dir /tmp/writing-bundle --json
```

### Copy summary

```bash
python -m cli writing bundle "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --deep --zip --copy-summary --output-dir /tmp/writing-bundle --json
```

### Summary mode

```bash
python -m cli writing bundle "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --deep --zip --emit-summary
```

Expected files:
- `check.json`
- `scaffold.json`
- `brief.json`
- `brief_prompt.txt`
- `expand.json`
- `expand.txt`
- `review.json`
- `review_summary.txt`
- `bundle_manifest.json`
- `README.txt`

Expected metadata:
- `manifest_version`
- `bundle_created_at`
- `summary_text`
- optional `archive_path`
- optional clipboard result fields when copy flags were used

## Shell Wrapper Regression

These tests are specifically important for wrapped shells and automation runners.

### Bundle should not hang on empty stdin

```bash
printf '' | python -m cli writing bundle "写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。" --deep --emit-summary
```

Expected:
- command returns immediately
- `review_source = expanded_text`
- no passive wait on stdin

This regression matters because PowerShell-based runners and test harnesses may attach stdin even when no review text was intentionally provided.

## Windows-Specific Notes

On non-macOS environments:
- `--copy-archive-path` and `--copy-summary` may fail gracefully if `pbcopy` is unavailable
- that should not break bundle generation itself
- record `copy_archive_path_error` or `copy_summary_error` if present

Recommended Windows checks:
- verify Chinese requirements survive quoting intact
- verify `--output-file` and `--output-dir` work with Windows paths
- verify `bundle` no longer hangs under PowerShell wrappers

## Suggested Result Capture Format

For each manual test, record:
1. command
2. environment
3. result: success, failed, or partial
4. critical output fields
5. user-visible problem, if any
6. reproducibility: always, intermittent, or unknown

## Current Readiness Summary

As of 2026-04-28, the `writing` branch is suitable for alpha testing with a stable scaffold-first workflow:
- classification is now strict enough to reject one-shot full-manuscript asks
- bundle export completes locally and no longer blocks on passive stdin reads
- the main remaining risks are output quality tuning and cross-shell ergonomics, not missing core command coverage
