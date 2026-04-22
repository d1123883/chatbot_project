# Model Configuration & Optimization (Models)

## 1. 核心模型選型
針對此專案的需求（需處理複雜工具指令與檔案上傳），選用以下模型：

*   **Claude 3.5 Sonnet**: 作為預設主模型。
    *   **理由**: 領先的工具調用 (Function Calling) 準確度，極佳的寫作語氣，以及支援 Vision (處理上傳圖片)。
*   **GPT-4o-mini**: 作為備用/輕量化任務模型（例如對話標題自動生成）。

## 2. 推理參數配置 (Inference Settings)

| 場景 | 模型 | Temperature | Max Tokens |
| :--- | :--- | :--- | :--- |
| **一般對話** | Claude 3.5 | 0.7 | 4096 |
| **工具執行** | Claude 3.5 | 0.0 | 2048 |
| **摘要與記憶萃取** | GPT-4o-mini | 0.3 | 1024 |

## 3. 系統提示詞框架 (System Prompt)

```text
You are a highly capable AI Assistant. 
- You have access to a session-based memory of user preferences.
- You can execute tools if needed.
- When answering, be concise and use Markdown.
- If a user uploads an image, analyze it before responding.
```

## 4. Token 優化策略
*   **對話滾動**: 僅保留最近 15 筆 Message 進入 Context。
*   **摘要壓縮**: 之前的歷史對話緩存為一段 Summary，以節省 Token 消耗。
