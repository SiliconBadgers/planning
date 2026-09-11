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

{{TENSOR_TABLE}}

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

{{WEIGHT_TABLE}}

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

{{PREFILL_TABLE}}

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

{{BANDWIDTH_TABLE}}

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

{{CONTEXT_TABLE}}

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
