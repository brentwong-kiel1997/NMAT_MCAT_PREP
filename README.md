# Gabay — personal NMAT & MCAT study companion

A single-learner Django site for preparing for both the Philippine NMAT (CEM)
and the US MCAT (AAMC): curriculum outlines, high-yield notes, practice MCQs,
a materials desk (glossary / formulas / tips / paths / checklists), a disease
library for mechanism reading, and a MiniMax-M3 study coach grounded in the
current subject's outline. All content and UI are English.

## Layout

- Working repository: `/home/ubuntu/django-wsgi`
- Bare repo (deploy source): `/home/ubuntu/repos/django-wsgi.git`
- Live checkout: `/home/ubuntu/deploy/django-wsgi`
- Site: `https://<host>:8888/` (HTTPS + Basic Auth)
- Curriculum content lives in `content/` as YAML — see `content/README.md`
  (a standalone, deployment-agnostic description of the content pack)

## Configuration (.env)

Secrets are read from a `.env` file, never from exported environment
variables. Copy the template and fill it in:

```bash
cp .env.example .env && chmod 600 .env
python manage.py env_status   # shows which file supplies each key, masked
```

Lookup order: `GABAY_ENV_FILE` → `<repo>/.env` → `/home/ubuntu/runtime/.env` →
`/home/ubuntu/runtime/secrets/minimax.env`. `.env` is gitignored; changes take
effect on the next request without restarting Gunicorn.

## Databases

One SQLite file, `users.sqlite3` under `/home/ubuntu/runtime/django-wsgi/`:
Django auth/sessions plus learner progress (`LearnerProfile`,
`ChapterProgress`, `PracticeAttempt`). Curriculum knowledge is NOT in a
database — it is read from `content/*.yml` at runtime by `portal/content.py`
(mtime-cached, so edits apply on the next request).

## Curriculum content (content/)

Edit the YAML, validate, commit, push:

```bash
# edit content/**/*.yml
python manage.py validate_content     # optional local self-check
python manage.py refresh_manifest     # regenerate MANIFEST.json (commit it too)
git add content/ && git commit -m "..."
git push origin main
```

`validate_content` also runs as a deploy gate. Stability rules (subject slugs,
question ids, chapter order/titles drive learner-progress keys) are documented
in `content/README.md`.

## Pushing and auto-deploy

Auto-deploy prefers the local bare repo, then the remote:
`scripts/poll_github.sh` runs from cron every 2 minutes — if the local bare
repo holds commits the remote does not have (pushed via `git push deploy
main`), those win and are never rolled back; otherwise it follows
`origin/main` (GitHub).

```bash
cd /home/ubuntu/django-wsgi
git add -A && git commit -m "..."
git push deploy main    # local bare repo: immediate post-receive deploy (preferred channel)
git push origin main    # GitHub backup; polling deploys it within ~2 min
```

- The poller never rolls a local-only deployment back to an older remote tip;
  the remote takes over once it has caught up
- Impatient? Run `scripts/poll_github.sh` manually
- Poll log (each deploy tagged local/github):
  `/home/ubuntu/runtime/django-wsgi/logs/poll_github.log`
- Failed deploys retry on the next tick (state advances only on success)

## Handy commands

```bash
python manage.py validate_content    # content gate (also runs during deploy)
python manage.py refresh_manifest    # after editing content files
python manage.py crawl_pages --out DIR --login   # crawl all pages (normalized HTML)
python manage.py db_status           # user DB path + tables
python manage.py env_status          # .env lookup + masked values
```
