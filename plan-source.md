# SiliconBadgers project master plan

A technical and organizational plan for a Qwen3.5-2B accelerator with four-bit weights, shared by eleven teams whose members choose their contributions.

**Status:** Working draft 0.2, technical baseline researched September 10, 2026. Qwen3.5-2B is the concrete checkpoint within the requested Qwen 3.5 through 3.7, approximately 2B direction. Four-bit weights are the target; INT4 versus FP4 and the other numerical formats remain explicit design questions. Checkpoint facts, project decisions, proposed experiments and analytical estimates are distinguished throughout. Each repository remains the authority for its own charter and accepted technical material.

## 01. Purpose and direction

SiliconBadgers is organizing an accelerator project around coherent engineering responsibilities. The project should produce both useful engineering evidence and a community capable of understanding, questioning and extending the design. Research, design reasoning, experiments, implementation, documentation and teaching can all contribute to that purpose.

The repositories give teams a charter and high-level objectives. Members choose the questions they want to pursue, the methods they use and the form of their contribution. Leads support that choice by clarifying context, connecting collaborators and helping the team communicate what it learns.

The shared workload is now Qwen3.5-2B. The initial technical scope is text prefill and autoregressive decode, with host tokenization and sampling. Vision and multi-token prediction remain possible extensions. This scope is a working proposal around the chosen model, while the exact performance, quality and physical resource targets still need to be settled.

Earlier Qwen-oriented accelerator work provides material for architectural exploration and possible reuse. The new repositories currently contain a much smaller working MAC example. The technical chapters connect the model to numerical formats, inference stages, storage, data movement, compute and verification without presenting the reference code as an already integrated system.

**The next shared decision:** select the four-bit numerical policy and a realistic system envelope using quality, bandwidth and implementation evidence. A common model gives teams context while preserving their choice of research and implementation directions.

## 02. What is settled

| Area | Current agreement |
|---|---|
| Model direction | Qwen 3.5 through 3.7 at approximately 2B, with Qwen/Qwen3.5-2B pinned as the concrete baseline. |
| Compression direction | Four-bit weights. INT4 and defined FP4 candidates will be compared; activations, state and cache precision are separate decisions. |
| Organization | The eleven team repositories belong to SiliconBadgers and are private. The separate `planning` repository houses this shared plan. |
| Repository structure | Hardware responsibilities use `rtl-compute`, `rtl-memory`, `rtl-control` and `soc`. Machine-learning work uses `ml-compiler` and `ml-models`. |
| Team direction | A detailed charter and high-level objectives define each team’s purpose. Members choose their contributions. |
| Leadership | Leads facilitate learning, context and collaboration. The organizing model is not an assigned queue of coding or infrastructure tickets. |
| Shared boundaries | Teams agree together on behavior that others depend on. Each accepted specification or implementation has one authoritative home. |
| Initial publication | Every new project repository began with one initial commit under the project author’s GitHub identity. Earlier local draft history was not imported. |
| Existing code | The INT8 MAC is optional learning and experimentation material. Its format does not establish a four-bit model implementation. |
| Document scope | This main plan covers engineering responsibilities and decisions. Applicant records and proposed personnel assignments are outside it. |

The repository snapshot accompanying this document records the exact initial revisions and the time their privacy and commit counts were checked. It describes that snapshot, rather than making a permanent claim about future repository history.

## 03. Current capabilities and limits

Five repositories participate in the runnable example. This is an inventory of supplied material, not a score for team progress.

| Repository | Supplied material | What it establishes |
|---|---|---|
| `architecture` | Signed-MAC contract and structural check | The behavior of the example primitive |
| `ml-models` | Numerical reference, four unit tests and deterministic vector generator | A reference for that contract and selected numerical cases |
| `rtl-compute` | Signed INT8 MAC with INT32 accumulation | A small arithmetic implementation with retained source attribution |
| `verification` | Independent runner and RTL testbench | Agreement with reference vectors and directed behavior checks |
| `accelerator` | Workspace manifest and combined runner | One working path through the separate repositories |

