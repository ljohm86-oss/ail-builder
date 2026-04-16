# Raw Model Outputs v1

这是一条独立于 benchmark 与 release baseline 的原始输出测试线。

目的：

- 模拟团队成员、IDE、外部模型给出的原始 AIL 输出
- 验证当前系统链路：
  - raw output
  - `Diagnostic`
  - `Repair`
  - `Diagnostic`
  - compile candidate

该目录中的样本不是“理想生成结果”，而是故意包含脏样本与边界样本，用于观察：

- Diagnostic 能拦下什么
- Repair 能救回什么
- 原始 compile candidate 率与修复后 compile candidate 率

当前样本分布：

- landing: 8
- ecom_min: 6
- after_sales: 3
- app_min: 3

当前覆盖的噪声类型：

- multiple_profile
- multi_result_wrapper
- separator (`---`)
- markdown_wrapper
- unknown_component
- unknown_flow
- app_min_boundary_auth
- under_specified
- clean_control
