# Tested profiles and model links

Model weights are not included in this repository.

## Upstream model repos

- Qwen base model: <https://huggingface.co/Qwen/Qwen3.6-27B>
- Unsloth GGUF repo: <https://huggingface.co/unsloth/Qwen3.6-27B-GGUF>
- Unsloth tested file: <https://huggingface.co/unsloth/Qwen3.6-27B-GGUF?show_file_info=Qwen3.6-27B-UD-Q6_K_XL.gguf>
- Bartowski GGUF repo: <https://huggingface.co/bartowski/Qwen_Qwen3.6-27B-GGUF>
- Bartowski tested file: <https://huggingface.co/bartowski/Qwen_Qwen3.6-27B-GGUF/blob/main/Qwen_Qwen3.6-27B-Q6_K_L.gguf>

## Profile config source

Machine-readable profile metadata lives in:

```text
configs/tested-profiles.json
```

Launch-script examples live in:

```text
configs/*.sh
```

## Main profiles

| Profile | Model file | Context | KV | Reasoning/template |
|---|---|---:|---|---|
| `unsloth-65k-f16` | `Qwen3.6-27B-UD-Q6_K_XL.gguf` | 65,536 | f16/f16 | no-think |
| `unsloth-65k-q8` | `Qwen3.6-27B-UD-Q6_K_XL.gguf` | 65,536 | q8_0/q8_0 | no-think |
| `unsloth-128k-f16` | `Qwen3.6-27B-UD-Q6_K_XL.gguf` | 131,072 | f16/f16 | no-think |
| `unsloth-128k-q8` | `Qwen3.6-27B-UD-Q6_K_XL.gguf` | 131,072 | q8_0/q8_0 | no-think |
| `bartowski-128k-f16` | `Qwen_Qwen3.6-27B-Q6_K_L.gguf` | 131,072 | f16/f16 | no-think |
| `bartowski-128k-q8` | `Qwen_Qwen3.6-27B-Q6_K_L.gguf` | 131,072 | q8_0/q8_0 | no-think |
| `unsloth-128k-q8-reasoning-on-enable-false-preserve-false` | `Qwen3.6-27B-UD-Q6_K_XL.gguf` | 131,072 | q8_0/q8_0 | `--reasoning on`, `--reasoning-format deepseek`, `enable_thinking:false`, `preserve_thinking:false` |

## Notes from upstream docs

Qwen3.6 documentation describes thinking mode, non-thinking mode, and thinking preservation. It also recommends at least 128K context for preserving thinking capabilities in complex tasks. See the Qwen model card and docs linked above.
