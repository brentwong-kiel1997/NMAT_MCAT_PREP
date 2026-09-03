# Deploying Gabay — step by step

This guide takes a **fresh Ubuntu 22.04/24.04 server** to a running,
password-protected HTTPS deployment of Gabay. It mirrors exactly how the
production instance is built. Everything here is plain commands — no
proprietary tooling.

> For local poking-around instead, see the **Quickstart** in [README.md](README.md).
> Machine-specific notes (IPs, chosen passwords) belong in a gitignored
> `DEPLOYMENT.local.md`, never in this file.

---

## 0. What you will build

```
 developer laptop                       server
 ┌──────────────────┐    git push      ┌────────────────────────────────────────────┐
 │ working checkout │ ─── "deploy" ──► │ /home/ubuntu/repos/django-wsgi.git (bare)  │
 │  (GitHub origin) │                  │        │ post-receive hook                 │
 └──────────────────┘                  │        ▼ checkout -f (staging)             │
                                       │ /home/ubuntu/runtime/staging               │
                                       │        │ scripts/deploy.sh                 │
                                       │        │  pip → migrate → validate gate    │
                                       │        │  → collectstatic                  │
                                       │        ▼ atomic swap (two renames)         │
                                       │ /home/ubuntu/deploy/django-wsgi  (live)    │
                                       │        │ + restart gunicorn                │
                                       │ gunicorn 127.0.0.1:8000  (systemd)         │
                                       │        ▲ proxy                             │
   browser ── HTTPS :8888 ──────────► │ nginx: TLS + Basic-Auth front door         │
                                       │                                            │
   secrets & data (NEVER in git):      │ /home/ubuntu/runtime/                      │
                                       │   .env            ← DJANGO_SECRET_KEY etc. │
                                       │   django-wsgi/users.sqlite3                │
                                       │   django-wsgi/{venv,logs,certs,auth}       │
                                       └────────────────────────────────────────────┘
```

Three directories with strict roles — keep them separate:

| Path | Role | In git? |
| --- | --- | --- |
| `/home/ubuntu/deploy/django-wsgi` | checked-out code, replaced on every push | is the repo |
| `/home/ubuntu/repos/django-wsgi.git` | bare repo receiving pushes | — |
| `/home/ubuntu/runtime/` | venv, DB, logs, certs, secrets | **never** |

---

## 1. Prerequisites

- Ubuntu 22.04+ server, one sudo user (`ubuntu` below)
- Domain or IP; port **8888** reachable (or change it, consistently, below)
- The GitHub repo: `git@github.com:brentwong-kiel1997/NMAT_MCAT_PREP.git`
  (or your fork)

## 2. System packages

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv git nginx apache2-utils \
                    sqlite3 curl
```

(`apache2-utils` provides `htpasswd`; `sqlite3` is for backups/inspection.)

## 3. Directory layout

```bash
sudo mkdir -p /home/ubuntu/{repos,deploy,runtime/django-wsgi/{logs,certs,auth}}
sudo chown -R ubuntu:ubuntu /home/ubuntu/{repos,deploy,runtime}
```

## 4. Get the code into a bare repo + install the deploy hook

```bash
git clone --bare git@github.com:brentwong-kiel1997/NMAT_MCAT_PREP.git \
    /home/ubuntu/repos/django-wsgi.git

# the hook turns every push into a deploy (staging + atomic swap)
git --git-dir=/home/ubuntu/repos/django-wsgi.git show main:scripts/post-receive \
  > /home/ubuntu/repos/django-wsgi.git/hooks/post-receive
chmod +x /home/ubuntu/repos/django-wsgi.git/hooks/post-receive
```

On a fresh server the live checkout is still empty — seed it once
(this first time it is required so step 5 has a `requirements.txt` to
read; later pushes rebuild staging and swap, never touching the live
directory directly):

```bash
GIT_WORK_TREE=/home/ubuntu/deploy/django-wsgi \
GIT_DIR=/home/ubuntu/repos/django-wsgi.git git checkout -f main
```

On your **development machine**, add the server as a remote:

```bash
git remote add deploy ubuntu@YOUR_SERVER:/home/ubuntu/repos/django-wsgi.git
```

## 5. Python environment

```bash
python3.12 -m venv /home/ubuntu/runtime/django-wsgi/venv
/home/ubuntu/runtime/django-wsgi/venv/bin/pip install --upgrade pip
/home/ubuntu/runtime/django-wsgi/venv/bin/pip install \
    -r /home/ubuntu/deploy/django-wsgi/requirements.txt
