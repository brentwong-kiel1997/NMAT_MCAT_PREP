# Gabay — NMAT（菲律宾医学院入学）与 MCAT 备考个人助手

## 本地结构

- 工作仓库：`/home/ubuntu/django-wsgi`
- 裸仓库（自动部署）：`/home/ubuntu/repos/django-wsgi.git`
- 线上检出：`/home/ubuntu/deploy/django-wsgi`
- 站点：`https://<host>:8888/`（HTTPS + Basic Auth）

## 当前内容

首页 + 疾病库（8 个高收益病种）。后续可继续追加疾病、题库、生理专题。

## 自动部署

```bash
cd /home/ubuntu/django-wsgi
git add -A && git commit -m "..." && git push origin main
```
