# Current team work

Updated September 22, 2026. This is the current seven-team assignment map.
The dated plan and eleven-charter snapshots remain historical context.

| Team | Repositories / issues | Current deliverable |
|---|---|---|
| Software | [software#3](https://github.com/SiliconBadgers/software/issues/3) | Extend llama.cpp profiling and recommend boundaries from evidence. |
| Compute1 | [rtl-compute#2](https://github.com/SiliconBadgers/rtl-compute/issues/2) | Independent full compute-unit proposal in research/compute1/. |
| Compute2 | [rtl-compute#2](https://github.com/SiliconBadgers/rtl-compute/issues/2) | Independent full compute-unit proposal in research/compute2/. |
| Top-Level Control | [rtl-control#2](https://github.com/SiliconBadgers/rtl-control/issues/2), [architecture#3](https://github.com/SiliconBadgers/architecture/issues/3) | Controller diagram/walkthrough here; MMIO and descriptor proposal in architecture#3. |
| Memory Control | [rtl-memory#2](https://github.com/SiliconBadgers/rtl-memory/issues/2) | Memory-controller diagram, interfaces and load-compute-store walkthrough. |
| Verification | [verification#2](https://github.com/SiliconBadgers/verification/issues/2), [verification#3](https://github.com/SiliconBadgers/verification/issues/3), [verification#4](https://github.com/SiliconBadgers/verification/issues/4) | Test plan, per-layer methodology and hardened Synopsys unit/integration pilots. |
| Synthesis / Physical Design | [physical-design#2](https://github.com/SiliconBadgers/physical-design/issues/2), [physical-design#3](https://github.com/SiliconBadgers/physical-design/issues/3) | One Synopsys chip baseline and synthesis coverage for every unit, with stubs. |

Compute1 and Compute2 independently investigate the entire compute question.
They do not split arithmetic versus stateful work or need a joint proposal.
Each can use Software's existing evidence and discuss interfaces with Memory
and Control while the wider profiling work continues.

## Shared references and supporting repos

- [Central diagram](https://github.com/SiliconBadgers/architecture/blob/main/docs/accelerator-diagram.md); the four compute boxes are provisional.
- [Software evidence and reproduction](https://github.com/SiliconBadgers/software/tree/main/experiments/llama-cpp/2026-09-22).
- [Slide maps](https://github.com/SiliconBadgers/architecture/blob/codex/register-map-baseline/docs/register-maps.md), preserved as a baseline in [architecture PR #2](https://github.com/SiliconBadgers/architecture/pull/2).
- `architecture` owns shared diagrams/contracts and decisions. `soc` and
  `accelerator` support composition/integration; they are not extra active teams.
- `planning` keeps this map and the historical plan. These seven active-team
  homes plus `soc`, `accelerator` and `planning` form ten core repositories.

## Before contributing

All ten core repositories are public. Main requires one code-owner approval
from @abhinavnandwani, with admin bypass enabled. Accept any pending invitation,
check branch push access, and work through PRs for review.

Each clone needs its tracked commit guard activated. Before AI edits or the
first commit, follow that repo's docs/git-ai.md. Configure capture, restart Codex,
verify an actual edit, and keep line attribution and visible co-author credit.

## Progress and evidence

The diagram and recorded Software profiling package exist. The register maps
are a slide baseline, not a frozen ABI. Repo folders, templates and contributor
checks organize the next work; they do not complete the open research, controller,
verification or synthesis issues. Synopsys runs and full accelerator results are
not claimed by the scaffold refresh.

Publish intermediate results with source revisions, commands, inputs, tool
versions, numerical checks and limits. Keep timing measurements distinct from
hardware estimates. Teams should arrange a meeting this week to divide their
assigned work. Update this page when deliverables are accepted, linking to the
owning repo instead of copying results or creating a competing diagram.
