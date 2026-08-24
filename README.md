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

## 知识库快照（knowledge.sqlite3）

教材知识的源头是 Python 数据文件（`portal/notes.py`、`practice.py`、`materials_data.py`、`pack_enrich.py`、`exams.py`、`diseases.py`）。仓库根目录的 `knowledge.sqlite3` 是从这些源码重建出来的快照，随 git 提交、可直接配套使用。

改教材的固定流程——源码和快照必须成对提交，避免两份真相漂移：

```bash
# 1. 改 portal/*.py 里的内容
scripts/snapshot-knowledge.sh   # 2. 重建快照（含完整性校验）
git add -A && git commit -m "..."  # 3. 源码 + 快照一起提交
```

部署脚本仍会在服务器上用 `load_knowledge` 重建运行时知识库，所以即使某次忘了重建快照，线上也不会错；快照主要保证 clone 即用、GitHub 上的数据完整。

## 推送与自动部署

```bash
cd /home/ubuntu/django-wsgi
git add -A && git commit -m "..."
git push origin main    # GitHub 备份（NMAT_MCAT_PREP）
git push deploy main    # 触发裸仓 post-receive 自动部署
```
