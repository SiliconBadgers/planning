# Technical source inventory

Inspected on September 10, 2026. This inventory contains model configuration,
tensor shapes and provenance. It contains no downloaded model weight values.

| File | Provenance and use |
|---|---|
| [qwen35-2b-model.json](qwen35-2b-model.json) | [Official model API](https://huggingface.co/api/models/Qwen/Qwen3.5-2B), recorded revision and parameter totals |
| [qwen35-2b-config.json](qwen35-2b-config.json) | [Pinned checkpoint configuration](https://huggingface.co/Qwen/Qwen3.5-2B/blob/15852e8c16360a2fea060d615a32b45270f8a8fc/config.json) |
| [qwen35-2b-tensors.json](qwen35-2b-tensors.json) | Shapes and dtypes from the pinned safetensors header; two bounded Range requests read eight length bytes and 76,648 header bytes |
| [transformers-reference.json](transformers-reference.json) | Inspected source commit, URL and SHA256; no claim of an installed or executed runtime |
| [version-survey.json](version-survey.json) | Bounded official-author lookups for Qwen3.6 and Qwen3.7 |
| [team-manifest.json](team-manifest.json) | Display roles and starter-code status for the included team snapshots |
| [team-charters/README.md](team-charters/README.md) | Exact charter and objective copies from the recorded component revisions |

The model source revision is `15852e8c16360a2fea060d615a32b45270f8a8fc`.
The metadata total is 2,274,069,824 parameters in 632 stored tensors. The text
subset is 1,881,825,088 parameters, with tied input/output weights counted once.
Vision and multi-token-prediction tensors are identified separately in the plan.

The reference implementation was inspected at Transformers commit
`5b7dcb0d36c242d8d85920a81c564ef3a86ca6dd`. Its file checksum is recorded in
the JSON provenance record. Runtime dependencies, kernels and numerical output
have not been validated by this documentation task.

Primary technical references used by the plan:

- [Qwen3.5-2B model card](https://huggingface.co/Qwen/Qwen3.5-2B).
- [OCP Microscaling Formats v1.0](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf).
- [NVIDIA NVFP4 format description](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/).
- [Gated Delta Networks](https://arxiv.org/abs/2412.06464).
- [FlashAttention](https://arxiv.org/abs/2205.14135).
- [GQA](https://arxiv.org/abs/2305.13245).
- [AWQ](https://arxiv.org/abs/2306.00978).
- [GPTQ](https://arxiv.org/abs/2210.17323).

Links identify the source of facts and methods. The system budgets and design
recommendations are this project's calculations and analysis, with assumptions
in [model-budget.json](../model-budget.json). They are not measured results
from these papers or from the project hardware.