The published example passed four model tests, 261 golden vectors and 131,600 RTL checks from fresh GitHub clones. Directed checks include signed arithmetic, hold, clear priority, reset and wraparound. Wrong, empty and truncated vector inputs were rejected during the source validation.

`soc`, `rtl-memory`, `rtl-control`, `ml-compiler`, `fpga` and `physical-design` have charters, objectives and scaffolds, with no supplied component implementation. Their placeholder test commands report that state. Research and design contributions are assessed through their reasoning and evidence, independently of whether a component has an executable test target.

There is no validated full-model inference system, integrated control/memory/SoC implementation, compiler, board demonstration or ASIC physical implementation in these new repositories. The broader reference codebase has not been fully migrated. GitHub CI and additional operating-system environments have not been established by the current example checks.

{{TECHNICAL_PLAN}}

## 15. Team and repository map

The RTL teams own hardware responsibilities. Architecture, machine-learning work, verification, FPGA, physical design and system integration span those blocks. This is a map of responsibility, not a management hierarchy.

{{REPOSITORY_TABLE}}

Control and SoC have distinct charters. Control explains how accelerator operations progress, coordinate resources and complete. SoC explains how the hardware is composed and what the host can access and observe. `accelerator` connects knowledge and evidence across repositories, while `soc` owns the composed hardware design.

### What the Qwen target means for each charter

These are durable technical objectives and questions that teams can explore. The examples illustrate the scope of worthwhile contributions; leads and members choose their methods and work.

| Repository | Target-specific charter objective | Questions that can guide member proposals |
|---|---|---|
| `architecture` | Make the hybrid decoder and its system assumptions coherent | What scope, numerical contracts and resource envelope support a defensible complete result? |
| `rtl-compute` | Understand and realize useful arithmetic across dense, attention and recurrent work | How should matrix, vector and state operations share resources? What does INT4 or FP4 cost at equal quality? |
| `rtl-memory` | Make weights, scales and per-request state available at the needed rate | Which residency, packing, banking and transfer policies explain the measured bandwidth? |
| `rtl-control` | Make prefill, decode and context transitions progress predictably | What dependencies and scheduling policies balance utilization, responsiveness and correct state updates? |
| `soc` | Compose an observable, usable accelerator system | What host and memory interfaces, reset behavior and platform boundaries let the blocks work together? |
| `ml-compiler` | Express the model faithfully in executable artifacts and schedules | What export format, tiling and runtime abstraction preserve semantics while exposing hardware reuse? |
| `ml-models` | Establish the workload and the quality consequences of approximation | Which INT4/FP4 policies, activation formats and recurrent-state choices preserve useful behavior? |
| `verification` | Build independent confidence in numerical and system claims | How can errors be localized from packed tensors through persistent state to complete sequences? |
| `fpga` | Reveal practical behavior on an available prototype platform | What can the board demonstrate about bandwidth, capacity, integration and latency? |
| `physical-design` | Establish what the architecture can plausibly become in silicon | Which memories, clocks, ports and arithmetic choices are physically credible under identified constraints? |
| `accelerator` | Maintain an interpretable complete-system account | How do component results combine, where are the bottlenecks, and what evidence supports each system claim? |

A literature study, numerical investigation, worked calculation, design alternative, tutorial or prototype can all advance these objectives. The model selection supplies a shared technical subject; the repository charters continue to protect member choice.

## 16. Shared boundaries

| Teams meeting at a boundary | What needs a common understanding |
|---|---|
| Architecture, ML models and ML compiler | Intended computation, numerical meaning, programming needs and workload assumptions |
| Compute and control | Accepted operations, operand timing, result behavior and conditions for progress |
| Memory and its consumers | Address units, data layout, ordering, response behavior, contention and initialization assumptions |
| Control and SoC | Configuration, command acceptance, execution visibility, completion and errors |
| SoC, ML compiler and FPGA | Host-visible behavior, reusable system logic and platform-specific adaptation |
| Verification and design teams | Intended behavior, what the evidence supports and what remains uncertain |
| Physical design and RTL teams | Clock/reset assumptions, technology constraints, physical costs and interpreted feedback |
| Accelerator and all teams | Compatible system assumptions, configuration context and the meaning of a combined result |

