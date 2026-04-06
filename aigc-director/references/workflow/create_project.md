# 创建项目

创建一个新的视频生成项目。

## 请求与响应

### 请求

```bash
curl -X POST "http://localhost:8000/api/project/start" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "故事内容",
    "style": "anime",
    "video_ratio": "16:9",
    "episodes": 4,
    "llm_model": "qwen3.5-plus",
    "vlm_model": "qwen-vl-plus",
    "image_t2i_model": "doubao-seedream-5-0",
    "image_it2i_model": "doubao-seedream-5-0",
    "video_model": "wan2.6-i2v-flash",
    "enable_concurrency": true,
    "web_search": false
  }'
```

### 响应

```json
{
  "session_id": "xxx",
  "status": "stage_completed",
  "params": {
    "idea": "故事内容",
    "style": "anime",
    "llm_model": "qwen3.5-plus",
    "vlm_model": "qwen-vl-plus",
    "episodes": 4
  }
}
```

---

## 停点流程

本项目采用 **Agent 驱动的 6 阶段流水线**。系统在每一阶段完成后会进入 **停点 (Stop Event)**，等待用户确认后继续执行。

| 阶段 | 停点 ID | 阶段内部步骤 (Phase) | 说明 |
|------|---------|-----------------------|------|
| 1 | 2 | script_generation | 剧本生成：产出全剧本、人物设定、环境设定 |
| 2 | 3 | character_design | 角色/场景设计：为每个角色/场景生成参考图 |
| 3 | 4 | storyboard | 分镜设计：将剧本拆分为具体镜头 (segments) |
| 4 | 5 | reference_generation | 参考图生成：根据分镜生成首帧控制图 |
| 5 | 6 | video_generation | 视频生成：根据参考图生成动态视频片段 |
| 6 | - | post_production | 后期剪辑：按剧集拼接视频并生成最终成片 |

---

## 全局监听：SSE 进度流

启动项目后，**必须** 立即连接 SSE 端点以接收实时反馈：

```bash
# 执行第一阶段并获取进度
curl -N "http://localhost:8000/api/project/{session_id}/execute/script_generation"
```

SSE 每个事件为一行 JSON：

- `{"type": "progress", "percent": 10, "message": "正在生成剧本..."}`
- `{"type": "stage_complete", "stage": "script_generation", "requires_intervention": true}`
- `{"type": "error", "content": "..."}`

---

## 查看项目状态

随时可以查看当前剧本、分镜或视频的状态：

```bash
curl "http://localhost:8000/api/project/{session_id}/status"
```

---

## 下一步

跳转到 [1. 生成剧本 (script_generation)](create_script.md)。
5. LLM 模型: qwen3.5-plus（默认值）
   - 可选：qwen3.5-plus, deepseek-chat, gpt-4o, gemini-2.5-flash
6. VLM 模型: qwen-vl-plus（默认值）
   - 可选：qwen-vl-plus, gemini-2.5-flash-image
7. T2I 模型: doubao-seedream-5-0（默认值）
   - 可选：doubao-seedream-5-0, wan2.6-t2i, jimeng_t2i_v40
7. I2I 模型: doubao-seedream-5-0（默认值）
   - 可选：doubao-seedream-5-0, wan2.6-image
8. Video 模型: wan2.6-i2v-flash（默认值）
   - 可选：wan2.6-i2v-flash, kling-v3, jimeng_ti2v_v30_pro
9. 联网搜索: false（默认值）
   - 可选：true, false
10. 并发生成: true（默认值）
   - 可选：true, false

> **注意**：
> - **所有参数必须都展示给用户**
> - 根据用户消息渠道选择格式：
>   - 飞书：使用 Markdown 表格
>   - 微信：使用编号列表（微信不支持 Markdown 表格）

---

## 停点1：项目配置确认

在调用 API 创建项目之前，必须展示当前配置并询问用户：

### 展示当前配置

根据用户提供的idea和选择（用户未提及的选项使用默认值），生成配置确认表格：

| 配置项 | 当前值 |
|--------|--------|
| 故事创意 (idea) | [用户的创意内容] |
| 视频风格 (style) | realistic（默认值）或其他用户选择 |
| 剧集数量 (episodes)| 4（默认值）或其他用户选择 |
| 视频比例 (video_ratio) | 16:9（默认值）或其他用户选择 |
| LLM 模型 | qwen3.5-plus（默认值）或其他用户选择 |
| VLM 模型 | qwen-vl-plus（默认值）或其他用户选择 |
| T2I 模型 | doubao-seedream-5-0（默认值）或其他用户选择 |
| I2I 模型 | doubao-seedream-5-0（默认值）或其他用户选择 |
| Video 模型 | wan2.6-i2v-flash（默认值）或其他用户选择 |
| 联网搜索 | false（默认值）|
| 并发生成 | true（默认值）|

### 询问用户

> 当前配置如上，请问是否有需要修改的？
> - 如需修改，请告知具体要修改的项目和新值
> - 如无需修改，请回复"确认"或"确定"

### 循环确认

- 如果用户提出修改 → 记录修改项 → 重新展示更新后的配置 → 再次询问确认
- 直到用户确认无需修改 → 才能调用 API 创建项目

---

## 注意事项

1. **必须询问用户**：在创建项目前，一定要询问用户项目的配置，用户没有提及的选项则使用默认值
2. **检查 API Key**：在创建项目前，必须检查用户选择的模型对应的 API Key 是否已配置

### API Key 检查步骤

```bash
# 1. 读取 .env 文件
cat aigc-claw/backend/.env

# 2. 根据用户选择的模型检查对应 API Key
#    - LLM 模型：检查 DASHSCOPE_API_KEY / DEEPSEEK_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY
#    - 图片模型：检查 ARK_API_KEY / DASHSCOPE_API_KEY / VOLC_ACCESS_KEY/VOLC_SECRET_KEY
#    - 视频模型：检查 DASHSCOPE_API_KEY / VOLC_ACCESS_KEY/VOLC_SECRET_KEY / KLING_ACCESS_KEY/KLING_SECRET_KEY

# 3. 如果缺少 API Key，提醒用户配置
```

### 缺少 API Key 时的处理

如果检测到缺少必要的 API Key，需要告知用户：
1. 缺少哪个平台的 API Key
2. 如何获取（官方链接）
3. 配置位置（`aigc-claw/backend/.env` 文件）
4. 等待用户配置完成后才能继续创建项目

| 平台 | API Key 变量 | 获取链接 |
|------|--------------|----------|
| DeepSeek | `DEEPSEEK_API_KEY` | https://platform.deepseek.com/api_keys |
| 阿里云 DashScope | `DASHSCOPE_API_KEY` | https://bailian.console.aliyun.com/cn-beijing/?tab=home#/home |
| 字节火山方舟 | `ARK_API_KEY` 或 `VOLC_ACCESS_KEY`/`VOLC_SECRET_KEY` | https://www.volcengine.com/product/ark |
| 快手可灵 Kling | `KLING_ACCESS_KEY`/`KLING_SECRET_KEY` | https://klingai.com/cn/dev |

---

## 常见问题

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `curl: (7) Failed to connect` | 后端未运行 | 启动后端服务 |
| `500 Internal Server Error` | API Key 缺失或配置错误 | 检查 `backend/.env` 文件 |
| `404 Not Found` | API 路径错误 | 确认 URL 为 `http://localhost:8000/api/project/start` |