```

> Every deploy re-runs `pip install -r requirements.lock` (the committed
> freeze — exact production parity), so dependency changes apply themselves.

## 6. Secrets — outside git, always

The app **refuses to start** without `DJANGO_SECRET_KEY`, and AI-coach keys
are read from `.env` files. Create the runtime env file:

```bash
umask 077
cat >> /home/ubuntu/runtime/.env <<EOF
DJANGO_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')
EOF
chmod 600 /home/ubuntu/runtime/.env
```

Optional AI coach (MiniMax shown; any OpenAI-compatible endpoint works):

```bash
cat >> /home/ubuntu/runtime/.env <<'EOF'
MINIMAX_API_KEY=***
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M3
EOF
```

`.env` lookup order (first file defining a key wins):
`$GABAY_ENV_FILE` → `<repo>/.env` → `/home/ubuntu/runtime/.env` →
`/home/ubuntu/runtime/secrets/minimax.env`. For `DJANGO_SECRET_KEY` the
process environment is consulted first.

**Rules**

- Never commit `.env` (it is gitignored; keep it that way).
- AI-provider keys entered through the web UI are Fernet-encrypted in the DB;
  the `.env` route above is only the bootstrap.

## 7. systemd unit for gunicorn

`/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gabay Django WSGI (gunicorn)
After=network.target

[Service]
Type=exec
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/deploy/django-wsgi
Environment=DJANGO_DEBUG=0
Environment=DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*
ExecReload=/bin/kill -HUP $MAINPID
ExecStart=/home/ubuntu/runtime/django-wsgi/venv/bin/gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 2 \
  --access-logfile /home/ubuntu/runtime/django-wsgi/logs/gunicorn.access.log \
  --error-logfile /home/ubuntu/runtime/django-wsgi/logs/gunicorn.error.log
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn    # started by the first deploy
```

Notes:

- No secrets live in this unit — the secret key and AI keys come from
  `.env` files at runtime (`portal/envfile.py`).
- `DJANGO_ALLOWED_HOSTS=*` is convenient; tighten to your real hostname
  once things work.
- gunicorn binds **127.0.0.1 only** — it must never be reachable directly.

## 8. TLS certificate

For a private/LAN deployment a self-signed cert is fine (browsers will warn
once). For a public domain use certbot/Let's Encrypt instead and skip this.

```bash
openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
  -keyout /home/ubuntu/runtime/django-wsgi/certs/server.key \
  -out    /home/ubuntu/runtime/django-wsgi/certs/server.crt \
  -subj "/CN=YOUR_SERVER_NAME"
chmod 600 /home/ubuntu/runtime/django-wsgi/certs/server.key
```

## 9. nginx: TLS + Basic-Auth front door

`/etc/nginx/sites-available/django-wsgi`:

```nginx
server {
    listen 8888 ssl;
    listen [::]:8888 ssl;
    server_name _;

    ssl_certificate     /home/ubuntu/runtime/django-wsgi/certs/server.crt;
    ssl_certificate_key /home/ubuntu/runtime/django-wsgi/certs/server.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    # password on every route — the app's own login is the second layer
    auth_basic           "Django WSGI — password required";
    auth_basic_user_file /home/ubuntu/runtime/django-wsgi/auth/.htpasswd;

    client_max_body_size 20m;

    location /static/ {
        alias /home/ubuntu/deploy/django-wsgi/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port  8888;
        proxy_redirect off;
    }
}
```

Create the shared front-door password, then enable the site:

```bash
sudo htpasswd -c /home/ubuntu/runtime/django-wsgi/auth/.htpasswd gabay
sudo chown ubuntu:www-data /home/ubuntu/runtime/django-wsgi/auth/.htpasswd
sudo chmod 640 /home/ubuntu/runtime/django-wsgi/auth/.htpasswd

sudo ln -sf /etc/nginx/sites-available/django-wsgi /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

Store the password you chose somewhere safe (e.g.
`runtime/django-wsgi/auth/password.txt`, mode 600). Add more people with
`sudo htpasswd <file> <name>`; remove with `-D`.

> `X-Forwarded-Proto https` matters: Django only sets Secure session
> cookies because it trusts this header (`SECURE_PROXY_SSL_HEADER`).

## 10. First deploy

From your development machine:

```bash
git push deploy main
```

Watch the hook output. A healthy deploy prints, in order:

1. `pip` install (quiet, from the committed `requirements.lock`)
2. `check` + `migrate` (run against the live DB from the staging checkout)
3. **`validate_content` — the gate**: content hashes vs `MANIFEST.json` +
   structural checks, still in staging. If it fails, the script exits here
   and the live directory was never touched — the old site keeps serving,
   completely unchanged.
4. `collectstatic` (into staging)
5. **atomic swap**: staging renames onto the live path (the previous
   revision is kept at `/home/ubuntu/deploy/.django-wsgi.prev`)
