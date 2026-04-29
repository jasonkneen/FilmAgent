# 静态短视频

静态短视频对应 `standard` pipeline。它不调用视频生成模型，而是：

1. 输入创作灵感或完整文案
2. 必要时用 LLM 将创作灵感扩写成旁白
3. 按句号切分旁白
4. 每句生成一张图片
5. 每句生成一段 TTS 音频
6. 用图片和音频合成静态视频片段
7. 拼接成最终视频

## 请求

```bash
curl -X POST "http://localhost:8000/api/pipelines/standard/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "inspiration",
    "text": "一个关于拖延症和自救的短视频灵感",
    "title": "",
    "llm_model": "qwen3.5-plus",
    "image_model": "wan2.7-image",
    "video_ratio": "9:16",
    "tts_voice": "zh-CN-YunjianNeural",
    "tts_speed": 1.2,
    "style_control": "Minimalist black-and-white matchstick figure style illustration, clean lines, simple sketch style",
    "enable_subtitles": true
  }'
```

## 参数说明

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `mode` | | `copy` | `inspiration` 为创作灵感，先经 LLM 构思；`copy` 为完整文案，直接进入 TTS |
| `text` | ✅ | | 创作灵感或完整文案 |
| `title` | | | 可选，留空时由 LLM 根据最终旁白生成 |
| `llm_model` | | 后端默认 | 标题生成和创作灵感扩写使用的 LLM |
| `image_model` | | 后端默认 | 文生图模型，需支持 `text_to_image` |
| `video_ratio` | | `9:16` | 视频比例，支持 `9:16` / `16:9` / `1:1` |
| `tts_voice` | | `zh-CN-YunjianNeural` | Edge TTS 声音 |
| `tts_speed` | | `1.2` | TTS 语速 |
| `style_control` | | 火柴人黑白简笔风 | 作为所有图像提示词的前缀 |
| `enable_subtitles` | | `false` | 是否把标题和字幕直接绘制到静态图片上 |

默认风格控制：

```text
Minimalist black-and-white matchstick figure style illustration, clean lines, simple sketch style
```

## 字幕与标题

静态短视频不依赖 FFmpeg `libass` 烧字幕。开启 `enable_subtitles` 时：

1. 后端先用 Pillow 将标题和当前句字幕绘制到每张图片上
2. 生成 `captioned_image_XX.jpg`
3. 再用带字图片合成视频片段

因此静态短视频的标题/字幕功能只需要 Pillow，不需要 FFmpeg 的 `ass` filter。

## 产物

产物目录：

```text
aigc-claw/backend/code/result/task/{task_id}/
```

常见产物：

| 文件 | 说明 |
|------|------|
| `storyboard.json` | 每句旁白、图片提示词、图片/音频/视频路径 |
| `narration.txt` | 最终旁白文本 |
| `image_XX.*` | 每句旁白生成的原始图片 |
| `captioned_image_XX.jpg` | 开启字幕时生成的带标题/字幕图片 |
| `audio_XX.mp3` | 每句旁白生成的 TTS |
| `video_XX.mp4` | 每句图片+音频合成的静态片段 |
| `final.mp4` | 最终拼接成片 |

## 响应

```json
{
  "task_id": "20260429_170348_a281f881",
  "pipeline": "standard",
  "status": "pending",
  "metadata_url": "/api/tasks/20260429_170348_a281f881",
  "output_dir": "/.../backend/code/result/task/20260429_170348_a281f881"
}
```

任务完成后查询：

```bash
curl "http://localhost:8000/api/tasks/{task_id}"
```

`output.final_video` 指向最终视频。

## 模型能力筛选

```bash
curl "http://localhost:8000/api/models?media_type=image&ability=text_to_image&verified_only=true"
```

## 前端入口

```text
http://localhost:3000/pipelines/standard
```

前端选项：

| 控件 | 说明 |
|------|------|
| 创作灵感 / 完整文案 | 决定输入是否先经 LLM 构思 |
| 标题 | 可选，留空时由 LLM 生成 |
| 添加标题和字幕 | 只作用于静态短视频，会直接画到图片上 |
| 生成配置 | LLM 模型、图片模型、视频比例、TTS 声音、TTS 速度、风格控制 |

## 注意事项

1. 静态短视频不会调用视频生成模型。
2. 完整文案会按所有句号切分，建议每句不要太长。
3. 图像提示词会自动追加“不要生成文字、logo、水印、标签”等约束。
4. 如果开启标题和字幕，会额外生成带字图片产物。
