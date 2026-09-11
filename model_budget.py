"""Reproducible planning arithmetic from pinned config and tensor shapes.

Standard library only. This is a capacity and operation-count model, not a
simulator, quantizer, runtime benchmark, or measured hardware performance claim.
"""
from pathlib import Path
import hashlib
import json
from math import prod, ceil

ROOT = Path(__file__).resolve().parent
MIB = 2**20
GIB = 2**30


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '|' + '|'.join(['---'] * len(headers)) + '|'] +
                     ['| ' + ' | '.join(str(v) for v in row) + ' |' for row in rows])


def calculate():
    config = json.loads((ROOT / 'sources/qwen35-2b-config.json').read_text())['text_config']
    inventory = json.loads((ROOT / 'sources/qwen35-2b-tensors.json').read_text())
    metadata = json.loads((ROOT / 'sources/qwen35-2b-model.json').read_text())
    text_tensors = {k: v for k, v in inventory.items() if k.startswith('model.language_model.')}
    text_parameters = sum(prod(v['shape']) for v in text_tensors.values())
    full_parameters = sum(prod(v['shape']) for v in inventory.values())
    assert full_parameters == metadata['safetensors']['total']
    major = {k: v for k, v in text_tensors.items() if len(v['shape']) == 2 and
             '.in_proj_a.' not in k and '.in_proj_b.' not in k}
    retained = {k: v for k, v in text_tensors.items() if k not in major}
    retained_bytes = sum(prod(v['shape']) * {'BF16': 2, 'F32': 4}[v['dtype']] for v in retained.values())
    quant_parameters = sum(prod(v['shape']) for v in major.values())
    assert quant_parameters + sum(prod(v['shape']) for v in retained.values()) == text_parameters
    assert all(v['shape'][-1] % 128 == 0 for v in major.values())
    h, intermediate, vocab = (config[k] for k in ('hidden_size', 'intermediate_size', 'vocab_size'))
    layers = config['num_hidden_layers']
    linear_layers = config['layer_types'].count('linear_attention')
    full_layers = config['layer_types'].count('full_attention')
    heads, key_dim, value_dim = (config[k] for k in ('linear_num_value_heads', 'linear_key_head_dim', 'linear_value_head_dim'))
    q_heads, kv_heads, attn_dim = (config[k] for k in ('num_attention_heads', 'num_key_value_heads', 'head_dim'))

    # Count every dense matrix product once per new token. The tied embedding
    # is counted once as the output projection; an input embedding is a lookup.
    matrix_counts = {
        'All 24 SwiGLU MLPs': layers * 3 * h * intermediate,
        '18 DeltaNet projection sets, including a/b': linear_layers * (5*h*h + 2*h*heads),
        'Six gated full-attention projection sets': full_layers * h * (3*q_heads*attn_dim + 2*kv_heads*attn_dim),
        'Tied embedding / vocabulary output': h*vocab,
    }
    matrix_total = sum(matrix_counts.values())
    assert matrix_total == sum(prod(v['shape']) for v in text_tensors.values() if len(v['shape']) == 2)
    other_count = text_parameters - matrix_total
    weight_formats = []
    for name, group, scale_bytes, global_bytes in [
        ('INT4, group 128, BF16 scale', 128, 2, 0),
        ('INT4, group 64, BF16 scale', 64, 2, 0),
        ('INT4, group 32, BF16 scale', 32, 2, 0),
        ('MXFP4, group 32, E8M0 scale', 32, 1, 0),
        ('NVFP4, group 16, E4M3 + tensor scale', 16, 1, 4),
    ]:
        payload = 0
        scales = 0
        for v in major.values():
            rows, cols = v['shape']
            payload += rows * ceil(cols / 2)
            scales += rows * ceil(cols / group) * scale_bytes + global_bytes
        total = payload + scales + retained_bytes
        weight_formats.append({'format': name, 'group_size': group,
                               'bits_per_quantized_value': 4 + 8*scale_bytes/group,
                               'payload_bytes': payload, 'scale_bytes': scales,
                               'retained_precision_bytes': retained_bytes, 'total_bytes': total})
    weight_bytes = weight_formats[1]['total_bytes']
    state_elements = linear_layers * heads * key_dim * value_dim
    conv_bytes = linear_layers * (2*config['linear_num_key_heads']*key_dim + heads*value_dim) * config['linear_conv_kernel_dim'] * 2
    kv_bytes_per_token = full_layers * 2 * kv_heads * attn_dim * 2
    recurrence_macs = 3 * state_elements
    conv_macs = linear_layers * (2*config['linear_num_key_heads']*key_dim + heads*value_dim) * config['linear_conv_kernel_dim']
    contexts = []
    for tokens in [2048, 8192, 32768, config['max_position_embeddings']]:
        kv_bytes = tokens * kv_bytes_per_token
        attention_macs = full_layers * 2 * q_heads * attn_dim * tokens
        contexts.append({'tokens': tokens, 'kv_bytes_bf16': kv_bytes,
                         'recurrent_bytes_fp32': state_elements * 4,
                         'recurrent_bytes_16bit': state_elements * 2,
                         'conv_bytes_bf16_four_slots': conv_bytes,
                         'sequence_bytes_fp32_state': kv_bytes + state_elements*4 + conv_bytes,
                         'decode_qk_av_macs': attention_macs,
                         'decode_counted_macs': matrix_total + recurrence_macs + conv_macs + attention_macs})
    bandwidth = []
    for ctx in contexts[:3]:
        # B=1, all packed weights streamed once, all KV read once, all FP32
        # recurrent state loaded/stored once through a local scratchpad.
        traffic = weight_bytes + ctx['kv_bytes_bf16'] + 2*state_elements*4 + kv_bytes_per_token
        bandwidth.append({'tokens': ctx['tokens'], 'modeled_bytes_per_decode_token': traffic,
                          'upper_bound_tokens_per_second': {str(bw): bw*1e9/traffic for bw in [10,25,50]},
                          'effective_gb_per_second_for_20_tokens_per_second': traffic*20/1e9})
    prefill = []
    for tokens in [2048,8192,32768]:
        prefill.append({'tokens': tokens,
                        'dense_macs_last_logits_only': (matrix_total-h*vocab)*tokens + h*vocab,
                        'causal_qk_av_macs': full_layers*q_heads*attn_dim*tokens*(tokens+1),
                        'serial_recurrence_macs': recurrence_macs*tokens,
                        'naive_one_layer_score_bytes_bf16': q_heads*tokens*tokens*2})
    report = {'model_revision': metadata['sha'], 'scope': 'Text decoder, no vision or MTP execution',
              'full_checkpoint_parameters': full_parameters, 'text_parameters': text_parameters,
              'quantized_major_matrix_parameters': quant_parameters,
              'retained_precision_parameters': text_parameters-quant_parameters,
              'matrix_macs_per_decode_token': matrix_counts, 'other_text_parameters': other_count,
              'weight_formats': weight_formats, 'contexts': contexts, 'bandwidth_scenarios': bandwidth,
              'prefill': prefill,
              'assumptions': ['BF16 KV cache; FP32 recurrent state for bandwidth baseline',
                              'Four BF16 convolution slots per channel reserved',
                              'INT4 group 64 and BF16 scales for bandwidth baseline',
                              'Small a/b gate matrices, convolution and norms keep source precision',
                              'No zero-points, alignment padding, allocator reserve or duplicate layouts',
                              'No measured clock, power, quality or system throughput claim'],
              'source_sha256': {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'sources').glob('*.json'))}}
    tables = {
        'TENSOR_TABLE': table(['Text component','Parameters','Dense GMAC per decoded token'],
                             [[name,f'{n:,}',f'{n/1e9:.4f}'] for name,n in matrix_counts.items()] +
                             [['Convolution, norms and scalar parameters',f'{other_count:,}','Counted separately'],
                              ['Text decoder total',f'{text_parameters:,}',f'{matrix_total/1e9:.4f} (matrix products only)']]),
        'WEIGHT_TABLE': table(['Packing scenario','Bits per quantized value with block scale','Total GB','Total GiB'],
                             [[x['format'],f"{x['bits_per_quantized_value']:.3f}",f"{x['total_bytes']/1e9:.4f}",f"{x['total_bytes']/GIB:.4f}"] for x in weight_formats]),
        'CONTEXT_TABLE': table(['Context tokens','BF16 KV MiB','FP32 recurrent MiB','Total sequence MiB, including conv','16-bit recurrent alternative MiB'],
                               [[f"{x['tokens']:,}",f"{x['kv_bytes_bf16']/MIB:,.0f}",'18',f"{x['sequence_bytes_fp32_state']/MIB:,.3f}",'9'] for x in contexts]),
        'BANDWIDTH_TABLE': table(['Context','Modeled GB per decoded token','10 GB/s upper bound tok/s','25 GB/s upper bound tok/s','50 GB/s upper bound tok/s'],
                                [[f"{x['tokens']:,}",f"{x['modeled_bytes_per_decode_token']/1e9:.3f}"] + [f"{x['upper_bound_tokens_per_second'][str(bw)]:.1f}" for bw in [10,25,50]] for x in bandwidth]),
        'PREFILL_TABLE': table(['Prompt tokens','Dense TMAC, last logits only','Causal full-attention TMAC','One naive score matrix MiB, one layer'],
                              [[f"{x['tokens']:,}",f"{x['dense_macs_last_logits_only']/1e12:.3f}",f"{x['causal_qk_av_macs']/1e12:.3f}",f"{x['naive_one_layer_score_bytes_bf16']/MIB:,.0f}"] for x in prefill])
    }
    return report, tables


def build():
    report, tables = calculate()
    (ROOT/'model-budget.json').write_text(json.dumps(report, indent=2)+'\n')
    (ROOT/'budget-tables.md').write_text('# Calculated planning tables\n\nGenerated by model_budget.py; assumptions and exact values are in model-budget.json.\n\n' + '\n\n'.join('## '+k.replace('_',' ').title()+'\n\n'+v for k,v in tables.items())+'\n')
    return tables


if __name__ == '__main__':
    build()
    print('Calculated model-budget.json and budget-tables.md from pinned metadata.')