6. `ensure_admin` / `ensure_ai_model` (idempotent seeds)
7. `systemctl restart gunicorn`
8. `Deployed <rev> → gunicorn 127.0.0.1:8000`

Afterwards confirm the unit: `systemctl is-active gunicorn` → `active`.

**Rollback**: `mv /home/ubuntu/deploy/.django-wsgi.prev /home/ubuntu/deploy/django-wsgi && sudo systemctl restart gunicorn`.

## 11. Admin account & AI coach

```bash
cd /home/ubuntu/deploy/django-wsgi
/home/ubuntu/runtime/django-wsgi/venv/bin/python manage.py \
    ensure_admin --username admin --password 'pick-a-strong-one'
```

Then, signed in as staff: **Manage → Models** to add/switch the AI coach
model (keys are encrypted at rest; the UI masks them). Without a model the
rest of the site works — only the coach is offline.

## 12. Verification checklist

Against `https://SERVER:8888` (expect the browser basic-auth prompt first):

| Probe | Expected |
| --- | --- |
| `/` | 200, home page |
| `/register/` | 200; create an account and get logged in |
| `/api/progress/?subject_slug=bio` while signed out | `401 {"error": "login required"}` |
| `/content-images/items/…any committed .svg` | 200 image |
| `/exams/` after login | exam list; a full mock can be started and submitted |

Direct-to-app probes (on the server, bypassing nginx):

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/          # 200
curl -s http://127.0.0.1:8000/api/progress/?subject_slug=bio             # 401 JSON
```

---

## 13. Day-2 operations

**Deploy a change** — edit, validate locally, push:

```bash
.venv/bin/python manage.py validate_content
.venv/bin/python manage.py refresh_manifest   # if content/*.yml changed
git add -A && git commit -m "…"
git push origin main     # GitHub
git push deploy main     # server (auto-migrates, gates, restarts)
```

**Logs**: `runtime/django-wsgi/logs/gunicorn.{access,error}.log`,
`journalctl -u gunicorn`, `/var/log/nginx/error.log`.

**Restart without a deploy**: `sudo systemctl restart gunicorn`.

**Back up the user DB** (accounts, sessions, all progress):

```bash
sqlite3 /home/ubuntu/runtime/django-wsgi/users.sqlite3 \
  ".backup /home/ubuntu/runtime/django-wsgi/users.sqlite3.$(date +%F)"
```

`.backup` is safe on a live database; plain `cp` is not. Restore = stop
gunicorn, copy the backup over `users.sqlite3`, `manage.py migrate`
(idempotent), start.

**Rotate the nginx front-door password**:
`sudo htpasswd /home/ubuntu/runtime/django-wsgi/auth/.htpasswd gabay` then
share the new password out-of-band.

**Rotate `DJANGO_SECRET_KEY`** (e.g. after someone with access leaves):
edit `/home/ubuntu/runtime/.env`, restart gunicorn. Two consequences to
know:

1. every existing login session is invalidated (everyone signs in again);
2. AI-provider keys in the DB were encrypted with the old key and become
   unreadable — re-enter them via **Manage → Models**.

## 14. Troubleshooting

| Symptom | Likely cause → fix |
| --- | --- |
| Deploy stops at `validate_content` | content edited without `refresh_manifest`, or genuinely broken YAML — fix, commit, push again; old site kept serving meanwhile |
| 502 from nginx | gunicorn down: `journalctl -u gunicorn -n 50`; often a failed migration or missing env |
| App refuses to start: `DJANGO_SECRET_KEY is not set` | section 6 not done, or `.env` not readable by `ubuntu` |
| Login loop (redirected back to `/login/`) | reaching Django over plain HTTP in a mode that expects TLS — use nginx, or set `DJANGO_DEBUG=1` for local dev |
| Browser stuck on basic-auth prompt | wrong front-door password; reset per section 9 |
| Coach answers "model unconfigured" | no provider active — Manage → Models |
| Stale CSS/JS after a frontend change | cache-buster query string in `base.html` — bump the `?v=…` value |
| `sudo: a password is required` during push | the pushing user needs passwordless `systemctl restart gunicorn` via sudoers, or run deploys from an account that has it |

## 15. Security checklist

- [ ] `DJANGO_SECRET_KEY` lives only in `/home/ubuntu/runtime/.env` (mode 600), never committed
- [ ] gunicorn bound to 127.0.0.1 only; nginx is the sole public entry
- [ ] TLS enabled; Basic-Auth front door enabled
- [ ] `.env`, `auth/.htpasswd`, `certs/`, `users.sqlite3*` are **not** in git
- [ ] `manage.py test` and `validate_content` green on the latest commit (CI enforces on GitHub)
- [ ] Regular DB backups scheduled; at least one tested restore
- [ ] Everyone who should have access has a site account (`/register/`); staff accounts are admin-created
