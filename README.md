# Django WSGI（本地仓库 + HTTPS:8888 + 密码 + 自动部署）

## 架构

- 工作仓库：`/home/ubuntu/django-wsgi`
- 裸仓库（推送目标 / 自动部署入口）：`/home/ubuntu/repos/django-wsgi.git`
- 线上检出：`/home/ubuntu/deploy/django-wsgi`
- WSGI：Gunicorn → `127.0.0.1:8000`
- 对外：Nginx **仅 HTTPS** 监听 **8888**，并要求 **HTTP Basic Auth**

## 访问

```bash
curl -k -u admin:'<password>' https://127.0.0.1:8888/
```

密码文件（不入库）：`/home/ubuntu/runtime/django-wsgi/auth/password.txt`

## 自动部署

向裸仓库推送 `main` 会触发 `post-receive` → 检出到 deploy 目录 → `scripts/deploy.sh` 重启 Gunicorn：

```bash
cd /home/ubuntu/django-wsgi
# 改代码后
git add -A && git commit -m "..." && git push origin main
```

## 手动部署

```bash
bash /home/ubuntu/deploy/django-wsgi/scripts/deploy.sh
sudo nginx -t && sudo systemctl reload nginx
```
