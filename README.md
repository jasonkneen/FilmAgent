<p align="center">
  <img src="aigc-director-pics/banner.png" width="100%" />
</p>

<h2 align="center">
  <a href="https://github.com/HITsz-TMG/AIGC-Claw">AIGC-Claw: AI 视频生成全流程系统</a>
</h2>

<h4 align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <a href="https://github.com/HITsz-TMG/AIGC-Claw/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/HITsz-TMG/AIGC-Claw?style=flat-square" alt="License">
  </a>
  <a href="https://github.com/HITsz-TMG/AIGC-Claw/stargazers">
    <img src="https://img.shields.io/github/stars/HITsz-TMG/AIGC-Claw?style=flat-square&logo=github" alt="Stars">
  </a>
  <a href="https://github.com/HITsz-TMG/AIGC-Claw/fork">
    <img src="https://img.shields.io/github/forks/HITsz-TMG/AIGC-Claw?style=flat-square&logo=github" alt="Forks">
  </a>
  <img src="https://img.shields.io/badge/Python-3.9+-purple.svg" alt="Python">
</h4>

<p align="center">
  <b>AI 视频生成全流程系统 | 通过 6 个阶段将用户想法转化为完整视频</b>
</p>

<div align="center">

🎯  [**项目主页**](https://github.com/HITsz-TMG/AIGC-Claw)  :octocat:  [**代码**](https://github.com/HITsz-TMG/AIGC-Claw)  📝  [**文档**](./aigc-director/SKILL.md)

<a href="https://trendshift.io/repositories/12871" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12871" alt="HITsz-TMG%2FFilmAgent | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>

---

## 📖 项目介绍

AIGC-Claw 是一个基于 OpenClaw 平台的 AI 视频生成系统，通过 6 个阶段将用户的创意想法转化为完整的视频作品。

系统模拟了影视制作的完整流程：从剧本创作、角色设计、分镜规划，到参考图生成、视频生成，最后进行后期剪辑。每个阶段完成后都会展示产物，等待用户确认后继续下一阶段，确保用户对最终视频有完整的把控。

AIGC-Claw 支持多种 AI 模型接入，包括阿里云 DashScope、字节跳动 Seedream、即梦 Jimeng、快手可灵 Kling、DeepSeek、OpenAI 和 Google Gemini，可根据需求灵活选择。

---

## 📺 AIGC-Claw

<details>
<summary><b>Web 前端界面</b></summary>
<div align="center">

| | |
|:---:|:---:|
| ![Stage 1](./aigc-director-pics/workflow_demo/stage_1.png) | ![Stage 2](./aigc-director-pics/workflow_demo/stage_2.png) |
| ![Stage 3](./aigc-director-pics/workflow_demo/stage_3.png) | ![Stage 4](./aigc-director-pics/workflow_demo/stage_4.png) |
| ![Stage 5](./aigc-director-pics/workflow_demo/stage_5.png) | ![Stage 6](./aigc-director-pics/workflow_demo/stage_6.png) |

</div>
</details>

<details>
<summary><b>微信交互</b></summary>
<div align="center">

| | | | |
|:---:|:---:|:---:|:---:|
| ![WeChat 1](./aigc-director-pics/wechat_demo/wechat_1.jpg) | ![WeChat 2](./aigc-director-pics/wechat_demo/wechat_2.jpg) | ![WeChat 3](./aigc-director-pics/wechat_demo/wechat_3.jpg) | ![WeChat 4](./aigc-director-pics/wechat_demo/wechat_4.jpg) |

</div>
</details>

<details>
<summary><b>飞书交互</b></summary>
<div align="center">

| | | | |
|:---:|:---:|:---:|:---:|
| ![Feishu 1](./aigc-director-pics/feishu_demo/feishu_1.jpg) | ![Feishu 2](./aigc-director-pics/feishu_demo/feishu_2.jpg) | ![Feishu 3](./aigc-director-pics/feishu_demo/feishu_3.jpg) | ![Feishu 4](./aigc-director-pics/feishu_demo/feishu_4.jpg) |

</div>
</details>

---

## 💥 News

- `2026/3/27`: 🚀 AIGC-Claw 正式发布，支持 6 阶段视频生成全流程

---

## ✨ 功能特性

| 阶段 | 功能 | 描述 |
|:---:|---|---|
| 1 | 🎭 **剧本生成** | 输入创意自动生成结构化剧本，支持电影(4幕)和微电影(1幕)模式 |
| 2 | 👤 **角色设计** | AI 生成角色设定图（四视图）和场景背景图 |
| 3 | 🎬 **分镜设计** | 智能拆分镜头脚本，设计镜头语言 |
| 4 | 🖼️ **参考图生成** | 为每个镜头生成高精度参考图 |
| 5 | 🎥 **视频生成** | 图生视频 / 文生视频 |
| 6 | ✂️ **后期剪辑** | 自动拼接视频片段，添加转场效果 |

### 🌟 核心能力

- **多模型支持**：集成阿里云 DashScope、字节跳动 Seedream、即梦 Jimeng、快手可灵 Kling、DeepSeek、OpenAI、Google Gemini
- **Agent 架构**：基于 OpenClaw 平台的可调用 Skill，全流程自动化
- **交互式确认**：每个阶段完成后展示产物，等待用户确认后继续
- **临时工作台**：支持单独调用 LLM、VLM、文生图、图生图、视频生成

---

## 🛠️ 技术栈

<div align="center">

| 前端 | 后端 | AI 模型 |
|:---:|:---:|:---:|
| <img src="https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js"> | <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi"> | <img src="https://img.shields.io/badge/DashScope-FF6B6B?style=flat-square"> |
| TypeScript | Python 3.9+ | OpenAI |
| Tailwind CSS | Uvicorn | Gemini |

</div>

---

## 🚀 快速开始

### 方式一：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/HITsz-TMG/AIGC-Claw.git
cd AIGC-Claw

# 2. 配置并启动后端
cd aigc-director/aigc-claw/backend

# 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动后端
python api_server.py
# 服务运行在 http://localhost:8000
```

```bash
# 3. 配置并启动前端（新终端）
cd aigc-director/aigc-claw/frontend
npm install
npm run build
npm start
# 访问 http://localhost:3000
```

### 方式二：OpenClaw 自动配置

向 OpenClaw 发送消息：

```
帮我克隆git仓库：https://github.com/HITsz-TMG/AIGC-Claw.git
然后把AIGC-Claw中的aigc-director文件夹递归复制到workspace/skills中，用作AIGC相关的skill
```

使用时建议指明 "使用 aigc-director"：

```
你用aigc-director来帮我生成一个视频，内容是"一条狗的使命"
```

### 方式三：通过 ClawHub 安装

请确保本地安装了clawhub-cli

打开终端，输入命令，所有询问均选择yes

```bash
clawhub install aigc-director
```

安装完成后，ClawHub 会将 `aigc-director` 复制到 `workspace/skills`（或指定的 skills 目录）。

之后可以参考方式一手动安装自行构建项目并运行，也可以使用openclaw完成后续项目构建。

在第一次使用 `aigc-director` 时，如果没有手动构建项目，openclaw会自动构建前后端并运行，无需手动初始化（构建项目需要配置环境和编译，请耐心等待）。


---

## 📊 工作流

<div align="center">

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   剧本生成   │ → │  角色设计   │ → │  分镜设计   │ → │ 参考图生成  │ → │  视频生成   │ → │  后期剪辑   │
│   Script    │   │  Character  │   │ Storyboard  │   │  Reference  │   │    Video   │   │    Post     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ↓                  ↓                  ↓                  ↓                  ↓                  ↓
   🎭 剧本产出        👤 角色/场景        🎬 分镜列表        🖼️ 参考图          🎥 视频片段        🎬 最终成片
```

</div>

---

## 📁 项目结构

```
AIGC-Claw/
├── aigc-director/                    # 🎯 OpenClaw Agent Skill
│   ├── SKILL.md                      # Agent 工作流规则定义
│   ├── CLAUDE.md                     # Claude Code 开发指引
│   ├── README.md                     # 项目说明（本文件）
│   ├── references/                   # API 参考文档
│   │   ├── init_project/             # 项目初始化指南
│   │   ├── run_project/              # 服务启动指南
│   │   ├── workflow/                 # 六阶段工作流 API
│   │   ├── sandbox/                  # 临时工作台 API
│   │   └── send_message/             # 消息推送集成
│   └── aigc-claw/                    # 💻 实际代码项目
│       ├── backend/                  # Python FastAPI 后端
│       │   ├── api_server.py         # API 入口
│       │   ├── core/                 # 核心模块
│       │   │   ├── orchestrator.py   # 工作流引擎
│       │   │   └── agents/           # 6 个阶段 Agent
│       │   └── tool/                 # 外部 API 客户端
│       └── frontend/                 # Next.js 前端
├── FilmAgent/                        # 🎬 另一个 Agent（待开发）
└── README.md                         # 主 README
```

---

## 🔧 配置说明

### 环境要求

- **Python**: 3.9+
- **Node.js**: 18+
- **npm**: 9+

### 后端环境变量

在 `aigc-claw/backend/.env` 中配置：

```bash
# LLM 配置
LLM_MODEL=qwen3.5-plus
VLM_MODEL=qwen-vl-plus

# 图像生成
IMAGE_T2I_MODEL=doubao-seedream-5-0-260128
IMAGE_IT2I_MODEL=doubao-seedream-5-0-260128

# 视频生成
VIDEO_MODEL=wan2.6-i2v-flash
VIDEO_RATIO=16:9

# API Keys
DASHSCOPE_API_KEY=your_key
ARK_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
```

### 可用模型

| 类型 | 模型 |
|:---:|:---|
| **LLM** | qwen3.5-plus, deepseek-chat, gpt-4o, gemini-2.5-flash |
| **VLM** | qwen-vl-plus, gemini-2.5-flash-image |
| **文生图** | doubao-seedream-5-0, jimeng_t2i_v40, wan2.6-t2i |
| **图生图** | doubao-seedream-5-0, jimeng_t2i_v40, wan2.6-image |
| **视频生成** | wan2.6-i2v-flash, kling-v3, jimeng_ti2v_v30_pro |

---

## 📚 文档

<div align="center">

| 文档 | 描述 |
|:---:|:---|
| 📖 [SKILL.md](./aigc-director/SKILL.md) | OpenClaw Agent 工作流规则 |
| 📖 [CLAUDE.md](./aigc-director/CLAUDE.md) | Claude Code 开发指引 |
| 📖 [README 文档](./README.md) | 六阶段工作流 API |

</div>

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

---

## 📄 许可证

MIT License - 查看 [LICENSE](./LICENSE) 了解详情

---

## 📚 参考文献

| 重要图示 | 论文信息（标题 / Paper / GitHub / Citation） |
|:---:|---|
| <img src="https://raw.githubusercontent.com/HITsz-TMG/Anim-Director/main/AniMaker/assets/pipeline.png" width="320" alt="AniMaker pipeline"/> | **AniMaker: Multi-Agent Animated Storytelling with MCTS-Driven Clip Generation**<br>Paper: [https://doi.org/10.1145/3757377.3764009](https://doi.org/10.1145/3757377.3764009)<br>GitHub: [https://github.com/HITsz-TMG/Anim-Director/tree/main/AniMaker](https://github.com/HITsz-TMG/Anim-Director/tree/main/AniMaker)<br>Citation: `@inproceedings{shi2025animaker, title={AniMaker: Multi-Agent Animated Storytelling with MCTS-Driven Clip Generation}, author={Shi, Haoyuan and Li, Yunxin and Chen, Xinyu and Wang, Longyue and Hu, Baotian and Zhang, Min}, booktitle={Proceedings of the SIGGRAPH Asia 2025 Conference Papers}, pages={1--11}, year={2025}, doi={10.1145/3757377.3764009}}` |
| <img src="https://github.com/HITsz-TMG/FilmAgent/blob/main/pics/framework.png?raw=true" width="320" alt="FilmAgent framework"/> | **FilmAgent: Automating Virtual Film Production Through a Multi-Agent Collaborative Framework**<br>Paper: [https://doi.org/10.1145/3681758.3698014](https://doi.org/10.1145/3681758.3698014)<br>GitHub: [https://github.com/HITsz-TMG/AIGC-Claw/blob/main/FilmAgent.md](https://github.com/HITsz-TMG/AIGC-Claw/blob/main/FilmAgent.md)<br>Citation: `@inproceedings{xu2024filmagent_techcomm, title={FilmAgent: Automating Virtual Film Production Through a Multi-Agent Collaborative Framework}, author={Xu, Zhenran and Wang, Jifang and Wang, Longyue and Li, Zhouyi and Shi, Senbao and Hu, Baotian and Zhang, Min}, booktitle={SIGGRAPH Asia 2024 Technical Communications}, pages={1--4}, year={2024}, doi={10.1145/3681758.3698014}}` |
| <img src="https://github.com/HITsz-TMG/Anim-Director/blob/main/Anim-Director/assets/demos/Tim/AnimDirector%28Ours%29/Scene_1_Segment_1.jpg?raw=true" width="320" alt="Anim-Director result"/> | **Anim-Director: A Large Multimodal Model Powered Agent for Controllable Animation Video Generation**<br>Paper: [https://doi.org/10.1145/3680528.3687688](https://doi.org/10.1145/3680528.3687688)<br>GitHub: [https://github.com/HITsz-TMG/Anim-Director/tree/main/Anim-Director](https://github.com/HITsz-TMG/Anim-Director/tree/main/Anim-Director)<br>Citation: `@inproceedings{li2024anim, title={Anim-director: A large multimodal model powered agent for controllable animation video generation}, author={Li, Yunxin and Shi, Haoyuan and Hu, Baotian and Wang, Longyue and Zhu, Jiashun and Xu, Jinyi and Zhao, Zhen and Zhang, Min}, booktitle={SIGGRAPH Asia 2024 Conference Papers}, pages={1--11}, year={2024}, doi={10.1145/3680528.3687688}}` |
