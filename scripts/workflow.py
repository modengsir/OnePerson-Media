#!/usr/bin/env python3
"""OnePerson Media v0.1: prepare a prompt packet and evaluate estimated credits.

This CLI does NOT make network requests or paid model calls.
"""
import argparse
import json
import re
from pathlib import Path

PROVIDERS = {"manual", "renoise", "hybrid"}
PLATFORMS = {"douyin", "xiaohongshu", "youtube", "youtube_shorts", "x", "bilibili"}


def validate_config(data):
    """Return a list of actionable errors. Do not assume consent to paid tools."""
    errors = []
    if not isinstance(data, dict):
        return ["配置必须是 JSON 对象"]
    for key in ("project_id", "topic"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} 必须是非空字符串")
    provider = data.get("provider", "manual")
    if provider not in PROVIDERS:
        errors.append(f"provider 必须是 {', '.join(sorted(PROVIDERS))} 之一")
    if data.get("platform") not in PLATFORMS:
        errors.append(f"platform 必须是 {', '.join(sorted(PLATFORMS))} 之一")
    duration = data.get("duration_seconds")
    if type(duration) is not int or not 15 <= duration <= 180:
        errors.append("duration_seconds 必须是 15～180 之间的整数")
    creator = data.get("creator", {})
    if not isinstance(creator, dict):
        errors.append("creator 必须是对象")
        creator = {}
    for key in ("avatar_authorized", "voice_authorized"):
        if creator.get(key) is not True:
            errors.append(f"必须明确确认 creator.{key}=true；不得默认授权")
    paid = data.get("paid_tools", {})
    if not isinstance(paid, dict):
        errors.append("paid_tools 必须是对象")
        paid = {}
    if paid.get("require_confirmation") is not True:
        errors.append("paid_tools.require_confirmation 必须为 true")
    credits = paid.get("max_estimated_credits")
    if type(credits) is not int or credits < 0:
        errors.append("paid_tools.max_estimated_credits 必须是非负整数")
    if provider in {"renoise", "hybrid"}:
        if paid.get("renoise_opt_in") is not True:
            errors.append("选用 Renoise 或混合模式，必须明确 renoise_opt_in=true")
        if type(credits) is not int or credits <= 0:
            errors.append("付费模式必须设置大于 0 的预计积分预算")
    elif paid.get("renoise_opt_in") is True:
        errors.append("manual 模式不应开启 Renoise 付费授权；请先切换 provider")
    return errors


def safe_slug(value):
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-_")
    return slug[:64] or "oneperson-project"


def build_plan(data):
    creator = data["creator"]
    mode = data.get("provider", "manual")
    return f"""# 视频工作计划（仅供规划，尚未付费生成）

项目：{data['project_id']}
主题：{data['topic']}
平台：{data['platform']}
目标时长：{data['duration_seconds']} 秒
工具模式：{mode}
创作者：{creator.get('display_name','示例创作者')}
受众：{creator.get('audience','普通用户')}
口吻：{creator.get('tone','真实、口语化')}

## 第一轮给 Agent 的指令

你是我的自媒体 AI 导演。请围绕“{data['topic']}”生成三套不同角度的选题方案，每套附 3 秒钩子、受众痛点、45 秒以内可执行的故事结构、可能需要的演示素材。

等我选好方案后，再生成完整口播稿、分镜时间轴、字幕重点，以及需要我提供的数字人/声音资产。**不要在此阶段开始任何付费生成。**

## 第二轮（用户确认脚本后）

核对人物授权、声音授权、画幅和英文术语发音，先给出片段划分、模型建议和逐项预计积分。

- manual：输出适配我自己工具的操作步骤，不调用 Renoise。
- renoise：仅在用户已经自行连接 Renoise 且能力可用时，查询费用并逐项确认后执行。
- hybrid：列出每个任务的所选工具、费用和人工确认点。

## 成片前检查

检查字幕、口型、人物一致性与专有词读音（例如 Renoise）。把问题标注在秒数上，不合格的片段定点修改。最后由用户人工验收。

## 真实性承诺

本工作包没有联网、没有生成视频、没有扣积分；真实消耗与成片效果需人工补充记录。
"""


