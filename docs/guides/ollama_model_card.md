| Model Name         | Model Size (GB) | Context Length (tokens) | Function Calling Support? | Notes/References                                                                                  |
|--------------------|-----------------|------------------------|--------------------------|---------------------------------------------------------------------------------------------------|
| moondream:latest   | 1.74            | Unknown                | Unknown                  | No public info on context or tool-calling.                                                        |
| qwen2.5vl:7b       | 5.97            | 32k (est.)             | Unlikely                 | Vision-language; tool-calling not documented.                                                     |
| qwen2.5vl:32b      | 21.16           | 32k (est.)             | Unlikely                 | Vision-language; tool-calling not documented.                                                     |
| phi4:latest        | 9.05            | 128k (est.)            | Yes (mini/multimodal)    | Phi-4-mini & multimodal support tool-calling.                                                     |
| devstral:latest    | 14.33           | 32k (est.)             | Yes (if \"small\")       | Devstral Small supports tool-calling; check your variant.                                         |
| gemma3:27b         | 17.40           | 8k–32k (varies)        | Yes                      | Gemma 3 supports tool-calling (may require careful prompting).                                    |
| llava:7b           | 4.73            | 8k–32k (varies)        | Unlikely                 | Vision-language; tool-calling not documented.                                                     |
| codegemma:latest   | 5.01            | 8k–32k (varies)        | Unlikely                 | Code focus; tool-calling not documented.                                                          |
| qwen2.5-coder:32b  | 19.85           | 32k (est.)             | Possible                 | Not explicitly listed, but QwQ-32B (related) supports tool-calling.                               |
| qwq:32b            | 19.85           | 32k (est.)             | Yes                      | QwQ-32B supports structured outputs and function calling.                                         |
| qwen2.5-coder:14b  | 8.99            | 32k (est.)             | Possible                 | Not explicitly listed.                                                                            |
| deepseek-r1:70b    | 42.52           | 32k–128k (varies)      | Yes                      | Recent info confirms DeepSeek R1 supports function calling (may require frameworks like BAML).    |
| mistral-nemo:12b   | 7.07            | 32k (est.)             | Yes                      | Mistral Nemo supports function calling.                                                           |
| mistral-small:22b  | 12.57           | 32k (est.)             | Yes                      | Mistral Small supports function calling.                                                          |
| mistral:latest     | 4.11            | 32k (est.)             | Yes (if Large/Medium/Small/Instruct) | Mistral Large, Medium, Small, and Instruct support function calling.                              |

**Notes:**
- **Model Size** is from your Ollama server's output (converted from bytes to GB, rounded to two decimals).
- **Context Length** is the best public estimate; actual may vary by Ollama config and hardware.
- **Function Calling**: "Possible" means related models support it, but not confirmed for this exact variant. 