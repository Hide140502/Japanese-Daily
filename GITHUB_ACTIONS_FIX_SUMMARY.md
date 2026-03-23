# GitHub Actions 状态持久化问题修复指南

## 📋 问题描述

日语/英语每日推送系统在 GitHub Actions 中运行时，每天推送的内容都是相同的（一直推送第 N 天的内容），学习天数无法自动递增。

## 🔍 根本原因

GitHub Actions 默认的 `GITHUB_TOKEN` **没有写权限**（特别是 fork 仓库），导致 workflow 中的 `git push` 命令返回 403 错误：

```
remote: Write access to repository not granted.
fatal: unable to access 'https://github.com/...': The requested URL returned error: 403
```

虽然脚本成功更新了本地的 `current_day.txt`，但无法提交到远程仓库，导致下次运行时又读取相同的天数。

## 🔧 解决方案

### 方案：使用 Personal Access Token (PAT)

#### 第一步：创建 Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 配置：
   - Name: `[Project-Name]-Push`
   - Expiration: `No expiration` (建议)
   - Scopes: ✅ **repo** (勾选)
4. 点击 **Generate token**
5. **复制 token**（只显示一次，请妥善保管）

#### 第二步：添加到 Repository Secrets

1. 访问：`https://github.com/[USERNAME]/[REPO]/settings/secrets/actions`
2. 点击 **New repository secret**
3. Name: `PAT_TOKEN`
4. Secret: 粘贴刚才的 token
5. 点击 **Add secret**

#### 第三步：修改 Workflow 文件

修改 `.github/workflows/[your-workflow].yml`：

**修改 1：Checkout 步骤**
```yaml
# 修改前
- name: 检出代码
  uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}

# 修改后
- name: 检出代码
  uses: actions/checkout@v4
  with:
    token: ${{ secrets.PAT_TOKEN }}
```

**修改 2：添加权限声明**
```yaml
jobs:
  daily-push:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # 添加这行

    steps:
      # ... 其他步骤
```

**修改 3：提交状态更新步骤**
```yaml
# 修改前
- name: 提交状态更新
  run: |
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git config user.name "github-actions[bot]"
    git add current_day.txt
    git diff --staged --quiet || git commit -m "chore: 更新学习天数 [skip ci]" && git push

# 修改后
- name: 提交状态更新
  if: success()  # 只在前面步骤成功时执行
  run: |
    echo "📝 准备提交状态更新..."
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git config user.name "github-actions[bot]"
    git add current_day.txt
    if git diff --staged --quiet; then
      echo "⚠️ 状态文件没有变化，跳过提交"
    else
      echo "✅ 检测到状态文件变化，准备提交..."
      git commit -m "chore: 更新学习天数 [skip ci]"
      echo "🚀 正在推送到远程仓库..."
      git push https://${{ secrets.PAT_TOKEN }}@github.com/[USERNAME]/[REPO].git
      echo "✅ 状态更新已提交到远程仓库"
    fi
```

## 📝 关键修改点总结

| 修改项 | 说明 |
|--------|------|
| 1. 创建 PAT Token | 替代 GITHUB_TOKEN，获得写权限 |
| 2. 添加 Secrets | 将 PAT 添加到 `PAT_TOKEN` |
| 3. 修改 checkout | 使用 `PAT_TOKEN` 而非 `GITHUB_TOKEN` |
| 4. 添加 permissions | 明确声明 `contents: write` |
| 5. 使用 if: success() | 确保只在前置步骤成功后更新状态 |
| 6. 明确 git push URL | 在 push 时使用 PAT 认证 |

## ✅ 验证步骤

1. 推送修改后的 workflow 到 GitHub
2. 在 Actions 页面手动触发 workflow
3. 检查运行日志，确认：
   - ✅ `git push` 返回成功（无 403 错误）
   - ✅ 状态文件成功提交到仓库
   - ✅ 下次运行时天数正确递增

## 🎯 示例项目参考

- 本项目：`Siesta2025/Japanese-Daily`
- 修复提交：`dbe12b2` - "fix: 使用 PAT Token 解决推送权限问题"

---

**注意：** PAT 有完整的仓库访问权限，请妥善保管，不要在代码中硬编码或公开分享。