def qa_template():
    return """# 人工验收清单

- [ ] 脚本已确认，长度适配时长
- [ ] 人像、声音和素材授权已明确
- [ ] 第三方付费任务已估价并单独获批准
- [ ] 数字人脸/发型/衣服一致
- [ ] 口型同步、声音自然
- [ ] 字幕无错字、无遮挡
- [ ] 英文专有名词（尤其 Renoise）读音准确
- [ ] 品牌合作与 AI 生成内容依平台要求披露
- [ ] 创作者已审核最终成片
"""


def fresh_cost(data):
    return {"project_id": data["project_id"], "provider": data.get("provider", "manual"),
            "credit_budget": data["paid_tools"]["max_estimated_credits"],
            "require_confirmation": True, "recorded_actual_credits": 0,
            "events": [], "note": "本地记录与预检；并非第三方平台硬性扣费上限"}


def preflight(cost, estimated, approved=False):
    """Conservative local check for a single *proposed* paid task."""
    if cost.get("provider") == "manual":
        return False, "自主工具模式未允许调用 Renoise 付费任务"
    if type(estimated) is not int or estimated < 0:
        return False, "缺少有效的预计积分，必须停止"
    if approved is not True:
        return False, "尚未取得用户对本次付费任务的明确确认，必须停止"
    spent = cost.get("recorded_actual_credits", 0)
    budget = cost.get("credit_budget", 0)
    if type(spent) is not int or type(budget) is not int or budget <= 0:
        return False, "缺少有效预算记录，必须停止"
    if spent + estimated > budget:
        return False, f"预计累计 {spent + estimated} 积分，超出项目预算 {budget} 积分"
    return True, f"本地预检通过：预计新增 {estimated}，累计不超过 {budget}；仍需在提供商执行前获得真实确认"


def prepare(config_path, output):
    data = json.loads(Path(config_path).read_text(encoding="utf-8"))
    errs = validate_config(data)
    if errs:
        raise ValueError("；".join(errs))
    out = Path(output)
    if out.resolve() == Path.cwd().resolve():
        raise ValueError("不能把项目输出到仓库根目录")
    out.mkdir(parents=True, exist_ok=True)
    for name, contents in {
        "project.json": json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        "plan.md": build_plan(data),
        "qa-checklist.md": qa_template(),
        "cost.json": json.dumps(fresh_cost(data), indent=2, ensure_ascii=False) + "\n",
    }.items():
        p = out / name
        if p.exists():
            raise FileExistsError(f"文件已存在，防止覆盖：{p}")
        p.write_text(contents, encoding="utf-8")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_validate = sub.add_parser("validate", help="校验任务配置")
    p_validate.add_argument("config")
    p_prepare = sub.add_parser("prepare", help="生成不含付费操作的工作包")
    p_prepare.add_argument("config")
    p_prepare.add_argument("--output", required=True)
    p_preflight = sub.add_parser("preflight", help="本地预算预检；不会生成或扣费")
    p_preflight.add_argument("cost_json")
    p_preflight.add_argument("--estimated", type=int, required=True)
    p_preflight.add_argument("--approved", action="store_true", help="仅标记本地审批信息，不代表平台已授权")
    args = parser.parse_args(argv)
    try:
        if args.command in {"validate", "prepare"}:
            data = json.loads(Path(args.config).read_text(encoding="utf-8"))
            errors = validate_config(data)
            if errors:
                print("配置无效：", "；".join(errors))
                return 2
            if args.command == "validate":
                print("配置有效：不会调用付费工具")
            else:
                target = prepare(args.config, args.output)
                print(f"工作包已创建：{target}")
            return 0
        cost = json.loads(Path(args.cost_json).read_text(encoding="utf-8"))
        ok, msg = preflight(cost, args.estimated, args.approved)
        print(("通过" if ok else "停止") + "：" + msg)
        return 0 if ok else 3
    except (ValueError, FileNotFoundError, FileExistsError, json.JSONDecodeError) as e:
        print(f"错误：{e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