Architecture stewards shared definitions in collaboration with the teams that implement and use them. An exploratory proposal can challenge an existing definition. Its status should be clear so consumers can distinguish an experiment from behavior they can rely on.

A coupled source module can stay in one authoritative location while its boundaries are being understood. The organization should guide design ownership without encouraging duplicate implementations or forcing a premature decomposition.

The existing example has this dependency path:

```text
architecture contract
    -> ml-models reference and vectors
    -> rtl-compute arithmetic
    -> verification independent checks

accelerator coordinates this example across sibling repositories
```

This path illustrates collaboration. It is not a final accelerator block diagram or a required next project.

## 17. Decisions still open

The following are shared planning questions. The listed teams are participants in the discussion, not assignees for a predefined task.

| Decision | Question to resolve | Relevant perspectives | A useful decision would clarify |
|---|---|---|---|
| Supported system scope | Adopt text prefill/decode as the first demonstration scope, or include a specific extension? | Architecture, ML models, ML compiler, system integration | A complete computational path and explicitly scoped host fallback |
| Meaning of success | What would a convincing engineering or learning result demonstrate? | Participating teams together | Correctness expectations, useful observations and the limits of the intended claim |
| Numerical behavior | INT4 or which FP4 format, with which scales, activation, KV and recurrent-state policies? | ML models, architecture, compute, verification | A quality/cost comparison and a bit-defined selected policy |
| Execution and data contracts | What must software and hardware assume about commands, data and progress? | Architecture, ML compiler, control, memory, SoC | Shared semantics and the assumptions left open for exploration |
| Resource envelope | Which tools, hardware, technology resources and member availability are actually accessible? | FPGA, physical design, leads and participating members | Real constraints that can inform the scale of proposed work |
| Reference reuse | Which existing source or research results should inform the new project? | The relevant source-owning teams and verification | Provenance, understood dependencies and the evidence needed to reuse a result |
| Shared evidence | Which combination of studies or demonstrations would help teams learn together next? | System integration and interested teams | An agreed question and interpretation of results, with member-chosen methods |

The model and four-bit direction are settled. The comparison scenarios make the remaining questions concrete without fixing their answers. The current MAC's INT8 precision, a particular board, a PDK, a bus protocol and a command encoding should not silently become project decisions merely because an example or reference uses them.

No project-wide deadline, resource allocation or full-system performance target is assumed in this draft.

## 18. A direction for progress

The plan can describe desired maturity without prescribing each member’s work. The following outcomes can develop in parallel and be revisited as the project learns.

| Desired outcome | Why it matters | Possible evidence |
|---|---|---|
| A shared purpose | Teams understand what they are contributing toward | Workload studies, agreed scope and a clear explanation of intended value |
| Compatible assumptions | Independent work can connect without hidden disagreements | Reviewed semantics, worked examples and resolved interface ambiguities |
| Defensible component knowledge | Local design claims are understandable and useful | Research comparisons, numerical studies, prototypes, reasoning and implementation evidence |
| Combined-system understanding | The group learns from interactions across components | Integration studies, representative scenarios and interpreted system measurements |
| Physical feasibility | Platform and implementation choices are grounded in reality | Board studies, technology investigations and measured results with explicit constraints |
| Durable learning | New members can understand and extend what has been learned | Design narratives, experiment context, teaching material and clear limitations |

These outcomes are not mandatory phases or a fixed delivery schedule. Teams can propose a shared demonstration once its purpose is understood, then choose how their interests connect to it. An investigation that rules out a design or exposes an unsupported assumption is useful progress.

The immediate technical focus is to establish a reproducible Qwen text reference, compare INT4 and FP4 numerical policies, and ground the memory/compute envelope in available resources. Teams can contribute studies, measurements, implementation or learning material to those outcomes. The plan describes why those outcomes matter while leaving the work to the members.

## 19. How members and leads use the plan

Members can use a charter objective to explain why a question interests them, then choose an appropriate contribution. The form might be a literature study, calculation, design proposal, experiment, implementation, investigation, tutorial or collaborative review.

