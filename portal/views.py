from django.http import HttpResponse
from django.utils import timezone


def home(request):
    now = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S %Z")
    body = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Django WSGI</title>
  <style>
    :root {{
      --bg: #0f1c17;
      --fg: #e8f2ec;
      --accent: #3d9b6a;
      --muted: #9bb5a8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: "IBM Plex Sans", "Noto Sans SC", sans-serif;
      color: var(--fg);
      background:
        radial-gradient(ellipse at 20% 10%, #1a3a2c 0%, transparent 50%),
        radial-gradient(ellipse at 80% 90%, #163028 0%, transparent 45%),
        linear-gradient(160deg, #0b1410, #122019 55%, #0f1c17);
    }}
    main {{
      width: min(40rem, 92vw);
      text-align: left;
    }}
    .brand {{
      font-size: clamp(2.4rem, 6vw, 3.6rem);
      font-weight: 700;
      letter-spacing: -0.03em;
      margin: 0 0 0.6rem;
      animation: rise 700ms ease-out both;
    }}
    h1 {{
      font-size: clamp(1.2rem, 2.6vw, 1.55rem);
      font-weight: 500;
      margin: 0 0 0.75rem;
      color: var(--muted);
      animation: rise 700ms ease-out 80ms both;
    }}
    p {{
      margin: 0;
      line-height: 1.55;
      color: #c5d8ce;
      animation: rise 700ms ease-out 160ms both;
    }}
    .meta {{
      margin-top: 1.5rem;
      font-size: 0.9rem;
      color: var(--accent);
      animation: rise 700ms ease-out 240ms both;
    }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
</head>
<body>
  <main>
    <p class="brand">Django WSGI</p>
    <h1>HTTPS + Basic Auth · 端口 8888</h1>
    <p>本页由 Gunicorn 通过 WSGI 提供，经 Nginx 强制 HTTPS 并要求访问密码。</p>
    <p class="meta">服务时间：{now}</p>
  </main>
</body>
</html>
"""
    return HttpResponse(body)
