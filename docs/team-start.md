# Parallel team investigations

Current starting material, September 22, 2026. This packet connects the revised
block diagram to the first completed llama.cpp profile. It supersedes the old
eleven-team organization for current coordination; the September 10 plan and
charter snapshots remain historical background. No personal assignments or
calendar deadlines are created here.

## Read these together

- [Editable Mermaid architecture](https://github.com/SiliconBadgers/architecture/blob/main/docs/accelerator-diagram.md): functional engines, local/top-level control, buffers and platform memory.
- [Candidate boundary worksheet](https://github.com/SiliconBadgers/architecture/blob/main/contracts/accelerator-boundaries.md): acceptance, completion, state ownership, backpressure and errors.
- [Shared workload cases](https://github.com/SiliconBadgers/architecture/blob/main/docs/workload-cases.md), including a small CSV extracted from measured matrix shapes.
- [Profiling report](https://github.com/SiliconBadgers/software/blob/main/experiments/llama-cpp/2026-09-22/REPORT.md) and [reproduction procedure](https://github.com/SiliconBadgers/software/blob/main/experiments/llama-cpp/2026-09-22/README.md), with code, source/model pins, results and numerical checks.

The diagram is a hypothesis. It does not settle the number of engines, whether
arithmetic should be shared, the numerical policy or the final host/command ABI.
An existing CPU runs software; no custom CPU/ISA or separate compiler team is
required. Software includes workload mapping, backend/runtime and host integration.

## Evidence available now

At a 2048-token prompt, matrix products occupy roughly 80% of timed CPU prefill
operations and 82% of decode operations; the vocabulary output head is about
25% of decode. These are CPU operation intervals, not silicon area allocations
or predicted accelerator speedups. They motivate studying projections and the
output head together rather than limiting a matrix engine to the MLP.

The baseline uses a mixed-format Q4_K_M GGUF, not the proposal's custom uniform
INT4. The repeated passage is not a task-quality benchmark. The 8192-token CPU
trace has an unresolved timing anomaly and is excluded from timing conclusions.
All teams can use the current shapes, traces and saved outputs now.

## Work that can proceed concurrently

| Workstream | Repository / starting guide | First useful output | Exchange with others |
|---|---|---|---|
| Software | [software](https://github.com/SiliconBadgers/software/blob/main/docs/START-HERE.md) | A representative workload extension or selected dependency/state trace with numerical checks and an offload comparison | Shapes, layouts, lifetimes and end-to-end costs |
| Compute 1 | [rtl-compute](https://github.com/SiliconBadgers/rtl-compute/blob/main/docs/START-HERE.md) | Shared matrix/vector datapath alternatives with utilization, storage and operand-rate estimates | Candidate arithmetic coverage and resource demand |
| Compute 2 | [rtl-compute](https://github.com/SiliconBadgers/rtl-compute/blob/main/docs/START-HERE.md) | Stateful/non-matrix operation map and candidate shared/specialized partition | State sequencing, local control and fusion boundaries |
| Memory Control | [rtl-memory](https://github.com/SiliconBadgers/rtl-memory/blob/main/docs/START-HERE.md) | Parameterized traffic/storage model and bank/port sketch | Bandwidth ceilings, ownership and transfer latencies |
| Top-Level Control | [rtl-control](https://github.com/SiliconBadgers/rtl-control/blob/main/docs/START-HERE.md) | Dependency/scheduler comparison using engine/memory stubs | Command granularity, completion and recovery behavior |
| Verification | [verification](https://github.com/SiliconBadgers/verification/blob/main/docs/START-HERE.md) | Small numerical/state fixtures, comparator and protocol cases | Exact/tolerance criteria and observable failures |
| Physical Design | [physical-design](https://github.com/SiliconBadgers/physical-design/blob/main/docs/START-HERE.md) | Arithmetic/memory feasibility comparison with actual library/tool constraints | Affordable widths, ports, lanes and uncertainty |
| Architecture coordination | [architecture](https://github.com/SiliconBadgers/architecture/blob/main/docs/START-HERE.md) | Evidence-backed comparison of candidate partitions | Shared decisions and unresolved assumptions |
| Host/system boundary | [soc](https://github.com/SiliconBadgers/soc/blob/main/docs/START-HERE.md) | Host-to-completion walkthrough and interface diagram using stubs | Registers/status/IRQ, clocks/resets and platform boundary |
| Cross-repository integration | [accelerator](https://github.com/SiliconBadgers/accelerator/blob/main/docs/START-HERE.md) | One reproducible slice with real-versus-stub inventory | Compatible revisions and cross-boundary mismatches |

The last three rows identify repository responsibilities, not new Discord
subteams. Compute 1 and Compute 2 share `rtl-compute`; their investigation split
does not assign permanent engine ownership. The nine engineering repositories linked above plus this `planning` repository
form the ten core repositories.

## Share evidence early

Each study should preserve its question, inputs/source revisions, assumptions,
method/commands, outputs with units, correctness checks, limitations and the
decision it informs. A useful partial result is preferable to waiting for every
related study to finish. Models and stubs can exercise unresolved boundaries.

At a joint review, compare compatible cases across compute demand, memory traffic,
control overhead, numerical behavior and physical feasibility. Freeze only the
details needed for the next integration slice. Use the
[decision template](https://github.com/SiliconBadgers/architecture/blob/main/decisions/decision-template.md)
to record alternatives, evidence and conditions for revisiting a choice.

## Current collateral and limits

| Material | Status |
|---|---|
| llama.cpp baseline, methodology, code and results | Published in Software; analysis reproduced and saved-output checks verified |
| Mermaid hierarchy and boundary worksheet | Proposed design material in this coordinated documentation change |
| Per-repository starting guides and matrix cases | Initial material for teams to revise through evidence |
| Full accelerator, final compute partition and custom numerical policy | Not implemented or validated by this packet |
| Small MAC example | Existing optional runnable example, separate from the proposed accelerator |
| Main protection / required approval | Requested, but GitHub Free blocks enforcement for these private repositories |
| CODEOWNERS | This change proposes `@abhinavnandwani` as sole owner in the ten core repositories; the file alone does not enforce review |

Keep this page current when new results or decisions are accepted. Preserve dated
experimental evidence in its owning repository and link it here instead of
copying mutable results into multiple repos.
