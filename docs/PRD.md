# Product Requirement Document (PRD) - Advanced AI Chatbot

## 1. 產品概覽與目標 (Product Overview)
*   **核心價值**：建立一個具備「檔案感知」、「精準記憶」與「執行能力 (Tool Use)」的生產力工具。
*   **目標受眾**：需要處理大量文本、追蹤多個專案上下文、且希望 AI 能直接執行外部指令的開發者或知識工作者。

## 2. 功能規格 (Functional Specifications)

### A. 對話與狀態管理 (Dialogue & State)
*   支援多個獨立聊天室 (Session)，每個 Session 擁有獨立的對話上下文。
*   實現 N 筆最近訊息的緩存，支援多輪深度對話。

### B. 訊息系統 (Message System)
*   每一筆訊息包含 `role`, `content`, `timestamp` 欄位。
*   支援附加檔案 (Image/File) 參考。

### C. 檔案上傳 (Multi-modal)
*   使用者可上傳本地檔案（PDF, TXT）或圖片。
*   AI 需能根據上傳內容進行分析與回覆。

### D. 回答控制 (Execution Control)
*   **重新生成 (Regenerate)**：重試最後一次請求。
*   **中止回應 (Abort)**：中斷串流輸出。

### E. 記憶機制 (Memory)
*   儲存使用者偏好（如：編程語言、語氣設定）。
*   實現跨 Session 的資訊持續性。

### F. 工具整合 (Tool Use)
*   初始整合：**Google 搜尋 (SerpApi)** 或 **本地計算器**。
*   系統需具備擴展更多工具的能力。

## 3. AI 規格 (AI Specifications)
*   **模型選擇**：Claude 3.5 Sonnet (首選，具備強大推理與工具 call 能力)。
*   **輸出格式**：預設為 Markdown 串流輸出，特定指令輸出 JSON。

## 4. 異常處理 (Fallback)
*   當 AI Token 超限時，自動摘要前 20 筆對話歷史。
*   當工具執行失敗時，向使用者回報具體錯誤而非胡謅。
