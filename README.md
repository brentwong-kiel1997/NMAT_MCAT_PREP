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

## 自动部署

```bash
cd /home/ubuntu/django-wsgi
git add -A && git commit -m "..." && git push origin main
```
