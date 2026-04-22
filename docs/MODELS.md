# Model Configuration (Gemini 2.5 Flash)

## 1. 核心模型選型
根據使用者指定，本系統完全採用以下模型：

*   **Gemini 2.5 Flash** (`gemini-2.5-flash`):
    *   **定位**: 高性能、低延遲的次世代大模型。
    *   **優勢**: 具備強大的長上下文處理能力、極速的推理響應，以及優異的工具調用 (Function Calling) 準確度。

## 2. 推理參數配置 (Inference Settings)

| 場景 | 模型 | Temperature | Max Tokens |
| :--- | :--- | :--- | :--- |
| **預設對話** | Gemini 2.5 Flash | 0.8 | 8192 |
| **工具執行** | Gemini 2.5 Flash | 0.0 | 4096 |
| **知識萃取** | Gemini 2.5 Flash | 0.2 | 2048 |

## 3. 系統提示詞框架 (System Prompt)

```text
You are an Advanced AI Assistant powered by Gemini 2.5 Flash.
- You have high reasoning capabilities and follow user instructions strictly.
- You use tools when available to provide factual information.
- You maintain a professional and helpful tone.
```

## 4. 安全設定 (Safety Settings)
*   **Hate Speech**: BLOCK_MEDIUM_AND_ABOVE
*   **Harassment**: BLOCK_MEDIUM_AND_ABOVE
*   **Sexually Explicit**: BLOCK_MEDIUM_AND_ABOVE
*   **Dangerous Content**: BLOCK_MEDIUM_AND_ABOVE
