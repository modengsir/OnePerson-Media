# 将项目发布到个人 GitHub

如果仓库尚未创建，可按以下手动步骤操作（需要你本人拥有 GitHub 写入权限）。

1. GitHub 新建公开仓库 `OnePerson-Media`，**不要**自动初始化 README / License（本项目已经有）。
2. 下载本项目压缩包并解压到 `OnePerson-Media` 目录。
3. 在 Mac 终端切换到该目录，先检查 `.gitignore`，确保没有真实自拍、录音、密钥、私人文件。
4. 执行：

```bash
cd OnePerson-Media
python3 -m unittest discover -s tests -v
git init -b main
git add .
git commit -m "feat: release OnePerson Media v0.1"
git remote add origin https://github.com/modengsir/OnePerson-Media.git
git push -u origin main
```

如果使用 `gh` CLI 且已登录，也可以先创建空仓库：

```bash
gh repo create OnePerson-Media --public --description "一人自媒体 AI 工作流：开源 Skill，可选 Renoise"
```

注意：**这些命令不会由本项目自动执行**。如果 GitHub App 未获得写入授权，请在 GitHub Settings / Connected Apps 中检查当前连接授权范围后再试；不要在聊天中粘贴 Token。
