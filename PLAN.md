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

## 04. Qwen baseline and exact scope

**Locked target:** the Qwen 3.5 through 3.7 family at approximately two billion parameters, with four-bit weights. The concrete checkpoint for this revision is **Qwen/Qwen3.5-2B**, pinned to revision `15852e8c16360a2fea060d615a32b45270f8a8fc`. This gives experiments a reproducible target. The [official checkpoint](https://huggingface.co/Qwen/Qwen3.5-2B/tree/15852e8c16360a2fea060d615a32b45270f8a8fc) supplies the configuration, tokenizer, template and weights.

The official Qwen model catalog checked on September 10, 2026 exposed Qwen3.6 at 27B and 35B-A3B, and no Qwen3.7 checkpoint in that author's matching results. No approximately 2B Qwen3.6 or Qwen3.7 checkpoint was verified. A later small checkpoint can become a new baseline after a configuration, operator and numerical comparison. A cloud model name does not establish available weights or hardware compatibility. The bounded lookup is recorded in [version-survey.json](sources/version-survey.json), with links to the official queries.

**Working scope for the first system study:** text input and text generation using the post-trained decoder, one ordinary autoregressive token at a time. Tokenization, chat formatting and sampling start on the host. Vision processing and multi-token prediction are extension studies. These scope choices make the initial budget concrete; they remain adjustable if the club chooses a broader demonstration. The source checkpoint includes vision and MTP tensors, so a text-only export must deliberately select the required tensors and preserve tied output weights.

**Evaluation scenarios:** batch one is the primary latency case; batch four and eight are concurrency studies. Use 2,048-token and 8,192-token contexts for initial comparisons, with 32,768 as a stress case. A scenario is a common measuring point, not a demonstrated capacity, promised speed or fixed product limit. The model's configured 262,144-token maximum is included only as a capacity comparison. Model support for a length does not establish that the accelerator can store or execute it.

### Configuration that changes the architecture

| Property | Pinned text configuration |
|---|---|
| Decoder | Dense, 24 layers, hidden width 2,048 |
| Layer pattern | Six repetitions of three Gated DeltaNet layers followed by one gated full-attention layer |
| MLP | SwiGLU, intermediate width 6,144 in every layer |
| DeltaNet | 16 query/key heads and 16 value heads, each dimension 128 |
| Short convolution | Depthwise causal convolution, kernel length four, on 6,144 projected Q/K/V channels |
| Full attention | Eight query heads, two key/value heads, head dimension 256 |
| Attention position encoding | Partial RoPE on 64 dimensions of each 256-dimensional head |
| Vocabulary and output | 248,320 padded entries; embedding and LM output weights are tied |
| Reference precision | BF16 stored weights for most tensors; some FP32 tensors and FP32 recurrent-state configuration |

These are checkpoint facts, verified against the [pinned configuration](https://huggingface.co/Qwen/Qwen3.5-2B/blob/15852e8c16360a2fea060d615a32b45270f8a8fc/config.json). In particular, this 2B model has a dense MLP. MoE routing, expert placement and expert caching do not belong in its baseline datapath.

### What the two-billion-parameter label contains

The checkpoint header contains 2,274,069,824 stored parameters: 1,881,825,088 under the language decoder, 331,416,576 under vision, and 60,828,160 under MTP. The text decoder's tied output matrix has no additional duplicate stored tensor. We inspected the 76,648-byte safetensors header using bounded HTTP requests; weight values were not downloaded or executed. [Pinned tensor file](https://huggingface.co/Qwen/Qwen3.5-2B/blob/15852e8c16360a2fea060d615a32b45270f8a8fc/model.safetensors-00001-of-00001.safetensors).

| Text component | Parameters | Dense GMAC per decoded token |
|---|---|---|
| All 24 SwiGLU MLPs | 905,969,664 | 0.9060 |
| 18 DeltaNet projection sets, including a/b | 378,667,008 | 0.3787 |
| Six gated full-attention projection sets | 88,080,384 | 0.0881 |
| Tied embedding / vocabulary output | 508,559,360 | 0.5086 |
| Convolution, norms and scalar parameters | 548,672 | Counted separately |
| Text decoder total | 1,881,825,088 | 1.8813 (matrix products only) |

The dense work column is our calculation from tensor shapes. It counts one multiply-accumulate as one MAC, including one full vocabulary projection for each decoded token. Input embedding is a row lookup. Attention over cached tokens, state recurrence, convolution, normalization and nonlinear functions require additional work. The large output matrix is about 27% of the dense matrix work at batch one. A design study that models only the MLP and attention projections misses a substantial cost.

The [local tensor inventory](sources/qwen35-2b-tensors.json), [calculation source](model_budget.py) and [exact budget data](model-budget.json) make these numbers reproducible. They establish dimensions and analytical budgets, not quantized model quality or functioning inference.

## 05. Four-bit numerical strategy

**Project direction:** four-bit weight storage and transfer. **Open selection:** INT4 or a specifically defined FP4 format. **Recommended first comparison:** INT4 weight-only quantization with BF16 activations versus MXFP4 and NVFP4 weight-only equivalents, followed by selective activation quantization. Starting with weight-only comparisons isolates weight error and establishes the traffic benefit before changing every arithmetic path.

An accelerator can store weights in four bits and unpack them into a wider compute format. That is a valid W4A16 design, even though the multipliers themselves are wider. Native low-bit multiplication is a separate performance and area choice. Every result must specify weight storage, activation representation, multiplication, accumulation, state and cache formats.

### INT4, MXFP4 and NVFP4 are different contracts

| Candidate | Numerical representation | Proposed comparison setup |
|---|---|---|
| Signed INT4 | Uniform signed integers with an explicit scale; optional zero-point only if selected | Symmetric, zero-point zero, group sizes 32, 64 and 128 along the reduction axis; BF16 scales |
| MXFP4 | E2M1 values with an E8M0 shared scale per 32 values | Standard block size and encoding; wider accumulation |
| NVFP4 | E2M1 values with an E4M3 scale per 16 values and an additional FP32 tensor scale | Match this two-level representation explicitly; wider accumulation |

The OCP definition specifies the [MXFP4 block and scale format](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf). NVIDIA describes [NVFP4's two levels of scaling](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/). E2M1's nonnegative values are 0, 0.5, 1, 1.5, 2, 3, 4 and 6, with signed encodings. Its spacing is nonuniform. A raw nibble labeled FP4 is insufficient to interpret a tensor.

For INT4, choose whether the quantizer uses all codes from -8 through 7 or a symmetric -7 through 7 subset. The RTL can decode every nibble while the export policy deliberately leaves one value unused. These choices change clipping, scale selection and extreme-product tests. Affine quantization can improve the fit for some distributions, but a nonzero zero-point introduces correction terms into dot products and adds metadata. It should earn that complexity through measured quality improvement.

Smaller groups adapt to local ranges and outliers, at the cost of more scales, scale fetches and boundaries inside a dot product. Power-of-two scales can simplify rescaling. Fractional scales may preserve distinctions that exponent-only scales lose. The meaningful comparison is a quality, storage, conversion and implementation-cost curve for this checkpoint. GPU vendor throughput figures do not predict FPGA or custom RTL efficiency.

### Storage including the scale cost

The table quantizes the large text matrices, including the tied embedding/output matrix. Small `a` and `b` gate projections, convolution, normalization and scalar parameters retain their stored BF16 or FP32 precision. It assumes dense packing, groups along each matrix row's reduction dimension, no zero-points and no extra layout copy. All relevant dimensions divide these group sizes exactly. NVFP4 includes one FP32 global scale per quantized tensor.

| Packing scenario | Bits per quantized value with block scale | Total GB | Total GiB |
|---|---|---|---|
| INT4, group 128, BF16 scale | 4.125 | 0.9729 | 0.9061 |
| INT4, group 64, BF16 scale | 4.250 | 1.0023 | 0.9334 |
| INT4, group 32, BF16 scale | 4.500 | 1.0610 | 0.9881 |
| MXFP4, group 32, E8M0 scale | 4.250 | 1.0023 | 0.9334 |
| NVFP4, group 16, E4M3 + tensor scale | 4.500 | 1.0610 | 0.9881 |

GB means one billion bytes; GiB means 2^30 bytes. These are calculated payload sizes, excluding alignment, allocator reserve, activations, state, caches, runtime metadata and executable storage. INT4 group 64 and MXFP4 happen to have the same storage overhead here because both consume one scale byte per 32 weight values. Their numerical behavior differs.

The pure four-bit text-weight lower bound is about 0.941 GB, while the proposed mixed-precision INT4 group-64 payload is about 1.002 GB. Keeping the entire tied embedding/output matrix in BF16 adds about 0.747 GB to that particular payload. That precision exception is large enough to change the memory-system choice. Small gate and norm exceptions are comparatively inexpensive.

### Activation, accumulation and state precision

| Tensor or operation | Reference / initial comparison | Next question |
|---|---|---|
| Large weights | BF16 reference; INT4 or scaled FP4 candidates | Which packing and scales preserve useful behavior? |
| Projection/MLP activations | BF16 first; W4A8 and W4A4 as separate candidates | Where do outliers and dynamic scaling dominate error or latency? |
| Integer dot accumulation | Defined integer partial sums, then scale and combine | What bound follows from the real reduction length and rescaling? |
| Floating dot accumulation | FP32 software reference | Can narrower accumulation meet the agreed error budget? |
| Residual stream and norms | BF16 stream with FP32 reference reductions | Which narrowing points change layer outputs materially? |
| Full-attention K/V cache | BF16 initial case | Does INT8 cache reduce traffic acceptably at long context? |
| DeltaNet recurrent state | FP32 reference; BF16 or BFP16 experimental state | How does persistent rounding change long-sequence behavior? |
| Gates, decay and exponentials | FP32 reference | What approximation preserves small updates and stable decay? |

A W4A8 integer path is not equivalent to dequantizing W4 weights and multiplying BF16 activations. A W4A4 design changes activation distributions and needs its own calibration and quality evidence. Four-bit recurrent state is especially speculative because its errors persist and interact with future updates. It is outside the initial numerical proposal.

For a conservative integer bound, signed INT4 by signed INT8 can produce a magnitude of 1,024. A 6,144-element dot therefore has an absolute bound of 6,291,456 before scaling; signed 24-bit accumulation covers that crude bound. INT4 by INT4 has a 64 product bound and 393,216 dot bound, requiring 20 signed bits. INT32 partial sums offer headroom, but arbitrary scale alignment, residual addition and bias can require wider intermediates. Group partial sums with different scales must be converted to a common numerical domain before they are combined. Summing raw integers across groups changes the result.

### How the numerical choice earns acceptance

Use the same model revision, tokenizer, prompts and held-out evaluation data for every candidate. Begin with a simple rounding baseline, then compare calibration-aware approaches such as [AWQ](https://arxiv.org/abs/2306.00978) and [GPTQ](https://arxiv.org/abs/2210.17323). Their papers establish useful methods to investigate; their reported results on other models do not establish quality for this hybrid decoder. Quantization-aware training is a later option if post-training approaches fail to meet the agreed quality boundary.

Report perplexity or token loss, logit error, top-k agreement, representative task accuracy, instruction behavior, and long-context stability alongside memory and latency. Calibrate on prompts and generated continuations so cached decode states are represented. Hold evaluation examples out of calibration. Compare per-layer and per-stage errors to locate the tensors that merit higher precision.

Choose an accepted quality threshold before selecting a winner from the evaluation set. No acceptable percentage loss has been invented in this draft. The evidence should show the tradeoff curve and confidence in its measurement, including outlier tasks and failure cases. A hardware result is bit-exact against a defined quantized oracle; model quality is judged against the original numerical reference using tolerances and task metrics.

## 06. Inference as a sequence of different workloads

The system processes a request through loading, prompt preparation, prefill, token selection, repeated decode and context release. Each stage stresses different resources. The architectural proposal is to share matrix arithmetic across stages while giving attention, recurrent state and scalar/vector work appropriate scheduling and storage.

```text
Pinned checkpoint -> offline quantization and tensor packing -> device weight memory

Host prompt + chat template -> token IDs -> embedding lookup
  -> repeat six times:
       three [norm -> DeltaNet mixer -> residual -> norm -> SwiGLU -> residual]
       one   [norm -> gated full attention -> residual -> norm -> SwiGLU -> residual]
  -> final norm -> tied vocabulary projection -> host token selection
  -> append token and repeat decode with per-request caches/state
```

This is a logical computation diagram. It does not require a dedicated hardware block for every box. The model's text layer order is established by its configuration; implementation reuse and scheduling remain design choices.

| Stage | Work and persistent data | Tradeoff that matters | Useful measurement |
|---|---|---|---|
| Offline export | Calibration, packing, scales and a model manifest | Quality versus metadata and supported arithmetic | Quality report; complete tensor coverage |
| Cold load | About one GB of packed text weights in the proposed case | Initialization time versus keeping weights resident between requests | Load time and peak memory |
| Prompt preparation | Tokenizer, template, position IDs, masks | Host work and repeatability | Tokenization time and exact token IDs |
| Prefill | Matrix-matrix products, causal attention, chunked or recurrent DeltaNet | Weight reuse versus intermediate/state capacity | Time to first token with prompt length |
| Decode | Matrix-vector products at batch one, KV reads, recurrent updates | Weight and context bandwidth versus compute utilization | Inter-token latency distribution |
| Token selection | Vocabulary projection, penalties and sampling | Full logits on host versus device filtering | Sampling latency and policy equivalence |
| Request lifecycle | Allocate, initialize, resume, cancel and release | Utilization versus isolation and predictable completion | Correctness under interruption and concurrency |

Time to first token includes queueing if reported end to end, plus preparation, any required load, prefill and first token selection. Report cold and warm conditions separately. Decode speed is the rate after prefill, with context length and concurrency recorded. Aggregate tokens per second can rise with batching while a single user's next token takes longer.

Thinking mode changes the generated token distribution and total sequence length. Use a fixed chat template and mode in each benchmark, and record generated tokens separately from prompt tokens. A comparison that changes reasoning mode or terminates outputs differently does not isolate hardware performance.

## 07. Prefill: reuse weights and manage the prompt

For a linear projection, write `Y[T,N] = X[T,K] W[K,N]`. With one prompt token, the weights support one vector product. With many prompt tokens, a fetched weight tile can serve many rows of X. Ignoring activation and result traffic, a four-bit weight tile reused for T rows offers roughly `2*T / 0.5 = 4*T` arithmetic operations per weight byte, where one MAC is two operations. Scale traffic and finite tiles reduce that ideal.

This makes a tiled matrix engine a natural prefill candidate. A large array can be productive when there are enough independent token rows. The practical tile depends on SRAM capacity, banking, reduction length, scale groups and the cost of moving partial sums. A tile shape chosen only from hidden width misses the very wide vocabulary output and the narrow per-head attention/state operations.

### Quantified prefill work

The dense count applies every layer matrix to every prompt token and computes vocabulary logits only for the last token. The full-attention count includes QK and probability-times-V products over the causal triangle: `L_full * Hq * D * T * (T+1)`. It excludes padded tile work, nonlinear operations and DeltaNet recurrence. A kernel that evaluates masked entries will execute more operations.

| Prompt tokens | Dense TMAC, last logits only | Causal full-attention TMAC | One naive score matrix MiB, one layer |
|---|---|---|---|
| 2,048 | 2.812 | 0.052 | 64 |
| 8,192 | 11.246 | 0.825 | 1,024 |
| 32,768 | 44.982 | 13.195 | 16,384 |

TMAC means 10^12 multiply-accumulates. The score column is the storage for a naive full `Hq*T*T` BF16 score tensor in just one full-attention layer, before any separate probability buffer. At 8K tokens that is one GiB per layer. Causal masking reduces useful work but does not automatically eliminate a dense allocation.

These calculations favor tiled attention that maintains running softmax statistics and avoids materializing the complete score/probability matrices. [FlashAttention](https://arxiv.org/abs/2205.14135) supplies the relevant IO-aware exact-attention approach. It preserves the mathematical attention operation while changing data movement; finite-precision accumulation order still needs comparison against the chosen reference. Its use does not remove the quadratic number of causal query/key interactions.

### Whole prompt versus chunks

Processing a large prompt at once improves weight reuse and gives the matrix engine more parallel work. It also reserves more activations and can monopolize memory bandwidth. Chunking bounds live activations and gives an interactive scheduler points to serve decode requests. It adds scheduling and state-management overhead and may require rereading weights more often.

A prefill chunk must see the correct earlier K/V entries in the six full-attention layers and the correct incoming DeltaNet and convolution state in the other layers. Chunk boundaries must not reset state, reuse padded tokens, or alter positions. Compare full-prompt execution and several chunk sizes on identical token streams. Numerical differences due to reassociation should be explained; a discontinuity at a chunk boundary is a correctness concern.

### DeltaNet prefill is a separate algorithm choice

A sequential recurrence reuses the decode engine and makes correctness easier to reason about, but serial dependence across prompt tokens limits parallelism. Chunkwise formulations transform much of the work into matrix operations while carrying state between chunks. That can fit the prefill matrix engine better, at the cost of intermediate buffers and a second numerical path. The [Gated Delta Networks paper](https://arxiv.org/abs/2412.06464) motivates this recurrent/chunkwise relationship.

A first prototype can use sequential DeltaNet prefill and report its limitation honestly. The architectural study should compare sequential, chunkwise and mixed implementations rather than extrapolating a decode kernel's latency into a prefill claim. Chunk sizes 64, 128 and 256 are proposed experiments, not a format requirement. Larger chunks need more temporary storage and can amplify differences in finite-precision reduction order.

The useful outcome is an explanation of where prompt time goes: dense arithmetic, attention, state processing, weight rereads, activation spills or host overhead. A single aggregate prefill tokens-per-second number cannot select a dataflow by itself.

## 08. Decode: bandwidth, utilization and latency

At batch one, each new token uses almost all dense text weights again. Unless a substantial fraction is retained on chip across steps, the design streams approximately one GB per token in the proposed packing. Adding MACs helps only while arithmetic is limiting. When weight transfer dominates, useful optimizations include packing, effective burst access, overlapping transfers, avoiding duplicate reads and batching compatible requests.

The ordinary output step is sequential: token selection determines the input to the next step. Layers also depend on previous layer outputs. Within a layer, projections and independent heads provide parallelism, and independent requests can share weight fetches. These opportunities do not make the whole decoder a single unrestricted parallel operation.

### A first-order latency model

```text
Per stage, optimistic time >= max(counted MACs / effective MAC rate,
                                 transferred bytes / effective bandwidth)

Whole decode step >= sum of dependent stage times
                     + exposed transfers + scalar/control/host overhead

An even looser system bound uses max(total compute time, total transfer time).
It cannot prove overlap, utilization, timing closure or achieved throughput.
```

Here effective means sustained useful work under the actual access pattern. A memory interface's advertised peak bandwidth is not the correct number when bursts are short, reads and writes contend, banks conflict, or the host shares the link. Measure achieved bandwidth with representative packed weights, scales, cache traffic and state transfers.

### Decode bandwidth scenarios

The following calculated ceiling assumes one request, INT4 group-64 weights, BF16 K/V, all FP32 recurrent state loaded and stored once per token through an on-chip scratchpad, and one read of the stored K/V cache. It adds the newly written K/V entry. Activations, convolution-state movement, command traffic, alignment, refresh, bank conflicts and host traffic are omitted. GQA head reuse must prevent repeated external reads for this assumption to hold. These are optimistic upper bounds under these traffic assumptions, not expected device speeds.

| Context | Modeled GB per decoded token | 10 GB/s upper bound tok/s | 25 GB/s upper bound tok/s | 50 GB/s upper bound tok/s |
|---|---|---|---|---|
| 2,048 | 1.065 | 9.4 | 23.5 | 46.9 |
| 8,192 | 1.141 | 8.8 | 21.9 | 43.8 |
| 32,768 | 1.443 | 6.9 | 17.3 | 34.7 |

At 8K context, sustaining an illustrative 20 tokens/s requires about **22.8 GB/s effective bandwidth** for this modeled traffic alone. Twenty tokens/s is a scenario inherited from the earlier exploration, not an accepted club target. Placing recurrent state on chip removes about 37.7 MB per token in this FP32 scenario, while the weight stream remains about 1,002 MB. This comparison helps prioritize architecture effort.

### Compute can still limit decode

At 8K context, counted matrix, QK/AV, recurrent-dot/outer-product and convolution work is about 2.097 GMAC per token. Nonlinear functions, normalization, state decay and other scalar operations add work beyond that count. The 20-token/s scenario therefore needs at least about 41.9 GMAC/s in the counted operations. At a hypothetical 500 MHz, that is roughly 84 useful MACs every cycle before overhead.

A 16-lane engine delivering one MAC per lane per cycle at 500 MHz peaks at 8 GMAC/s. If used for all counted arithmetic, it cannot satisfy that scenario even with unlimited memory bandwidth. A specialized 16-lane DeltaNet state engine can still be a sensible companion to a larger matrix engine. A quoted recurrence-only speed says little about full decoder throughput. None of these arithmetic examples establishes a realizable clock on a particular FPGA or process.

### Batching and keeping requests responsive

For B requests executed together, a weight tile can serve B activation rows. An idealized per-token weight contribution becomes `weight_bytes/B`, while each request retains its own K/V, recurrent and convolution state. At 8K context the initial cache/state reservation is about 114.844 MiB per request, or about 918.75 MiB for eight requests, before activations and allocator overhead.

Batching can turn small matrix-vector work into more efficient matrix-matrix work, but requests must wait for shared execution slots. Different context lengths cause uneven attention work. A scheduler can use bounded batches and chunked prefill to balance aggregate throughput and worst-case next-token latency. Report both metrics and include cancellation and short requests in the study.

Speculative decoding and MTP can reduce the number of expensive accepted-token steps, but they add candidate generation, verification and rollback. A DeltaNet state that has been advanced along a rejected branch cannot be repaired by shortening a KV pointer alone. It needs a saved state or replay from a valid state boundary. This makes speculation a valuable later cross-team question rather than an assumed baseline speedup.

## 09. Gated DeltaNet: persistent state and numerical stability

Each linear-attention layer projects the residual stream into Q, K, V, an output gate z, and two small per-head gate signals a and b. Q/K/V pass through the short causal convolution and SiLU. Q and K are L2-normalized; Q also receives head-dimension scaling. The recurrent core updates a key-by-value state matrix, then its output passes through a gated normalization and an output projection.

The following mathematical form uses column vectors and `S[key,value]`. It expresses the inspected [pinned Transformers recurrent implementation](https://github.com/huggingface/transformers/blob/5b7dcb0d36c242d8d85920a81c564ef3a86ca6dd/src/transformers/models/qwen3_5/modeling_qwen3_5.py), with conversion and rounding boundaries left to the numerical contract.

```text
q = L2_normalize(conv_silu(Q)) / sqrt(128)
k = L2_normalize(conv_silu(K))
v = conv_silu(V)
beta = sigmoid(b)
log_decay = -exp(A_log) * softplus(a + dt_bias)
alpha = exp(log_decay)

S_decay = alpha * S_previous
prediction = transpose(S_decay) * k
delta = beta * (v - prediction)
S_new = S_decay + outer(k, delta)
core_output = transpose(S_new) * q
```

The output uses the updated state. Applying the decay after the prediction, taking the readout from the old state, transposing the outer product, or omitting Q scaling changes the model. Zero initialization is required for a new sequence, while continuing a sequence requires all its relevant prior state. The mathematical norm includes an epsilon in the implementation; a hardware reciprocal-square-root must reproduce the selected handling of tiny inputs.

### Storage and traffic

One head holds `128*128 = 16,384` state values. At FP32 that is 64 KiB; at 16 bits it is 32 KiB. Across 16 heads and 18 layers, one sequence requires **18 MiB FP32 state** or **9 MiB 16-bit state**. This capacity is independent of context length. It scales with concurrent sequences and any speculative or prefix snapshots.

The convolution adds history. Reserving four BF16 slots for each of 6,144 channels in all 18 layers requires 864 KiB, or 0.84375 MiB per sequence. A custom streaming implementation could retain three prior samples and combine them with the current sample, but a four-slot cache layout is the budgeted convention. The contract must say whether a snapshot includes three historical slots or an already-updated four-slot buffer.

| State placement | Advantage | Cost or constraint |
|---|---|---|
| All layers and heads on chip | Avoids external recurrent-state traffic between tokens | 9 or 18 MiB per sequence plus ports, control and physical overhead |
| One head in a local scratchpad | Small active storage and reusable lanes | Load/store every head each token; context traffic and scheduling |
| Several heads or a layer resident | More overlap and fewer transfers for selected state | Larger SRAM; benefit depends on scheduling and available capacity |
| State streamed directly from external memory | Minimal local capacity | Repeated passes can multiply external traffic and expose latency |

For a scratchpad that loads old state once and stores new state once, total external state traffic is 18 MiB/token at 16 bits or 36 MiB/token at FP32. This assumes intermediate passes stay local. A two-pass engine often performs two local reads and one local write per state element, so local SRAM traffic and port requirements exceed external load/store traffic.

### How to use the existing source exploration

The earlier [Qwen ASIC architecture exploration](https://github.com/abhinavnandwani/qwen-asic/blob/78d0fafde2d2f3a4094f8c7422fc76fb09ca4bbe/docs/ARCHITECTURE.md) describes a 16-lane, one-head-at-a-time, 16-bit state engine. Its analytical schedule is 1,024 cycles for prediction, eight for delta formation, 1,024 for update/readout and eight overhead, giving 2,064 cycles per head. Across 288 layer/head instances this is 594,432 recurrence cycles per token. Recomputing decayed state during the second pass avoids an intermediate state buffer.

At the source's hypothetical 500 MHz, this arithmetic gives about 841 recurrence-only steps/s with resident state. It excludes Q/K/V and gate projections, convolution, normalization, full attention, MLP, vocabulary output and system stalls. Its 32-KiB active head storage assumes 16-bit state; FP32 doubles it. Its BFP16 state, INT8 Q/K/V and fixed-point gates are experimental numerical choices, not the checkpoint's native computation or the new project's selected four-bit contract. The source's [model specification at that revision](https://github.com/abhinavnandwani/qwen-asic/blob/78d0fafde2d2f3a4094f8c7422fc76fb09ca4bbe/model/spec.toml) records that earlier INT8 exploration.

The two-pass schedule also needs a real SRAM port plan. The update phase reads old words and writes new ones. A single-port bank may serialize those operations unless bank ping-pong, separate read/write storage or a different schedule is provided. A bank count alone does not establish read/write throughput. Physical-design and FPGA studies should include the actual memory primitive and its latency.

### Precision questions unique to a recurrence

Persistent state error can accumulate, decay or change future updates. A low-precision state that looks acceptable after one token may lose small updates after thousands of steps. Conversely, using one exponent for a whole head may preserve range while discarding low-magnitude components. BF16, FP16 and BFP16 have different precision and overflow behavior despite all consuming two bytes per element.

Study per-head exponent selection, headroom, update rounding and rebase policy separately. If the exponent changes, every stored mantissa must retain its represented value under the specified rescaling. Saturating and rebasing after lost information cannot reconstruct the value that was clipped. Record clipping counts, update-to-state ratios, drift against FP32, and end-to-end quality at multiple lengths.

A useful first evidence chain compares one recurrence step, many repeated steps, complete DeltaNet layers, and the mixed 24-layer decoder. Include near-zero keys, strong and weak decay, nearly saturated beta, changing gate scales, cancellation in `v - prediction`, head independence, padding and chunk-boundary continuity. These are proposed questions for the responsible teams to explore through models, proofs, experiments or implementations.

## 10. Full attention: six layers still grow with context

This checkpoint uses grouped-query attention: four query heads share each of the two K/V heads. The stored cache therefore uses two heads, while QK and AV computation still serves eight query heads. The [GQA paper](https://arxiv.org/abs/2305.13245) explains the general sharing design; the head counts here come from the pinned checkpoint.

The query projection produces both queries and an output gate, giving 4,096 projected values rather than 2,048. Q and K receive per-head RMS normalization and partial RoPE before attention. After softmax-weighted V aggregation, a sigmoid gate modulates the attention output before the output projection. These details are visible in the [checkpoint's reference implementation](https://github.com/huggingface/transformers/blob/5b7dcb0d36c242d8d85920a81c564ef3a86ca6dd/src/transformers/models/qwen3_5/modeling_qwen3_5.py).

### Capacity, arithmetic and reuse

```text
BF16 KV bytes per cached token across all full-attention layers
  = 6 layers * 2 (K and V) * 2 KV heads * 256 dimensions * 2 bytes
  = 12,288 bytes = 12 KiB

Decode QK + AV MACs at context T
  = 6 * 2 products * 8 query heads * 256 dimensions * T
  = 24,576 * T
```

At 8K context the cache is 96 MiB and QK/AV require about 0.201 GMAC per new token. At 32K they become 384 MiB and about 0.805 GMAC. The recurrent layers prevent all 24 layers from accumulating a full KV history, but do not make the full model's decode time or memory independent of context.

Schedule the four query heads sharing a KV head so a loaded K/V tile can be reused locally. Expanding the two stored heads into eight physical copies would erase much of GQA's memory benefit. Layout choices should make vector segments and sequence tiles contiguous enough for bursts while matching bank access during dot products.

### Softmax and long-context numerics

Stable softmax subtracts a running or row maximum before exponentiation, then normalizes by a sum. Tiled execution can maintain a running maximum, normalization total and weighted output rather than storing the whole probability vector. It requires rescaling earlier partial results when the maximum increases. The approximation budget must include exponential evaluation, reductions, reciprocal and accumulator range.

Large contexts produce more terms in the denominator and weighted-value sum. A fixed-point implementation needs evidence for underflow of small probabilities, saturation and nearly tied logits. The initial study should keep Q/K dot products, softmax statistics and AV accumulation wide enough to establish a reliable reference before narrowing them. INT4 weights do not imply INT4 attention probabilities.

RoPE rotates only the configured fraction of each head. Text positions must match the processor's convention even though the checkpoint also supports multimodal positions. Precomputed tables trade storage and transfers for local trigonometric work; recurrences or approximations trade those resources for phase error. Select a design against the intended context range and validate high positions, not just the first few tokens.

### Cache compression and lifecycle

INT8 K/V can approximately halve payload storage, but scales, grouping and possible higher-precision tails reduce the saving. K and V may need different policies: K error changes attention weights; V error changes the weighted result. Compare per-head, per-channel and per-token groups with long-context quality and conversion cost. Four-bit KV is a later experiment, independent of four-bit weights.

Contiguous caches simplify address generation and DMA. Paged caches reduce fragmentation and support requests of different lengths, at the cost of page tables, more address logic and potentially shorter transfers. Pick the initial layout from the concurrency and memory envelope; paged allocation is not required merely because larger serving systems use it.

Prefix reuse must preserve token IDs, positions, model revision, quantization settings, all six KV histories, and corresponding DeltaNet/convolution state. A recurrent snapshot represents one exact prefix boundary. It cannot be sliced into arbitrary earlier prefixes the way a KV tensor can. Cancellation, resumption and speculative rollback therefore require an explicit context-state protocol.

## 11. Dense layers, normalization and output selection

### SwiGLU dominates much of the dense work

Every decoder layer computes `down(SiLU(gate(x)) * up(x))` with two 2,048-to-6,144 projections and one 6,144-to-2,048 projection. The 24 MLPs account for about 0.906 GMAC per decoded token. A fused gate/up schedule can reuse the input activation tile, apply SiLU and multiplication locally, then pass an intermediate tile into the down projection.

Fusion reduces activation writes and reads, but it ties together tile shapes, buffer lifetimes and scale conversions. If gate/up tiles arrive in a different order from down-projection consumption, retained partial sums can become the dominant scratchpad demand. Compare full-intermediate materialization, tiled fusion and recomputation using actual tensor dimensions. For a 128-token prefill tile, one BF16 `[128,6144]` intermediate is 1.5 MiB; retaining gate, up and product separately triples that before other buffers.

MLP activation distributions can contain outliers after the gate and elementwise product. A four-bit activation policy that works at the normalized layer input may fail at this intermediate. Test where to place quantization, how often to compute dynamic scales, and whether keeping the intermediate wider gives a better quality/cost balance than more elaborate calibration.

### Norms and nonlinear functions are small but frequent

RMSNorm, SiLU, sigmoid, softplus, exponential, reciprocal and reciprocal-square-root operate on fewer values than the matrix engine. Their pipeline stalls and conversion traffic can still dominate a small design with a fast matrix unit. A shared vector unit is a useful candidate if its latency, buffering and scheduling fit all consumers. Host execution is useful for an early hybrid prototype, but device/host transfers must be included in the system timing.

There are distinct normalization conventions in this model. Decoder and attention Q/K RMSNorm use a stored zero-centered weight with an effective multiplier of `1 + weight`; DeltaNet's gated norm uses its own weight and a SiLU gate. An exporter that applies a generic learned RMSNorm weight to every norm silently changes outputs. Preserve these operator semantics in the model manifest and golden reference. [Pinned normalization code](https://github.com/huggingface/transformers/blob/5b7dcb0d36c242d8d85920a81c564ef3a86ca6dd/src/transformers/models/qwen3_5/modeling_qwen3_5.py).

For lookup tables, record the input range, table spacing, interpolation, clipping and worst observed error on model activations. Polynomial approximations need coefficient precision, range reduction and intermediate-width definitions. Count latency and area with those numerical choices. A table-size comparison without approximation quality is incomplete.

### The tied output projection deserves explicit treatment

The same 248,320-by-2,048 matrix provides an input embedding row and a full vocabulary projection at the output. Tying avoids a second weight copy, but every ordinary decode step still performs about 0.509 GMAC to produce all logits. Prefill for generation usually needs logits at the last prompt position only. Prompt log-probabilities or training-style evaluation require more positions and must use a different budget.

A quantized export must use a coherent representation of this shared matrix for both roles, or explicitly account for a second layout or higher-precision copy. Embedding lookup and output GEMV favor different access patterns. Logical tying alone does not guarantee physical sharing if the exporter creates two incompatible packed layouts.

Full FP32 logits consume about 0.993 MB per request step. Returning them to the host is much smaller than streaming all weights, but synchronization and sampling latency can still matter. Device argmax can reduce transfers for greedy generation. Device top-k can help a top-k policy; truncating to a fixed k does not in general preserve exact top-p sampling. Repetition or presence penalties, banned-token masks, temperature and the random seed must match the selected policy.

Reduced or shortlist vocabularies change model behavior unless they implement a justified exact optimization for the chosen policy. They are research directions with quality consequences. The baseline uses the checkpoint's vocabulary and records how padded or special tokens are handled by the tokenizer and generation configuration.

## 12. Memory hierarchy and the system resource envelope

The initial data placement proposal uses external memory for packed weights, a local tiled working set for compute, and explicitly managed per-request caches/state. Whether recurrent state fits on chip depends on the board or ASIC SRAM envelope and the desired number of active requests. About one GB of weights is beyond a small all-SRAM accelerator concept, so the system study must include a real off-chip memory path or an explicitly measured host-streaming path.

### Per-request cache and state capacity

The totals below include BF16 KV, FP32 recurrent state and the reserved four-slot BF16 convolution cache. The last column is an alternative recurrent-state component, not an additional allocation. Switching to 16-bit state saves nine MiB per request. Weight buffers, activation tiles, scores, queues, alignment and allocation overhead are excluded.

| Context tokens | BF16 KV MiB | FP32 recurrent MiB | Total sequence MiB, including conv | 16-bit recurrent alternative MiB |
|---|---|---|---|---|
| 2,048 | 24 | 18 | 42.844 | 9 |
| 8,192 | 96 | 18 | 114.844 | 9 |
| 32,768 | 384 | 18 | 402.844 | 9 |
| 262,144 | 3,072 | 18 | 3,090.844 | 9 |

At 8K context and batch one, the proposed INT4 payload plus these caches/state consumes about 1.123 GB, or 1.046 GiB, before working buffers. A platform with only one GiB available to the accelerator cannot hold that scenario as specified. At eight concurrent 8K requests, caches/state alone approach 0.9 GiB, in addition to shared weights. The configured 262K context would need about three GiB of BF16 KV per request even though most layers are recurrent.

### What deserves SRAM

| Candidate resident data | Reason to retain it | What competes for the same capacity |
|---|---|---|
| Weight tiles and scales | Regular bursts and overlap with matrix arithmetic | Double buffers and multi-request reuse |
| Input/partial-sum tiles | Avoid repeated activation transfers and wide accumulator spills | Larger prefill tiles and fused MLP intermediates |
| Recurrent state | Remove repeated external state load/store | 9 or 18 MiB per active request if fully resident |
| K/V sequence tiles | Reuse across grouped query heads | Long contexts and softmax running statistics |
| Gate/norm/vector buffers | Decouple units with different throughput | Small capacity but potentially many access ports |

Choose residency using bytes avoided per useful operation and the schedule that actually reuses the data. Allocating a large array of SRAM to recurrent state could still be the right choice for energy or latency, but the bandwidth table shows why it does not solve the dominant weight stream by itself. Energy must be measured or estimated from an identified technology and memory implementation; this document supplies no universal pJ/access number.

### Platform and memory tradeoffs

External DDR can fit a modest platform and tool flow if its measured bandwidth supports the desired scenario. HBM provides a potential wider interface and more channels, with a different board, integration and cost envelope. Host-streamed weights simplify some prototypes but put the host link on every token's critical path. These are architectural alternatives; a particular board, cloud instance, PHY or memory product has not been selected here.

An FPGA prototype can measure command overhead, bank access, stalls and representative throughput even if the eventual ASIC uses another memory technology. An ASIC feasibility study must include usable SRAM macros, port counts, access times, clock distribution, interconnect, timing corners and area for the complete selected scope. Register arrays in a simulation are not evidence that an equivalent physical SRAM exists.

Use a common scenario sheet for both: usable capacity, sustained reads/writes under contention, clock that closes timing, power boundary, host interface and tested workload. The earlier source's 500 MHz, SKY130/GF180 and board assumptions are reference-study inputs. Their appearance in that source does not make them compatible or accepted project constraints.

### Dataflow candidates

A weight-stationary schedule retains weights across prompt or batch rows; it benefits from reuse but consumes storage and can leave lanes idle in batch-one decode. An output-stationary schedule retains partial sums while streaming reduction tiles; it saves accumulator traffic but must align scale groups and handle long reductions. A vector engine can map narrow or irregular stages efficiently but needs enough aggregate lanes for the dense workload. A matrix engine plus shared vector/state units offers specialization with extra queues and integration effort.

Evaluate these choices using the same tensor traces and resource envelope. Include unpacking, scale multiplication, partial-sum storage, SRAM ports and utilization. A raw multiplier-count comparison leaves out much of what makes a four-bit accelerator useful.

## 13. Hardware/software contracts and block responsibilities

The baseline suggests a logical system with a host interface, command and completion queues, execution control, external-memory transfers, banked local storage, a tiled matrix engine, vector/nonlinear arithmetic, and attention/DeltaNet state paths. This is a set of responsibilities. Teams can combine or split implementations when evidence supports the choice.

### Keep control and SoC distinct

`rtl-control` owns how accepted operations make progress: dependencies, resource arbitration, in-flight work, context selection, stalls, completion and recoverable errors. `soc` owns the composed hardware and host-visible integration: addressing, bus attachment, clock/reset domains, memory controllers and the observable system interface. Compute owns arithmetic behavior; memory owns storage and transfer behavior. A control microarchitecture should not implicitly determine the platform bus or external memory technology.

`ml-compiler` owns the path from the model's operators into a packed, executable schedule and the runtime's submission needs. `architecture` stewards shared semantics with all consumers. The question is what software must express and hardware must guarantee. A large instruction set is not a prerequisite for answering that question.

### Model artifact contract

Every export should identify the source checkpoint and revision, tokenizer/template hashes, selected text/vision/MTP scope, operator graph and tensor manifest. Each tensor records logical dimensions, stored layout, transposition, padding, quantization axis, group size, code interpretation, scales, zero-points if any, and offsets. Include checksums so runtime loading can detect a mismatched or incomplete artifact.

A reasonable INT4 experiment packs two consecutive reduction-axis values per byte, with the earlier value in the low nibble and signed two's-complement interpretation. Keep the scale array separately addressable and index groups explicitly. This is a proposed convention for review, not an existing public ABI. FP4 experiments need their own format identifiers and scale layout. Padding values must decode to numerical zero and must never contaminate a partial reduction or softmax mask.

### Operations and scheduling level

| Interface level | Benefit | Cost or constraint |
|---|---|---|
| Host submits every small operation | Fast path to a transparent prototype | High command and synchronization overhead |
| Host submits matrix/vector/state kernels | Reuse across layers; clear contract boundaries | Runtime must schedule dependencies and manage buffers |
| Device executes a layer or graph schedule | Lower submission overhead and better local overlap | More device control state and less immediate flexibility |

The initial programming study can compare these levels with representative command counts and host timing. Likely operation families include packed matrix multiplication, vector normalization/gating, tiled attention, DeltaNet state step/chunk, data movement and barriers. This list establishes computation that must be expressible; it does not freeze opcode numbers, tile dimensions or a compiler implementation.

Commands should identify format/configuration version, source and destination buffers, dimensions/strides, context identity, dependencies and an observable completion. The contract must say whether completion means operands were consumed, state was committed, outputs became visible, or all three. Queues need defined backpressure and error behavior so a stalled consumer cannot silently lose work.

### State is part of the programming model

A context owns the six KV caches, 18 recurrent matrices per head set, convolution history, current position and generation state. Initialize it before accepting dependent work. Reuse a context only after outstanding operations and DMA are complete. Define save/restore and invalidation at an explicit token or chunk boundary, especially for cancellation or future speculation.

Scale changes, layout versions and quantized model revisions must not be mixed within a continuing context without a defined conversion. Memory allocation needs separate capacities for shared immutable weights and mutable per-request state. This division lets runtime, control, memory and SoC agree on isolation without forcing them into one repository.

### A complete experiment can contain host fallback

A prototype may offload only selected matrices or DeltaNet while other operations run in software. That is useful evidence if the report names the offloaded operators and includes host/device transfers, synchronization and software time. A full-model result requires the complete computational path and numerical validation, even when the accelerator's implementation scope is partial. Kernel-only timing remains separately useful.

## 14. Verification, evaluation and evidence gates

The technical plan needs three distinct references: the checkpoint in its intended software semantics, a deliberately quantized software model, and bit-defined hardware-facing kernels. Their roles differ. A mismatch against the checkpoint can be an intended approximation; a mismatch against the accepted bit-level hardware contract is an implementation defect.

### Outcomes that make a claim credible

| Evidence outcome | What it establishes | Examples of useful contributions |
|---|---|---|
| Reproducible text reference | The selected checkpoint, tokenizer and operator path are understood | Loader study, traced tensors, documented runtime versions and baseline outputs |
| Quantization comparison | The four-bit policy has a known quality/cost tradeoff | Calibration study, layer sensitivity, INT4/FP4 comparison, long-context analysis |
| Defined arithmetic and state | Independent implementations can agree on exact behavior | Numerical specification, worked examples, proofs of bounds, executable oracle |
| Component confidence | A block meets its accepted contract | Directed and randomized tests, formal properties, independent scoreboards |
| Complete sequence behavior | Prefill, cached decode and lifecycle connect correctly | Mixed-layer inference, chunk equivalence, context isolation, save/restore studies |
| System feasibility | Resources and performance are credible under stated constraints | Measured bandwidth, utilization, timing, capacity and end-to-end latency |
| Explained limitations | Readers understand what a result does not establish | Failure analysis, quality exceptions, missing operators and extrapolation limits |

These are standards for interpreting results, not assigned tasks or a fixed stage schedule. Teams may pursue different questions concurrently. A careful result showing why a candidate fails is useful evidence and can change the architecture.

### Numerical and structural cases worth covering

For packed weights, cover every nibble code, group boundaries, signed interpretation, zero blocks, the smallest/largest scales, rounding ties, clipping, padding and unsupported-format rejection. For integer arithmetic, include extreme reductions and scale-alignment overflow. For FP4, cover representable values, signed zero and the selected handling of non-finite source values and scale encodings. Tests must follow the accepted format rather than borrowing INT4 expectations.

For mixed attention, compare the complete 3:1 layer sequence and the exact query-gate split, Q/K norm, RoPE and residual ordering. For caching, compare whole-prompt and chunked prefill, token-at-a-time continuation, different batch compositions, padded requests and explicit context reuse. For recurrence, record intermediate state at chosen boundaries so a final-logit discrepancy can be localized.

For control and memory, include backpressure, delayed responses, arbitration, reset, cancellation with DMA in flight and independent concurrent contexts. Define which behavior is guaranteed before testing it. A waveform with no obvious failure is weaker evidence than a scoreboard or property tied to the intended semantics.

### Evaluation matrix and reporting

| Axis | Initial common cases | Why it matters |
|---|---|---|
| Sequence shape | Prompts of 128, 2K and 8K; 32K stress; decoded continuations long enough to examine state drift | Separates warm-up, prefill and persistent-state effects |
| Concurrency | B=1 primary; B=4 and B=8 studies if capacity permits | Exposes weight reuse, state growth and latency tradeoffs |
| Numerical candidates | BF16/FP32 reference; INT4 W4A16; MXFP4/NVFP4 comparisons; selective W4A8 | Separates sources of error and implementation cost |
| Generation policy | Fixed template, mode, seed and sampling parameters; greedy diagnostics | Makes runs interpretable without requiring all outputs to be text-identical |
| Quality | Held-out token loss, representative tasks, logit diagnostics and long-context behavior | Prevents selecting precision solely from microbenchmarks |
| Performance | Cold load, warm TTFT, inter-token p50/p95, aggregate throughput, bytes and utilization | Distinguishes latency, throughput and bandwidth limits |
| Physical evidence | Device/process, resource use, achieved clock, timing constraints and power boundary | Prevents treating an analytical clock as a measured result |

All records should contain the model/export revision, exact scope, numerical policy, runtime/tool versions, input token lengths, generated lengths and memory assumptions. A comparison should state whether memory and power are measured or estimated, and whether transfers and host time are included. Statistical variation and excluded failures belong in the report.

The published starter tests currently establish only the small INT8 MAC example described earlier. None of the Qwen quality evaluations, four-bit kernels, model runs or physical results described in this technical plan has been performed in the new repositories. The work in this revision is a researched target definition, audited shape inventory and reproducible analytical model.


## 15. Team and repository map

The RTL teams own hardware responsibilities. Architecture, machine-learning work, verification, FPGA, physical design and system integration span those blocks. This is a map of responsibility, not a management hierarchy.

| Repository | Charter focus | Supplied code |
|---|---|---|
| [architecture](#team-architecture) | Architecture and system direction | MAC example contributor |
| [rtl-compute](#team-rtl-compute) | Compute datapaths | MAC example contributor |
| [rtl-memory](#team-rtl-memory) | Memory and data movement | Documentation and scaffold |
| [rtl-control](#team-rtl-control) | Execution control and scheduling | Documentation and scaffold |
| [soc](#team-soc) | SoC composition and system interfaces | Documentation and scaffold |
| [ml-compiler](#team-ml-compiler) | ML compiler and runtime | Documentation and scaffold |
| [ml-models](#team-ml-models) | ML models, workloads and numerical methods | MAC example contributor |
| [verification](#team-verification) | Verification and confidence in the design | MAC example contributor |
| [fpga](#team-fpga) | FPGA prototyping and hardware exploration | Documentation and scaffold |
| [physical-design](#team-physical-design) | Physical implementation and design feasibility | Documentation and scaffold |
| [accelerator](#team-accelerator) | System integration and shared project understanding | MAC example contributor |

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

### Team: architecture

[Open repository](https://github.com/SiliconBadgers/architecture) | [Source charter](https://github.com/SiliconBadgers/architecture/blob/4e67ed3711179c1500c5109defbad96447dfc7be/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/architecture/blob/4e67ed3711179c1500c5109defbad96447dfc7be/OBJECTIVES.md)

#### Purpose

Help SiliconBadgers make coherent, evidence-based choices about the accelerator it is building. This team connects workload needs, numerical behavior, hardware organization and practical constraints so that separate teams can contribute to a system whose purpose and tradeoffs are understood.

Architecture gives shared meaning to work across the project. A locally effective compute block, memory system or software interface is useful when its assumptions fit the wider design. The team develops that common understanding and keeps alternatives and uncertainty visible as the project learns.

#### Responsibilities

##### System intent and tradeoffs

Develop and explain the relationship between intended workloads, capabilities, constraints and architectural choices. Maintain a system view that includes performance, storage, numerical behavior, programmability and implementation feasibility.

##### Shared semantics

Steward the definitions that cross team boundaries: operations, data representations, interfaces, memory behavior and externally visible execution rules. Separate agreed behavior from open proposals and illustrative examples.

##### Architectural reasoning

Use literature, analytical models, simulation, comparison studies and implementation feedback to examine alternatives. Document assumptions and explain where the available evidence supports a choice or leaves it uncertain.

##### Continuity of understanding

Maintain accessible design explanations and decision rationale so new members can understand why the system has its current shape and can challenge those choices constructively.

#### Boundaries and shared decisions

Architecture stewards shared specifications through discussion with the teams that implement and consume them. Compute, memory, control and SoC teams choose internal implementations within agreed boundaries. ml-models owns numerical references; ml-compiler owns software realization; accelerator maintains combined-system understanding and demonstrations. Architecture proposals become shared commitments through agreement with affected teams, not merely by appearing in this repository.

#### Member autonomy

Members may choose an architectural question, compare competing organizations, examine workload needs, build a performance model, investigate a numerical format or improve an explanation. The team can decide its research methods and internal organization. Changes to shared semantics, resource assumptions or project-wide objectives need discussion with affected teams. A study that rules out a design can be a valuable result.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| ml-models and ml-compiler | Workload characteristics, numerical expectations and programming needs inform the system specification; architecture returns explicit assumptions and shared semantics. |
| RTL teams | Exchange resource and timing assumptions, interface proposals and feedback from implementation. Treat mismatches as opportunities to revise the shared design. |
| fpga, physical-design and accelerator | Use platform constraints and measured system behavior to refine architectural claims and the interpretation of results. |

#### Possible directions

Possible questions include how data reuse changes a memory hierarchy, where performance estimates depend on scheduling, which numerical assumptions matter for a workload, or how to explain an execution model to a new member. These are invitations to choose a direction, with no required sequence or predetermined answer.

#### What progress means

Progress is visible when important assumptions become explicit, design choices can be explained, teams interpret shared behavior consistently and new evidence can change a decision. A well-supported comparison, a clarified contract or a reusable teaching note may be as valuable as a simulator.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/architecture/blob/4e67ed3711179c1500c5109defbad96447dfc7be/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/architecture/blob/4e67ed3711179c1500c5109defbad96447dfc7be/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/architecture/blob/4e67ed3711179c1500c5109defbad96447dfc7be/CHARTER.md) for scope and shared decision boundaries.

##### Coherent system purpose

Build a shared understanding of what the accelerator is intended to do and what constraints matter. Members choose how to investigate and communicate that purpose as the project evolves.

Evidence might include workload studies, capability descriptions, architectural diagrams or an explanation of how competing goals were reconciled.

##### Clear shared behavior

Make cross-team assumptions understandable and consistent while preserving room to explore implementations.

Evidence might include reviewed interface definitions, worked examples and the resolution of incompatible assumptions.

##### Defensible tradeoffs

Improve the quality of architectural decisions through explicit reasoning and evidence from the relevant teams.

Evidence might include alternative analyses, transparent estimates, experiments or decisions revised after measurement.

##### Durable architectural knowledge

Make the reasoning behind the design accessible enough that members can contribute, question assumptions and carry work forward.

Evidence might include design narratives, decision records or educational material that other teams find useful.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: rtl-compute

[Open repository](https://github.com/SiliconBadgers/rtl-compute) | [Source charter](https://github.com/SiliconBadgers/rtl-compute/blob/b25a309d4964b403fae2ab189d240eae47843a50/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/rtl-compute/blob/b25a309d4964b403fae2ab189d240eae47843a50/OBJECTIVES.md)

#### Purpose

Explore and develop the arithmetic capabilities that turn the accelerator’s intended computations into effective hardware. The team seeks a sound balance among numerical behavior, throughput, latency, area and implementation complexity, using approaches its members choose.

Compute is where numerical operations meet hardware organization. Useful contributions can explain an arithmetic choice, investigate a datapath organization, demonstrate an operator, measure a tradeoff or make an existing block easier to understand. The team’s mandate is broader than extending the existing MAC example.

#### Responsibilities

##### Arithmetic behavior and organization

Study and develop arithmetic operators, processing elements, vector or matrix datapaths and related transformations appropriate to the agreed workloads. Explain the relationship between numerical semantics and hardware behavior.

##### Local execution structure

Own the pipelines, local operand handling and datapath coordination that belong inside compute blocks. Make externally relevant latency, acceptance and result behavior understandable to consumers.

##### Compute tradeoffs

Investigate precision, parallelism, reuse, utilization and implementation cost. Distinguish analytical expectations, simulation observations and mapped hardware results.

##### Reusable understanding

Preserve explanations, experiments, local checks and implementation knowledge so members can compare approaches and build on one another’s work.

#### Boundaries and shared decisions

This team owns arithmetic implementation and its internal pipelines. rtl-control coordinates operations across blocks; rtl-memory owns storage and movement services; soc owns system composition. Architecture and ml-models help establish shared numerical semantics. Verification contributes independent correctness assessment, while physical-design and FPGA provide implementation feedback. A choice that changes visible timing or numerical behavior is discussed with the relevant consumers.

#### Member autonomy

Members choose operators or design questions that serve the charter and their interests. Research, numerical analysis, hardware experiments, educational examples and implementation work are all valid directions. Internal datapath choices belong to the team within agreed interfaces. The current signed MAC can support exploration, but it does not prescribe the team’s next block, final precision or architecture.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and ml-models | Exchange operation requirements, numerical assumptions and reference behavior so compute choices remain meaningful to the workload. |
| rtl-control and rtl-memory | Agree on operand availability, operation acceptance, result handling and the assumptions that affect scheduling or data movement. |
| verification, fpga and physical-design | Share behavior and constraints; use independent checks and implementation measurements to assess the strengths and limits of a design. |

#### Possible directions

Members might study numerical representations, compare pipeline organizations, investigate an activation or normalization operation, explain array utilization, build a small datapath or characterize an existing one. A compelling direction should connect to a charter objective; it need not produce a new production module.

#### What progress means

Progress means arithmetic behavior and its costs are better understood, useful compute capabilities become dependable, and consumers can reason about their use. Evidence can be a numerical comparison, a clear block explanation, a verified implementation or a measured tradeoff with stated assumptions.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/rtl-compute/blob/b25a309d4964b403fae2ab189d240eae47843a50/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/rtl-compute/blob/b25a309d4964b403fae2ab189d240eae47843a50/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/rtl-compute/blob/b25a309d4964b403fae2ab189d240eae47843a50/CHARTER.md) for scope and shared decision boundaries.

##### Useful arithmetic capability

Develop a body of compute knowledge and hardware capabilities relevant to the project’s workloads, with members choosing which capabilities to explore.

Evidence might include operator studies, prototypes or explanations showing why an operation matters and what behavior is supported.

##### Numerical confidence

Make the relationship between intended mathematics, finite representations and implemented behavior explicit.

Evidence might include error analysis, comparisons to reference behavior or documented limitations of an arithmetic approach.

##### Understood efficiency

Understand how compute organization affects performance and implementation cost under realistic assumptions.

Evidence might include utilization studies, pipeline comparisons, measurements or resource analyses.

##### Composable compute blocks

Enable other teams to use compute capabilities without hidden assumptions about timing, control or data representation.

Evidence might include clear interfaces, integration experience or reusable design and teaching material.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: rtl-memory

[Open repository](https://github.com/SiliconBadgers/rtl-memory) | [Source charter](https://github.com/SiliconBadgers/rtl-memory/blob/ac2d19fd0658765573108d07451aac4003f3211e/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/rtl-memory/blob/ac2d19fd0658765573108d07451aac4003f3211e/OBJECTIVES.md)

#### Purpose

Understand and develop how data is stored, accessed and moved within the accelerator. The team makes memory behavior and its performance consequences explicit, supporting useful computation while balancing capacity, bandwidth, latency, cost and implementation constraints.

Data access can shape the effectiveness of the entire accelerator. This team connects workload access patterns to storage organization and movement mechanisms. Its contributions can include access-pattern studies, architecture comparisons, interface explanations, behavioral models, RTL or measurements.

#### Responsibilities

##### Storage organization

Study capacity, locality, banking, buffering, ports and storage hierarchy choices in the context of the project’s workloads. Explain the assumptions behind the chosen organization.

##### Movement and access behavior

Own memory-side access mechanisms, queues, arbitration and data movement services within the agreed subsystem boundary. DMA is one possible mechanism when the system needs it, not a predetermined deliverable.

##### Memory semantics

Make addressing, ordering, conflicts, response behavior, initialization and reset implications understandable to consumers. Participate in establishing shared contracts for externally visible behavior.

##### Memory feasibility and performance

Investigate bandwidth demand, contention, reuse and physical storage constraints. Distinguish behavioral abstractions from realizable resources and preserve evidence behind estimates.

#### Boundaries and shared decisions

rtl-memory owns the storage subsystem and its access services. rtl-control decides when accelerator operations request those services; rtl-compute owns local arithmetic behavior; soc connects subsystem and host interfaces. Architecture coordinates the shared address and data model. Physical-design informs storage implementation options, and FPGA owns the board-specific adaptation of external memory resources. Exact routing and protocol boundaries are agreed where these responsibilities meet.

#### Member autonomy

Members may investigate access patterns, compare banking approaches, examine buffering policies, build storage models, explain an interface or develop memory hardware. The team chooses internal organization and methods within agreed semantics. Proposals that alter visible capacity, ordering, addressing or performance assumptions are discussed with consumers rather than decided in isolation.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and ml-models | Use workload dimensions, layouts and access patterns to examine what the storage system needs to support. |
| rtl-control, rtl-compute and soc | Exchange request patterns and interface assumptions; clarify ordering, contention and response behavior at subsystem boundaries. |
| verification, fpga and physical-design | Work together on correctness evidence and on the gap between an abstract storage model and an actual target implementation. |

#### Possible directions

Possible directions include a memory access study, a comparison of buffer organizations, an explanation of conflicting accesses, a behavioral storage model, an arbitration experiment or an investigation of available storage primitives. Members choose which uncertainty or capability is worth pursuing.

#### What progress means

Progress is visible when data movement requirements are understood, consumers can reason about storage behavior, and design choices have a defensible relationship to workload and platform constraints. A study that exposes a bandwidth bottleneck or clarifies ambiguous ordering is a substantive contribution.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/rtl-memory/blob/ac2d19fd0658765573108d07451aac4003f3211e/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/rtl-memory/blob/ac2d19fd0658765573108d07451aac4003f3211e/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/rtl-memory/blob/ac2d19fd0658765573108d07451aac4003f3211e/CHARTER.md) for scope and shared decision boundaries.

##### A workload-informed storage strategy

Understand how the accelerator’s data needs influence capacity, organization and movement choices.

Evidence might include access analyses, locality studies, storage budgets or comparisons of alternatives.

##### Predictable memory behavior

Make storage and access semantics sufficiently clear that consumers can coordinate work reliably.

Evidence might include behavioral explanations, models, interface agreements or checks of corner cases.

##### Understood data movement costs

Reveal how bandwidth, latency, contention and reuse affect the overall design.

Evidence might include experiments, simulations, analytical studies or measured implementation behavior.

##### Feasible and adaptable memory designs

Connect useful memory abstractions to realistic implementation options while allowing the project to evolve.

Evidence might include resource investigations, design alternatives or a demonstrated adaptation to a chosen target.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: rtl-control

[Open repository](https://github.com/SiliconBadgers/rtl-control) | [Source charter](https://github.com/SiliconBadgers/rtl-control/blob/7d887052f1352a4246011476316bf918cf181335/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/rtl-control/blob/7d887052f1352a4246011476316bf918cf181335/OBJECTIVES.md)

#### Purpose

Make accelerator execution understandable and dependable by coordinating operations, resources and progress over time. The team explores how commands become ordered activity across compute and memory, including dependencies, stalls, completion and recovery.

Execution control connects the programming model to the behavior of hardware blocks. Its design affects utilization, predictability and the ability to reason about a running system. The team can contribute through state and scheduling models, design explanations, protocol studies, experiments or hardware implementations.

#### Responsibilities

##### Execution semantics

Develop a clear model of command acceptance, progress, completion and exceptional conditions in collaboration with architecture and software. Make state and sequencing behavior visible enough for others to reason about it.

##### Scheduling and coordination

Study and develop operation ordering, dependencies, hazards, resource use and coordination among compute and memory services. Explore alternative scheduling approaches where they serve project objectives.

##### Liveness and recovery

Reason about stalls, backpressure, reset, cancellation or error behavior appropriate to the agreed design. Explain conditions under which work can progress or needs intervention.

##### Control knowledge and implementation

Maintain useful state diagrams, scheduling analyses, interface models, design rationale and implementation artifacts. Link internal choices to externally visible behavior.

#### Boundaries and shared decisions

rtl-control owns execution sequencing across accelerator operations. soc owns host-facing access, register/address decoding and system wiring; rtl-memory owns access and transfer machinery; rtl-compute owns arithmetic and internal datapath timing. Architecture stewards shared execution semantics with these teams. The control/SoC boundary must make configuration, launch, status and error ownership explicit without merging their charters.

#### Member autonomy

Members can choose to study scheduling strategies, model dependencies, examine deadlock conditions, explain a protocol, prototype a controller or improve an existing design. The team chooses its internal representation and implementation approach. Changes to command meaning or behavior seen by other blocks require shared agreement. No particular sequencer, command set or scheduling policy is mandated by the scaffold.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and ml-compiler | Connect intended operation semantics and software expectations to a realizable execution model. |
| rtl-compute and rtl-memory | Agree on operation requests, resource availability, responses and the assumptions required for progress. |
| soc and verification | Clarify the host-to-execution boundary and collaborate on observations that demonstrate correct ordering, progress and recovery. |

#### Possible directions

Members might compare centralized and distributed scheduling, investigate hazards, draw execution traces, analyze stalled transactions, develop a small controller or explain a recovery strategy. These are possible lines of inquiry; the team chooses its own work in service of the charter.

#### What progress means

Progress means the project can explain how operations execute, identify when progress is possible, and connect execution behavior to correctness and performance. State models, reasoned scheduling comparisons, verification findings and implementations can all supply useful evidence.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/rtl-control/blob/7d887052f1352a4246011476316bf918cf181335/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/rtl-control/blob/7d887052f1352a4246011476316bf918cf181335/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/rtl-control/blob/7d887052f1352a4246011476316bf918cf181335/CHARTER.md) for scope and shared decision boundaries.

##### An understandable execution model

Make the transition from a submitted operation to its completion clear to both hardware and software contributors.

Evidence might include state explanations, execution traces, interface definitions or a working model.

##### Reliable coordination

Support correct operation ordering and cooperation among compute and memory under the agreed conditions.

Evidence might include dependency analysis, protocol studies, simulations or implementations with explained assumptions.

##### Explained progress and recovery

Understand how execution responds to stalls, resource conflicts, reset and errors.

Evidence might include liveness reasoning, counterexamples, recovery designs or targeted experiments.

##### Informed scheduling choices

Understand how control decisions influence resource use and system performance.

Evidence might include schedule comparisons, utilization studies or measurements that guide an implementation choice.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: soc

[Open repository](https://github.com/SiliconBadgers/soc) | [Source charter](https://github.com/SiliconBadgers/soc/blob/40e39bdfa3c5b9d752a60975789b571303d793b9/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/soc/blob/40e39bdfa3c5b9d752a60975789b571303d793b9/OBJECTIVES.md)

#### Purpose

Bring the accelerator’s hardware capabilities together into a coherent system. The team makes block composition, host visibility and chip-level behavior understandable, so that individually developed components can participate in a usable and explainable whole.

System composition exposes assumptions that may be invisible inside an individual block. The SoC team develops the hardware context in which compute, memory and control interact with software and platform boundaries. Its work includes system modeling, interface reasoning, integration design, investigation and RTL.

#### Responsibilities

##### Hardware composition

Own top-level hardware organization and connections among accelerator blocks. Explain which component supplies each capability and how their assumptions fit together.

##### Host-visible behavior

Develop the host interface, register/address decoding, system interconnect and visibility of configuration, progress, results and errors in collaboration with architecture, control and software.

##### System-wide signals and boundaries

Reason about clock and reset organization, interrupts and crossings where the selected design requires them. Make the boundary between chip-level logic and platform-specific wrappers explicit.

##### Integration understanding

Maintain diagrams, assumptions, interface rationale and evidence from composed hardware. Investigate emergent behavior and support changes that keep the hardware system coherent.

#### Boundaries and shared decisions

SoC owns hardware composition and host-facing access. rtl-control owns execution sequencing; rtl-compute and rtl-memory own their respective block internals. FPGA owns board shells, pin constraints and board transport adaptation. Accelerator owns combined-system understanding, experiments and release context across hardware and software. Shared address, command and reset semantics are agreed with architecture and the affected consumers.

#### Member autonomy

Members may study interface options, map block connections, investigate reset behavior, model a system boundary, explore observability or develop integration hardware. The team decides internal organization within agreed external behavior. Changes that affect software access, block interfaces or platform assumptions are collaborative decisions. The scaffold does not select a bus standard, address map or top-level implementation.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| RTL block teams | Exchange concrete interface expectations, reset assumptions and composition needs while preserving each block’s authoritative implementation. |
| architecture and ml-compiler | Agree on what software can observe and control, and how system behavior is described consistently. |
| verification, fpga, physical-design and accelerator | Provide system context for independent assessment, target adaptation and combined demonstrations; use their feedback to refine integration assumptions. |

#### Possible directions

Possible directions include comparing host interfaces, making a block diagram executable, investigating clock/reset relationships, analyzing error visibility, building a system model or integrating selected blocks. Members choose the scale and form of their contribution.

#### What progress means

Progress is visible when composition is easier to understand, cross-block assumptions are explicit and hardware behavior can be observed and explained. A resolved interface ambiguity, a useful system diagram or an integration experiment can advance the charter alongside production RTL.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/soc/blob/40e39bdfa3c5b9d752a60975789b571303d793b9/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/soc/blob/40e39bdfa3c5b9d752a60975789b571303d793b9/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/soc/blob/40e39bdfa3c5b9d752a60975789b571303d793b9/CHARTER.md) for scope and shared decision boundaries.

##### Coherent hardware composition

Develop an understandable organization in which independently developed blocks cooperate as a system.

Evidence might include composition diagrams, interface models, integration designs or demonstrated block cooperation.

##### Clear host interaction

Make configuration, execution visibility and results accessible through a consistent system interface.

Evidence might include programming-model explanations, interface studies or demonstrations of host-visible behavior.

##### Predictable system-wide behavior

Understand reset, clocks, errors and other conditions that span component boundaries.

Evidence might include system analyses, boundary agreements, experiments or validation results with explicit assumptions.

##### Adaptable integration

Support changes to blocks and platforms while preserving a coherent system model.

Evidence might include reusable integration structures, clearly separated platform boundaries or documented lessons from composition.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: ml-compiler

[Open repository](https://github.com/SiliconBadgers/ml-compiler) | [Source charter](https://github.com/SiliconBadgers/ml-compiler/blob/394e5a30bad880c181ab5536b44e93d1106120ea/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/ml-compiler/blob/394e5a30bad880c181ab5536b44e93d1106120ea/OBJECTIVES.md)

#### Purpose

Make the accelerator understandable and usable for machine-learning workloads through software. The team connects intended workloads and algorithms to hardware capabilities through programming abstractions, mappings and runtime behavior that members can investigate, explain and develop.

An accelerator’s value depends in part on how people express useful work and understand its execution. This team explores that software/hardware relationship, from programming-model questions and algorithm mappings to compilers, libraries, runtimes and host tools when those approaches are appropriate.

#### Responsibilities

##### Programming experience

Study what users and workload developers need to express, observe and control. Develop explanations and abstractions that connect user intent to supported hardware behavior.

##### Workload mapping

Investigate how operations, data layouts and execution choices map onto accelerator capabilities. Compare approaches using both numerical meaning and system constraints.

##### Software realization

Own compiler, assembly, code generation, runtime and host software responsibilities selected by the team. Maintain a clear distinction between proposed abstractions, implemented capabilities and unsupported behavior.

##### Software/hardware agreement

Participate in defining command and data semantics with architecture and hardware teams. Explain how software depends on those semantics and provide feedback when hardware choices affect usability.

#### Boundaries and shared decisions

This team owns the software-facing path to accelerator use. Architecture stewards shared execution and data semantics; ml-models supplies numerical reference behavior; control realizes execution; SoC provides hardware-visible access. FPGA owns platform-specific transport integration, with the software API boundary agreed together. The team is free to choose a compiler, a smaller runtime, research artifacts or other approaches appropriate to the current questions.

#### Member autonomy

Members can investigate programming abstractions, study lowering strategies, compare data layouts, build examples, improve diagnostics, prototype a runtime or develop compiler infrastructure. They choose methods and scope based on their interests and the charter. A language, framework, ISA encoding or software stack is not selected by this scaffold. Changes to shared semantics require agreement with their hardware and model counterparts.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and ml-models | Connect workload meaning, numerical expectations and user needs to shared operation and data definitions. |
| rtl-control and soc | Agree on execution and access behavior, including the information software needs to reason about progress and results. |
| fpga, verification and accelerator | Use platform feedback and system experiments to assess usability and correctness from the software side. |

#### Possible directions

Members might explore a programming model, explain an operator mapping, compare layouts, develop a software example, study compiler techniques or investigate runtime observability. A useful result may be an analysis or design proposal before there is a reason to implement a full toolchain.

#### What progress means

Progress means the path from user intent to accelerator behavior becomes clearer and more useful. Evidence can include workload mappings, usable examples, comparisons of abstractions, tested software or a documented limitation that changes a design decision.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/ml-compiler/blob/394e5a30bad880c181ab5536b44e93d1106120ea/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/ml-compiler/blob/394e5a30bad880c181ab5536b44e93d1106120ea/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/ml-compiler/blob/394e5a30bad880c181ab5536b44e93d1106120ea/CHARTER.md) for scope and shared decision boundaries.

##### An intelligible programming model

Make it possible to describe supported work and understand what the accelerator promises to do.

Evidence might include abstraction studies, API or language proposals, examples or clear explanations of execution behavior.

##### Effective workload mapping

Understand how software choices interact with compute, memory and control capabilities.

Evidence might include mapping analyses, layout comparisons, compiler experiments or workload studies.

##### Dependable software interaction

Support software use that handles results, errors and execution state consistently with the hardware contract.

Evidence might include runtime designs, simulation experiments, diagnostics or tested host interactions.

##### An accessible contribution path

Help members understand and extend the software/hardware connection at different levels of experience.

Evidence might include tutorials, small examples, research notes or maintainable software abstractions.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: ml-models

[Open repository](https://github.com/SiliconBadgers/ml-models) | [Source charter](https://github.com/SiliconBadgers/ml-models/blob/7b52b7e09be7b283bb62c04d042c9a7141613be6/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/ml-models/blob/7b52b7e09be7b283bb62c04d042c9a7141613be6/OBJECTIVES.md)

#### Purpose

Connect the accelerator project to meaningful machine-learning workloads and trustworthy numerical understanding. The team studies algorithms, representations and workload behavior, and develops references that help other teams reason about both correctness and usefulness.

A correct hardware result is meaningful only relative to a well-understood computation. This team keeps the project grounded in algorithmic intent, finite-precision behavior and the characteristics of the workloads it chooses to support. Modeling can range from mathematical explanation to executable references and empirical workload studies.

#### Responsibilities

##### Workload understanding

Investigate relevant algorithms, model structures, operator mixes, dimensions and data behavior. Explain which characteristics matter to architectural and implementation choices.

##### Numerical reasoning

Study representations, quantization, accumulation, rounding and error behavior as appropriate to the selected workloads. Distinguish mathematical intent, chosen finite-precision semantics and observed model quality.

##### Reference behavior

Develop and maintain understandable reference computations and representative inputs that other teams can use. State what a reference establishes, its assumptions and the conditions it does not cover.

##### Reproducible knowledge

Preserve methods, provenance, experiment context and numerical explanations so results can be understood and revisited. Make model and workload knowledge accessible to hardware and software contributors.

#### Boundaries and shared decisions

ml-models owns numerical and workload references. Architecture uses that knowledge to establish shared system semantics; compute implements arithmetic; ml-compiler maps algorithms to supported execution; verification uses references alongside independent reasoning. A model implementation is evidence with assumptions, not an automatic definition of correct hardware behavior. Timing-oriented architectural modeling belongs with architecture unless a specific study is jointly owned.

#### Member autonomy

Members can choose algorithm or workload studies, quantization experiments, reference implementations, numerical comparisons, dataset characterization or teaching material. Methods and frameworks are selected by the team as needed. Changes that redefine expected numerical behavior or the workload used for shared claims are discussed with the affected teams. The existing MAC reference does not set the scope of the team’s research.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and ml-compiler | Share workload structure, representation choices and numerical expectations that inform capability and mapping decisions. |
| rtl-compute and rtl-memory | Explain operation semantics and data characteristics that matter for datapath and storage design. |
| verification and accelerator | Provide references and representative cases, interpret discrepancies and clarify the limits of system-level correctness or quality claims. |

#### Possible directions

Members might study a model family, compare numerical representations, investigate sensitivity to quantization, explain a reference operator, capture a representative workload or improve reproducibility. Small studies with clear assumptions can be useful without requiring large-model training or infrastructure.

#### What progress means

Progress means algorithmic intent and approximation choices become clearer, references become more trustworthy, and the project can explain why its selected computations matter. A negative numerical result or a clarified reference assumption can materially improve the design.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/ml-models/blob/7b52b7e09be7b283bb62c04d042c9a7141613be6/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/ml-models/blob/7b52b7e09be7b283bb62c04d042c9a7141613be6/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/ml-models/blob/7b52b7e09be7b283bb62c04d042c9a7141613be6/CHARTER.md) for scope and shared decision boundaries.

##### Meaningful workload context

Help the project understand the computations and data behavior it is trying to support.

Evidence might include workload profiles, algorithm explanations, operator analyses or representative cases.

##### Understood numerical behavior

Reveal how representation and approximation choices affect correctness or workload quality.

Evidence might include analytical reasoning, quantization studies, comparisons or documented limits.

##### Trustworthy reference computations

Give other teams useful numerical anchors with explicit scope and assumptions.

Evidence might include well-explained reference operators, reviewed examples, deterministic fixtures or discrepancy investigations.

##### Reproducible shared learning

Make numerical and workload findings accessible and possible to revisit.

Evidence might include documented methods, compact experiments, interpretation guides or educational material.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: verification

[Open repository](https://github.com/SiliconBadgers/verification) | [Source charter](https://github.com/SiliconBadgers/verification/blob/039b0c94055be7a1ce38e9122e2c26b64f925d0e/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/verification/blob/039b0c94055be7a1ce38e9122e2c26b64f925d0e/OBJECTIVES.md)

#### Purpose

Develop justified confidence in the accelerator by asking what it should do, what could invalidate that expectation and what evidence is sufficient for the claims being made. The team helps the project understand correctness, uncertainty and risk across component and system boundaries.

Verification is a form of investigation as well as implementation. Useful work can clarify an ambiguous requirement, construct a counterexample, compare verification methods, reason about a protocol, develop a test environment or explain where existing evidence is incomplete. The team’s remit is broader than running other teams’ tests.

#### Responsibilities

##### Correctness interpretation

Work with specification and implementation teams to make requirements observable and assessable. Identify ambiguity, contradictory assumptions and behavior that has not yet been defined.

##### Independent assessment

Choose verification approaches appropriate to the claim: review, modeling, simulation, assertions, formal reasoning or other methods. Preserve independence of reasoning even when artifacts are shared.

##### Coverage and limitations

Explain what evidence covers, how it was obtained and which behaviors or operating conditions remain uncertain. Distinguish a passing example from a justified broader claim.

##### Verification knowledge

Maintain reusable reasoning, environments, findings and educational material. Help members understand failure modes and how verification can shape a design before or during implementation.

#### Boundaries and shared decisions

Verification stewards independent assessment; each component team remains responsible for the quality and local validation of its work. Architecture and affected teams resolve intended semantics together. ml-models supplies reference behavior with stated assumptions. Accelerator organizes combined-system evidence and demonstrations. Verification communicates findings and confidence rather than unilaterally selecting system priorities or assigning implementation work.

#### Member autonomy

Members may choose a correctness question, examine a specification, investigate a verification technique, develop a model, explore formal properties, build test infrastructure or analyze a failure. The method should fit the question; no framework or coverage metric is prescribed here. Changes to intended behavior are agreed with the responsible teams, while findings can challenge any existing assumption.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and ml-models | Clarify intended behavior and numerical assumptions, and investigate where references or specifications may themselves be incomplete. |
| RTL and software teams | Exchange observable behavior, design intent and findings. Support actionable interpretation of mismatches without replacing component-owned validation. |
| fpga, physical-design and accelerator | Help distinguish functional, platform and implementation claims, and explain which evidence supports each. |

#### Possible directions

Possible directions include a protocol counterexample, a reset-behavior study, a survey of formal techniques, a useful assertion, an independent scoreboard, a failure investigation or a guide to interpreting coverage. Members choose meaningful questions rather than a fixed queue of test-writing assignments.

#### What progress means

Progress means the project makes better-supported claims, discovers important misunderstandings and understands the remaining uncertainty. Finding an unsupported assumption, narrowing a confidence claim or documenting a useful verification method can be valuable even when no bug is found.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/verification/blob/039b0c94055be7a1ce38e9122e2c26b64f925d0e/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/verification/blob/039b0c94055be7a1ce38e9122e2c26b64f925d0e/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/verification/blob/039b0c94055be7a1ce38e9122e2c26b64f925d0e/CHARTER.md) for scope and shared decision boundaries.

##### Clear correctness questions

Make intended behavior and the claims worth assessing explicit across the project.

Evidence might include requirement analyses, observable properties, clarified ambiguity or well-posed verification questions.

##### Appropriate independent evidence

Build confidence using methods whose assumptions and scope fit the design questions.

Evidence might include reviews, simulation results, formal reasoning, counterexamples or comparisons of methods.

##### Visible uncertainty

Make gaps and limitations understandable so the project can decide what to investigate next.

Evidence might include coverage arguments, untested-condition analyses or explanations of the limits of a result.

##### A stronger verification culture

Help members reason critically about correctness and contribute evidence throughout design work.

Evidence might include reusable environments, debugging narratives, tutorials or collaborative design reviews.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: fpga

[Open repository](https://github.com/SiliconBadgers/fpga) | [Source charter](https://github.com/SiliconBadgers/fpga/blob/dda9dd68e7ea9e64724169d325320f1ad0f82154/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/fpga/blob/dda9dd68e7ea9e64724169d325320f1ad0f82154/OBJECTIVES.md)

#### Purpose

Use FPGA platforms to explore, demonstrate and understand accelerator behavior in a physical system. The team connects design ideas to practical hardware experience and feeds platform observations back into the wider project.

Prototyping helps reveal assumptions about clocks, IO, memory, software interaction and observability that may be difficult to see in isolated simulation. The team contributes through platform studies, experiments, system adaptation, measurement, demonstrations and explanations of what hardware evidence means.

#### Responsibilities

##### Platform understanding

Investigate available boards, tools, resources and interfaces in relation to the project’s interests and constraints. Explain the opportunities and limitations of a chosen platform.

##### Board adaptation

Own board-specific shells, connections, constraints and host transport adaptation. Make the relationship between reusable accelerator logic and target-specific implementation explicit.

##### Physical experimentation

Develop ways to observe and investigate behavior on hardware, including bring-up, measurement and reproducible demonstrations where useful. Distinguish simulated, built and observed hardware results.

##### Shared practical knowledge

Preserve setup knowledge, experiments, limitations and lessons so members can learn from and extend physical prototypes without depending on undocumented experience.

#### Boundaries and shared decisions

FPGA owns board-specific adaptation and prototyping. soc owns reusable chip-level composition; RTL teams own block implementations; ml-compiler owns software abstractions, with the transport boundary agreed together. Architecture interprets platform constraints as one input to system design. Physical-design studies ASIC implementation, whose results are distinct from FPGA resource and timing observations.

#### Member autonomy

Members may investigate a board capability, compare platforms, study a transport, develop instrumentation, perform a hardware experiment or create a teaching demonstration. The team chooses the scale and form of its prototypes within available resources. New platform commitments and changes to shared hardware/software interfaces are discussed with the affected teams. No board, vendor toolchain or mandatory demonstration is selected by the scaffold.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| soc and RTL teams | Agree on the boundary between reusable design and board-specific behavior, and return feedback from target constraints and observations. |
| ml-compiler and verification | Connect host use and observed hardware behavior to software expectations and independent correctness evidence. |
| architecture and accelerator | Share platform capabilities, practical limits and interpreted measurements that can guide design choices and system demonstrations. |

#### Possible directions

Members might investigate memory access on a board, compare transport choices, explore hardware observability, create a small physical demonstration, analyze timing reports or document platform behavior. A feasibility study can be a useful contribution even when hardware access limits implementation work.

#### What progress means

Progress means the project learns something defensible from its interaction with hardware, can distinguish observation from assumption, and can reuse the practical knowledge gained. A clear platform comparison, a measured limitation or an accessible demonstration can all advance the charter.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/fpga/blob/dda9dd68e7ea9e64724169d325320f1ad0f82154/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/fpga/blob/dda9dd68e7ea9e64724169d325320f1ad0f82154/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/fpga/blob/dda9dd68e7ea9e64724169d325320f1ad0f82154/CHARTER.md) for scope and shared decision boundaries.

##### Informed platform choices

Understand which physical platforms and capabilities suit the project’s learning and engineering goals.

Evidence might include capability studies, comparisons or documented constraints connected to system needs.

##### Useful physical experimentation

Enable meaningful investigation of accelerator behavior beyond isolated models.

Evidence might include reproducible prototypes, instrumentation, measurements or hardware demonstrations with clear scope.

##### Clear platform boundaries

Keep reusable accelerator behavior and board-specific adaptation understandable as the design evolves.

Evidence might include interface explanations, adaptation designs or experience moving a concept between environments.

##### Accessible hardware knowledge

Help members learn from and extend physical-system work.

Evidence might include bring-up narratives, experiment notes, tutorials or explanations of hardware limitations.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: physical-design

[Open repository](https://github.com/SiliconBadgers/physical-design) | [Source charter](https://github.com/SiliconBadgers/physical-design/blob/57a4bd4e49c6c81ea189683f76aa2c8ac644e056/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/physical-design/blob/57a4bd4e49c6c81ea189683f76aa2c8ac644e056/OBJECTIVES.md)

#### Purpose

Connect logical hardware design to the realities of implementing a chip. The team investigates how technology, constraints and implementation choices affect feasibility, performance, power, area and confidence in the physical realization of the accelerator.

Physical implementation informs design choices long before a final chip exists. Studies of constraints, timing, storage options, synthesis behavior or implementation methodology can expose important tradeoffs. The team’s role includes research and interpretation as well as operating implementation tools.

#### Responsibilities

##### Implementation assumptions

Understand and explain target technology, libraries, tools and constraints relevant to the design. Distinguish available resources, exploratory assumptions and decisions the project has actually adopted.

##### Logical-to-physical tradeoffs

Investigate how RTL and architectural choices influence area, timing, power and physical organization. Feed evidence back to design teams in terms they can use.

##### Implementation methods and evidence

Develop suitable synthesis, timing, equivalence and physical implementation approaches as the project needs them. Explain what a flow and its checks do and do not establish.

##### Physical-design understanding

Preserve constraint rationale, experiments, results and interpretation so members can build knowledge rather than inherit opaque scripts or unexplained reports.

#### Boundaries and shared decisions

Physical-design owns ASIC implementation methods and interpretation of their results. RTL teams own functional block design; SoC owns hardware composition; architecture helps interpret system tradeoffs; verification contributes functional confidence. FPGA results describe a different implementation target. Physical-design can propose changes based on evidence, with behavior or shared-interface changes agreed with the responsible teams.

#### Member autonomy

Members may study timing methodology, compare synthesis outcomes, examine storage implementation choices, investigate constraints, build a flow, analyze reports or create educational material. Tools and targets follow the team’s questions and available access. Choosing a technology, adding external commitments or changing a shared design constraint is a collaborative decision. The charter does not set a tapeout date or equate a starter flow with sign-off readiness.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| RTL teams and soc | Exchange design intent, clock/reset assumptions and implementation feedback to connect measured issues to useful design choices. |
| architecture and ml-models | Relate physical costs and constraints to architectural estimates and workload needs without implying that an isolated metric determines the whole design. |
| verification and accelerator | Clarify the scope of implementation evidence and how it fits with functional and system-level claims. |

#### Possible directions

Members might investigate why a path is critical, compare alternative datapaths after synthesis, study constraint quality, explore a floorplanning idea, examine memory options or explain an implementation report. A careful analysis can be valuable before a complete flow is practical.

#### What progress means

Progress means implementation assumptions are explicit, results can be interpreted and design choices become better informed. A discovered constraint problem, a reproducible comparison or an explanation of an unavailable technology option is useful alongside more complete implementation work.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/physical-design/blob/57a4bd4e49c6c81ea189683f76aa2c8ac644e056/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/physical-design/blob/57a4bd4e49c6c81ea189683f76aa2c8ac644e056/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/physical-design/blob/57a4bd4e49c6c81ea189683f76aa2c8ac644e056/CHARTER.md) for scope and shared decision boundaries.

##### Understood implementation feasibility

Connect the proposed design to realistic technology, tooling and resource assumptions.

Evidence might include feasibility studies, technology investigations or documented limits on the conclusions currently possible.

##### Useful physical tradeoff evidence

Help the project understand how design choices affect physical costs and behavior.

Evidence might include comparative synthesis studies, timing analysis, power estimates or physical experiments with clear assumptions.

##### Trustworthy implementation methods

Make constraints, flows and result interpretation understandable and appropriately checked.

Evidence might include methodology studies, reproducible flows, constraint analyses or explanations of report limitations.

##### Shared physical-design knowledge

Build the team’s ability to reason about implementation and communicate findings to other contributors.

Evidence might include tutorials, experiment narratives, design feedback or accessible methodology documentation.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.

### Team: accelerator

[Open repository](https://github.com/SiliconBadgers/accelerator) | [Source charter](https://github.com/SiliconBadgers/accelerator/blob/070c21162baf32951afa0bf426217f41c633a640/CHARTER.md) | [Source objectives](https://github.com/SiliconBadgers/accelerator/blob/070c21162baf32951afa0bf426217f41c633a640/OBJECTIVES.md)

#### Purpose

Help the separate teams form a coherent accelerator project and understand what the combined system can actually do. This repository holds the system-level context, integration knowledge and shared evidence that connect individual team contributions.

The system can have properties and limitations that are not visible in one repository. This team brings component work into a common context, makes dependencies understandable and helps the group interpret demonstrations and measurements. Integration tooling is one possible means of doing that; the charter is broader than infrastructure maintenance.

#### Responsibilities

##### Combined-system understanding

Maintain an accessible view of how capabilities, assumptions and interfaces from separate teams fit together. Explain system configurations and identify integration questions that cross repository boundaries.

##### Shared evidence and demonstrations

Develop and interpret combined-system experiments that illuminate behavior or support agreed claims. Distinguish demonstrated capability from planned work and local component results.

##### Coordination through clarity

Make cross-team dependencies and unresolved assumptions visible, helping the relevant teams agree on compatible changes and shared ambitions. Preserve the reasoning behind those agreements.

##### Reproducible integration knowledge

Maintain the context needed to revisit system results, including configurations, methods, dependencies and limitations. Tooling and runbooks serve that understanding when they are useful.

#### Boundaries and shared decisions

Accelerator owns the cross-repository system view and integration context. Architecture stewards intended system semantics and architectural tradeoffs; soc owns composed hardware; individual teams own their research and implementations; verification owns independent assessment. This repository does not assign work to other teams or centralize copies of their source. Shared milestones are selected together by the participating teams.

#### Member autonomy

Members may investigate a system interaction, compare configurations, explain dependencies, design a demonstration, analyze system measurements or improve integration reproducibility. They choose the questions and methods within this charter. Demonstrations, priorities and claims that depend on other teams are agreed with those teams. The existing MAC runner is an optional example of integration and does not set a required project roadmap.

#### Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and all component teams | Connect intended behavior with actual capabilities and assumptions, and make incompatibilities visible to the teams able to resolve them. |
| ml-models, ml-compiler and verification | Relate workload meaning, software use and independent evidence to combined-system behavior. |
| fpga and physical-design | Interpret platform and implementation observations in their proper system context, including the limits of comparison between targets. |

#### Possible directions

Members might explain the current dependency structure, compare a pair of system configurations, investigate a cross-block mismatch, develop a meaningful demonstration, study performance attribution or improve how results are communicated. Infrastructure work is useful when it enables one of these outcomes.

#### What progress means

Progress means members can understand the combined system, reproduce and interpret meaningful results, and agree on changes without relying on hidden assumptions. A clarified dependency, a discovered integration limitation or a carefully scoped demonstration can all advance the charter.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](https://github.com/SiliconBadgers/accelerator/blob/070c21162baf32951afa0bf426217f41c633a640/OBJECTIVES.md) describe durable outcomes, and the
[repository structure](https://github.com/SiliconBadgers/accelerator/blob/070c21162baf32951afa0bf426217f41c633a640/README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.

#### High-level objectives

These objectives express the outcomes this team exists to advance. Members
choose which questions to pursue, the approach, the scale and the contribution
format. The order is not a priority ranking, and the examples of evidence are
illustrative. They are not a checklist, required deliverables or assignments.

Read the [charter](https://github.com/SiliconBadgers/accelerator/blob/070c21162baf32951afa0bf426217f41c633a640/CHARTER.md) for scope and shared decision boundaries.

##### A coherent system view

Make the relationship among team capabilities, interfaces and assumptions understandable.

Evidence might include system narratives, dependency explanations, configuration descriptions or resolved cross-team ambiguities.

##### Meaningful combined-system evidence

Help the project learn from interactions that span multiple components.

Evidence might include demonstrations, system studies, measurements or investigations with an explicit question and scope.

##### Sustainable collaboration across teams

Support compatible evolution while respecting each team’s ownership and choice of work.

Evidence might include clearer handoffs, shared decisions or documented resolution of integration conflicts.

##### Revisitable system knowledge

Make it possible to understand and revisit what a result demonstrates and how it was obtained.

Evidence might include experiment context, reproducible configurations, interpreted results or useful integration tooling.

##### Using these objectives

Use the objectives to explain why a chosen line of work matters and to reflect
on what has been learned. A member can advance several objectives through one
study, or explore one objective deeply. Leads support the conversation and help
connect related interests across the team. Members can propose new directions
or changes to these objectives when they can explain how the charter would be
better served.


## 21. Evidence and keeping the plan current

This plan distinguishes checkpoint facts, project decisions, supplied implementation evidence, calculated scenarios, open questions and recommendations for discussion. A proposal should retain its status until the affected teams adopt it. A successful example should retain the limits of the behavior it tested.

### Technical sources and reproducible calculations

Model facts are pinned to the [Qwen3.5-2B checkpoint revision](https://huggingface.co/Qwen/Qwen3.5-2B/tree/15852e8c16360a2fea060d615a32b45270f8a8fc). The [source inventory](sources/README.md) records what was inspected and what was not executed. The Transformers implementation was inspected at a recorded commit; it is a semantic reference, not an installed and validated runtime environment.

The [budget calculator](model_budget.py) derives parameters, matrix work, storage, state, KV and traffic from the saved configuration and tensor header. The [JSON results](model-budget.json) retain exact values and assumptions. Rebuilding the document regenerates the numerical tables without a network call. The calculations reconcile all 632 stored tensor shapes with the checkpoint metadata total, then select the text decoder and explicitly account for tied output weights.

Format and algorithm discussions link primary sources where used: OCP for MXFP4, NVIDIA for NVFP4, the Gated Delta Networks paper, FlashAttention, GQA, AWQ and GPTQ. Recommendations and bottleneck comparisons in this document are project analysis derived from those semantics and the recorded assumptions. They are not measurements reported by those sources.

### Repository evidence

The initial repository publication was checked for private visibility, exactly one commit per repository and the configured project author. Fresh GitHub clones matched the reviewed source files and passed the MAC example. Repository descriptions were subsequently edited without changing the commits.

Repository snapshot checked September 10, 2026 at 09:48 PM CDT.

| Repository | Recorded revision | Visibility | Commits at check |
|---|---|---|---|
| architecture | [4e67ed3711](https://github.com/SiliconBadgers/architecture/commit/4e67ed3711179c1500c5109defbad96447dfc7be) | Private | 1 |
| rtl-compute | [b25a309d49](https://github.com/SiliconBadgers/rtl-compute/commit/b25a309d4964b403fae2ab189d240eae47843a50) | Private | 1 |
| rtl-memory | [ac2d19fd06](https://github.com/SiliconBadgers/rtl-memory/commit/ac2d19fd0658765573108d07451aac4003f3211e) | Private | 1 |
| rtl-control | [7d887052f1](https://github.com/SiliconBadgers/rtl-control/commit/7d887052f1352a4246011476316bf918cf181335) | Private | 1 |
| soc | [40e39bdfa3](https://github.com/SiliconBadgers/soc/commit/40e39bdfa3c5b9d752a60975789b571303d793b9) | Private | 1 |
| ml-compiler | [394e5a30ba](https://github.com/SiliconBadgers/ml-compiler/commit/394e5a30bad880c181ab5536b44e93d1106120ea) | Private | 1 |
| ml-models | [7b52b7e09b](https://github.com/SiliconBadgers/ml-models/commit/7b52b7e09be7b283bb62c04d042c9a7141613be6) | Private | 1 |
| verification | [039b0c9405](https://github.com/SiliconBadgers/verification/commit/039b0c94055be7a1ce38e9122e2c26b64f925d0e) | Private | 1 |
| fpga | [dda9dd68e7](https://github.com/SiliconBadgers/fpga/commit/dda9dd68e7ea9e64724169d325320f1ad0f82154) | Private | 1 |
| physical-design | [57a4bd4e49](https://github.com/SiliconBadgers/physical-design/commit/57a4bd4e49c6c81ea189683f76aa2c8ac644e056) | Private | 1 |
| accelerator | [070c21162b](https://github.com/SiliconBadgers/accelerator/commit/070c21162baf32951afa0bf426217f41c633a640) | Private | 1 |

The [published repository index](https://github.com/SiliconBadgers/accelerator/blob/main/docs/REPOSITORIES.md), [team guide](https://github.com/SiliconBadgers/accelerator/blob/main/docs/TEAM_GUIDE.md) and [example validation](https://github.com/SiliconBadgers/accelerator/blob/main/docs/VALIDATION.md) provide the shared source material. The companion `repository-snapshot.json` records this document’s repository check.

This master plan lives in the private [SiliconBadgers planning repository](https://github.com/SiliconBadgers/planning), alongside its editable sources, calculations and pinned charter snapshots. The Markdown is the complete readable export, and the HTML is its browsable reading view. A fresh clone can rebuild both using Python without sibling repositories or network access. Running the builder updates local generated files; sharing a revision uses an ordinary reviewed Git commit and push.

The next revision should record the accepted quantization policy, evaluation thresholds and resource envelope, then attach measured evidence as teams produce it. A later model change should update the pinned configuration, tensor inventory, formulas and relevant contracts together. Calculated limits remain calculations until a complete measured result supports a stronger claim.
