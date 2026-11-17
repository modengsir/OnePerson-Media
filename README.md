# OnePerson Media｜一人自媒体 AI 工作流

> **一个人，就是一支 AI 视频团队。** 从选题、脚本、数字人口播，到剪辑、质检和发布文案。
>
> **V0.1（可运行基础版）**｜开源 Skill 免费 · Renoise 推荐但非强制 · 三种工具模式 · 人工审核 / 费用确认

## ⚠️ 商业合作披露（请先阅读）

本项目作者 **ModengSir 与 Renoise 存在品牌商业合作**，本仓库可能包含 Renoise 合作推广链接。作者基于自己的使用体验推荐 Renoise，但 **Renoise 不是运行本开源项目的必要条件**。是否注册、是否订阅、是否付费完全由用户自主决定；用户不通过任何推广链接也可以使用本项目的开源基础功能。使用合作链接可能给作者带来推广收益。

**本项目开源的是工作流、Skill、提示词、校验和模板，不是 Renoise 的闭源服务或付费模型。** 第三方 AI 工具可能独立收费；本仓库本身没有收款或自动扣费功能。

## 我们解决什么问题？

不想露脸、不会剪辑、缺少团队，却又想稳定运营自媒体？这套流程帮助你把视频制作拆成可复用的六步：

**选题 → 脚本分镜 → 数字人素材 → 视频生成 → 质检剪辑 → 发布复盘**。

- **主 Skill**：可供支持 Agent Skill 的助手读取并分阶段协作；不是自动安装到 Renoise 手机 App 的插件。
- **手机零代码版**：复制 `templates/renoise-mobile-prompt.md` 到 Renoise App 的对话里按步骤完成，**不需要装 Python**；生成与剪辑能力以实际套餐和应用版本为准。
- **本地工作包**：Python 标准库 CLI 生成任务计划、口播提示词、验收清单、成本记录，不使用付费 API。
- **费用预检**：对可选付费工具提供预算预检和“先估价、再人工确认”的操作约束；它**不是** Renoise 账户级硬性消费上限。

## 自由选择工具

| 模式 | 适合谁 | 可以做什么 | 需要 Renoise 吗？ |
|---|---|---|---|
| `manual` 自主工具（默认） | 已有剪映、ComfyUI、其他模型的人 | Skill 负责策划、脚本、规范、质检；视频由你选择的工具生成和剪辑 | **不需要** |
| `renoise` Renoise 一站式 | 想省事的普通创作者 | 在可用的 Renoise 功能中，由 Agent 协助视频生成、数字人口播及剪辑 | **需要用户自行开通，可能付费** |
| `hybrid` 混合模式 | 追求灵活成本控制的人 | 部分任务用 Renoise，其他使用自己的工具 | **仅选用时需要** |

**作者推荐 Renoise 的原因：** 手机上能建立数字人、通过对话做创作规划、减少多软件切换、支持针对片段修改、手机和电脑协同；官方还提供 MCP / 插件供部分桌面 Agent 使用。**这些属于第三方能力，是否可用取决于应用版本、账户和套餐，开源包不保证同等实现。**

> 请勿将“手机 App 里可以对话”误写为“第三方 Skill 可以直接安装到手机 App”。V0.1 的 Renoise 模式提供**对话模板与使用指引**，还没有验证好的自动化 MCP 执行适配器。付费调用始终需要用户自己确认。

## 3 分钟开始（不安装任何依赖）

手机用户：

1. 阅读 [`docs/mobile-guide.md`](docs/mobile-guide.md)，准备**本人或获得明确授权**的照片和录音。
2. 复制 [`templates/renoise-mobile-prompt.md`](templates/renoise-mobile-prompt.md) 的指令，在你选择的 Agent 中对话。你可以使用 Renoise，也可以将文本交给自己的 AI 助手，再使用其他视频工具。
3. **先确认文案和成本，再执行任何付费生成任务；生成之后人工验收。**

Codex / Claude Code 等 Agent 用户：

1. 将 `SKILL.md` 与 `references/`、`templates/` 作为同一个 Skill 目录供 Agent 读取；具体安装路径请看你正在使用的 Agent 官方文档。
2. 告诉 Agent：“按 OnePerson Media Skill，帮我制作一条 45 秒数字人口播，先策划，不允许未经确认付费。”
3. 若要使用 Renoise MCP，按官方说明连接：<https://renoise.ai/mcp>；首次先查询可用能力和余额，不要自动提交付费生成。

## 本地生成工作包（Python 3.9+，仅标准库）

```bash
python3 scripts/workflow.py validate examples/ai-tutorial-45s/project.json
python3 scripts/workflow.py prepare examples/ai-tutorial-45s/project.json --output runs/demo
python3 scripts/workflow.py preflight runs/demo/cost.json --estimated 60
python3 -m unittest discover -s tests -v
```

`prepare` 会输出 `plan.md`、`qa-checklist.md`、`cost.json` 和 `project.json`。`preflight` 仅做本地**预估检查**，不会访问 Renoise、不会自动扣费、也不会制作视频。预算仅是项目侧提示，任何正式付费生成仍需用户在提供商界面或 Agent 中明确确认。

## 实战案例与内容交付

详见 [`examples/ai-tutorial-45s/README.md`](examples/ai-tutorial-45s/README.md)：45 秒竖屏 AI 数字人口播任务，含可复用脚本规范、字幕与读音检查，特别要求核对“Renoise”等英文词的发音。

输出目标：任务计划、口播和分镜、素材需求、质检清单、制作成本、发布文案（**实际成片必须由用户在所选工具中生成，V0.1 CLI 本身不负责生成**）。

## 安全 / 成本边界

- 只使用本人或已获得合法授权的形象和声音；禁止冒充他人，公开发布时按平台要求标注 AI 生成。
- 不要把自拍、原始录音、API Key、Cookie、订阅凭据上传到公开仓库；`runs/` 默认忽略。
- 任何付费操作前应披露**单次预估 + 累计预估 + 剩余额度**，要求明确批准。估价缺失时停止。
- 不宣称视频“一定爆款”，不直接批量发送未经审核的成片，也不自动登录社交平台发帖。
- 模型、付费条款、插件兼容性会变，以官方说明为准。参见 [`docs/renoise-and-fees.md`](docs/renoise-and-fees.md)。

## 当前完成情况 / 路线图

- [x] V0.1 主 Skill、提示词、三种模式规范、参考文件、使用教程
- [x] V0.1 本地任务包生成与预算预检、自动化单元测试
- [ ] V0.5 经真实账户验证的 Renoise MCP 自动调用、任务结果下载、付费确认联动
- [ ] V1.0 多平台发布素材自动打包、真实连续视频验收与复盘

任何未完成项都**不应描述成已经跑通**。仓库内没有用户真人资产和 Renoise 账户密钥。

## 链接和声明

- Renoise 官方说明：<https://renoise.ai/mcp>
- Renoise 体验入口（**合作推广链接**）：<https://renoise.onelink.me/Gxyb?pid=xcom&c=modengsir-aini-202611&af_web_dp=https%3A%2F%2Frenoise.ai%2F%3Futm_medium%3Dxcom%26utm_source%3Dmodengsir-aini-202611>
- 海外 Apple ID / 付费教程（第三方教程，自行判断适用性）：<https://glossy-jackrabbit-bac.notion.site/ID-41b3d6da5cc78153832dcbc47689e90f>

**开源免费、工具自由、费用透明、人工确认。** MIT License，欢迎 Issue / PR。