Leads help make the purpose and available context accessible. They connect related interests, support learning and communicate cross-team needs. When work affects a shared interface or commitment, the affected teams discuss that change together.

Progress discussions can focus on what was learned, why it matters, what supports the conclusion and what remains uncertain. The plan does not impose ticket counts, output quotas or a single definition of a worthwhile contribution.

The expected repository structure supports these choices:

```text
team-repository/
  README.md        purpose and entry point
  CHARTER.md       mandate, boundaries and member autonomy
  OBJECTIVES.md    durable outcomes
  SETUP.md         optional example setup and scope
  research/       studies, literature and comparisons
  docs/           design explanations and learning material
  experiments/    exploration and interpreted results
  domain folders  RTL, software, tests or flows when useful
```

A directory is an available place for work, not a request to fill it. Teams may adapt the structure as their contributions develop.

## 20. Team charter library

The full charters and objectives below are included for convenient reading. They are a snapshot of the repository documents at the recorded revisions, written before this Qwen technical baseline was selected. Their general mandate remains useful; the target-specific direction is in the technical chapters and team map above. Each team's repository remains authoritative for its own charter when the two diverge. This planning revision does not rewrite the published charter snapshot.

{{TEAM_CHARTERS}}

## 21. Evidence and keeping the plan current

This plan distinguishes checkpoint facts, project decisions, supplied implementation evidence, calculated scenarios, open questions and recommendations for discussion. A proposal should retain its status until the affected teams adopt it. A successful example should retain the limits of the behavior it tested.

### Technical sources and reproducible calculations

Model facts are pinned to the [Qwen3.5-2B checkpoint revision](https://huggingface.co/Qwen/Qwen3.5-2B/tree/15852e8c16360a2fea060d615a32b45270f8a8fc). The [source inventory](sources/README.md) records what was inspected and what was not executed. The Transformers implementation was inspected at a recorded commit; it is a semantic reference, not an installed and validated runtime environment.

The [budget calculator](model_budget.py) derives parameters, matrix work, storage, state, KV and traffic from the saved configuration and tensor header. The [JSON results](model-budget.json) retain exact values and assumptions. Rebuilding the document regenerates the numerical tables without a network call. The calculations reconcile all 632 stored tensor shapes with the checkpoint metadata total, then select the text decoder and explicitly account for tied output weights.

Format and algorithm discussions link primary sources where used: OCP for MXFP4, NVIDIA for NVFP4, the Gated Delta Networks paper, FlashAttention, GQA, AWQ and GPTQ. Recommendations and bottleneck comparisons in this document are project analysis derived from those semantics and the recorded assumptions. They are not measurements reported by those sources.

### Repository evidence

The initial repository publication was checked for private visibility, exactly one commit per repository and the configured project author. Fresh GitHub clones matched the reviewed source files and passed the MAC example. Repository descriptions were subsequently edited without changing the commits.

{{SNAPSHOT_TABLE}}

The [published repository index](https://github.com/SiliconBadgers/accelerator/blob/main/docs/REPOSITORIES.md), [team guide](https://github.com/SiliconBadgers/accelerator/blob/main/docs/TEAM_GUIDE.md) and [example validation](https://github.com/SiliconBadgers/accelerator/blob/main/docs/VALIDATION.md) provide the shared source material. The companion `repository-snapshot.json` records this document’s repository check.

This master plan lives in the private [SiliconBadgers planning repository](https://github.com/SiliconBadgers/planning), alongside its editable sources, calculations and pinned charter snapshots. The Markdown is the complete readable export, and the HTML is its browsable reading view. A fresh clone can rebuild both using Python without sibling repositories or network access. Running the builder updates local generated files; sharing a revision uses an ordinary reviewed Git commit and push.

The next revision should record the accepted quantization policy, evaluation thresholds and resource envelope, then attach measured evidence as teams produce it. A later model change should update the pinned configuration, tensor inventory, formulas and relevant contracts together. Calculated limits remain calculations until a complete measured result supports a stronger claim.
