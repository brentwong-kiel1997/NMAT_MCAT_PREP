# Gabay — NMAT（菲律宾医学院入学）与 MCAT 备考个人助手

## 本地结构

- 工作仓库：`/home/ubuntu/django-wsgi`
- 裸仓库（自动部署）：`/home/ubuntu/repos/django-wsgi.git`
- 线上检出：`/home/ubuntu/deploy/django-wsgi`
- 站点：`https://<host>:8888/`（HTTPS + Basic Auth）

## 当前内容

首页、科目大纲与高收益笔记、练习题、教材资料台（术语 / 公式 / 策略 / 清单）、疾病库、MiniMax-M3 学习教练。

## 配置（.env）

密钥从 `.env` 文件读取，不再依赖导出环境变量。复制模板后填值：

```bash
cp .env.example .env && chmod 600 .env
python manage.py env_status   # 查看命中的文件与遮罩后的值
```

查找顺序：`GABAY_ENV_FILE` → `<仓库>/.env` → `/home/ubuntu/runtime/.env` → `/home/ubuntu/runtime/secrets/minimax.env`。
`.env` 已被 gitignore；改动即时生效，无需重启 Gunicorn。

## 教材内容（content/）

知识内容的唯一源是 `content/` 目录里的 YAML 文件（科目大纲、章节笔记、练习题、术语 / 公式 / 策略 / 清单、疾病库、考试结构），由 `portal/content.py` 按文件 mtime 缓存直接读取——改完文件，下一个请求即生效，无需重建数据库。双语统一写 `{zh: …, en: …}`（中英相同就写标量）。

改教材的流程：

```bash
# 1. 改 content/**/*.yml（顺手可跑 python manage.py validate_content 自检）
git add content/ && git commit -m "..."
git push origin main     # 约 2 分钟自动部署；validate_content 会在部署时把关
```

目录速查：`content/subjects/`（科目+大纲）、`content/notes/`（章节笔记，规范桶，跨科共享由读取器复刻）、`content/practice/`（题目）、`content/materials/`（术语/公式/策略/路径/清单）、`content/diseases/`、`content/exams/`（NMAT/MCAT 结构）、`content/catalog.yml`（顺序与标签）。

稳定性约束：`subject_slug`、题目 `id`、章节顺序（决定 `chapter_id`）不能随意改动——学习进度用它们做关联键。`manage.py validate_content` 会在部署时校验这些并对照 MANIFEST.json。

## 推送与自动部署

自动部署跟随 GitHub：`scripts/poll_github.sh` 由 cron 每 2 分钟轮询一次，发现 `origin/main`（NMAT_MCAT_PREP）有新提交就自动部署上线。

```bash
cd /home/ubuntu/django-wsgi
git add -A && git commit -m "..."
git push origin main    # 推 GitHub，约 2 分钟内自动部署
```

- 等不及轮询时可手动触发：`scripts/poll_github.sh`
- 旧通道仍然可用：`git push deploy main` 立即触发裸仓 post-receive 部署
- 轮询日志：`/home/ubuntu/runtime/django-wsgi/logs/poll_github.log`
- 部署失败会在下一个轮询周期自动重试（状态只在部署成功后才前进）
