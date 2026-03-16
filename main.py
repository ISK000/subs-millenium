# -*- coding: utf-8 -*-
"""
Cloud Run Proxy - v3.4.0 - iOS Fix + Telegram Button + Browser Landing
"""

import logging
import base64
import time
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from urllib.parse import unquote

MARZBAN_PANEL = "https://ulinux.fastlinky.xyz:8000"


BRAND_NAME = "MILLENIUM-GROUP"
TELEGRAM_CHANNEL = "https://t.me/milleniumgroupvpn"    # Кнопка "i" (info) → канал
TELEGRAM_SUPPORT = "https://t.me/i55ko"                # Кнопка Telegram (поддержка) → личка админа
DOMAIN = "api.millenium-group.blog"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Marzban VIP Proxy", version="3.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[
        "subscription-userinfo",
        "profile-title",
        "profile-update-interval",
        "profile-web-page-url",
        "support-url",
        "content-disposition",
    ],
)

# Переиспользуемый HTTP клиент
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=10.0, read=20.0, write=10.0, pool=10.0),
    verify=False,
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=30),
    http2=False,
    follow_redirects=True,
)

# ===================================================================
#  LANDING PAGE — когда открывают ссылку в браузере
# ===================================================================

LANDING_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>MILLENIUM GROUP VPN</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
  :root{
    --bg:#0a0a0f;
    --card:#12121a;
    --border:#1e1e2e;
    --gold:#f0c040;
    --gold-dim:#c9a030;
    --blue:#4e8cff;
    --text:#e8e8f0;
    --muted:#6e6e8a;
    --green:#34d399;
  }
  body{
    font-family:'Outfit',sans-serif;
    background:var(--bg);
    color:var(--text);
    min-height:100vh;
    overflow-x:hidden;
    -webkit-font-smoothing:antialiased;
  }

  /* animated grid bg */
  .bg-grid{
    position:fixed;inset:0;z-index:0;
    background-image:
      linear-gradient(rgba(240,192,64,.04) 1px,transparent 1px),
      linear-gradient(90deg,rgba(240,192,64,.04) 1px,transparent 1px);
    background-size:60px 60px;
    mask-image:radial-gradient(ellipse 70% 60% at 50% 30%,#000 20%,transparent 100%);
    -webkit-mask-image:radial-gradient(ellipse 70% 60% at 50% 30%,#000 20%,transparent 100%);
  }
  .glow-orb{
    position:fixed;border-radius:50%;filter:blur(100px);opacity:.22;z-index:0;
    animation:orbFloat 12s ease-in-out infinite alternate;
  }
  .glow-orb.a{width:500px;height:500px;background:var(--gold);top:-120px;left:-100px}
  .glow-orb.b{width:400px;height:400px;background:var(--blue);bottom:-80px;right:-60px;animation-delay:-6s}
  @keyframes orbFloat{0%{transform:translate(0,0) scale(1)}100%{transform:translate(30px,20px) scale(1.1)}}

  .wrapper{
    position:relative;z-index:1;
    max-width:520px;margin:0 auto;
    padding:50px 20px 40px;
    display:flex;flex-direction:column;align-items:center;
    min-height:100vh;
  }

  /* logo ring */
  .logo-ring{
    width:96px;height:96px;
    border-radius:50%;
    background:conic-gradient(from 0deg,var(--gold),var(--blue),var(--gold));
    padding:3px;
    animation:spin 8s linear infinite;
    margin-bottom:24px;
  }
  .logo-ring .inner{
    width:100%;height:100%;border-radius:50%;
    background:var(--bg);
    display:flex;align-items:center;justify-content:center;
    font-size:34px;font-weight:900;color:var(--gold);
    font-family:'JetBrains Mono',monospace;
    letter-spacing:-2px;
  }
  @keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}

  .brand{
    font-size:26px;font-weight:800;
    letter-spacing:2px;text-transform:uppercase;
    background:linear-gradient(135deg,var(--gold),#fff,var(--gold));
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;
    margin-bottom:6px;
  }
  .tagline{color:var(--muted);font-size:13px;letter-spacing:3px;text-transform:uppercase;margin-bottom:36px}

  /* cards */
  .card{
    width:100%;
    background:var(--card);
    border:1px solid var(--border);
    border-radius:16px;
    padding:22px;
    margin-bottom:16px;
    backdrop-filter:blur(20px);
  }
  .status-row{
    display:flex;align-items:center;justify-content:space-between;
    padding:11px 0;
    border-bottom:1px solid rgba(255,255,255,.04);
  }
  .status-row:last-child{border-bottom:none}
  .status-label{color:var(--muted);font-size:13px}
  .status-value{font-weight:600;font-size:13px;display:flex;align-items:center;gap:6px}
  .dot{width:8px;height:8px;border-radius:50%;display:inline-block}
  .dot.green{background:var(--green);box-shadow:0 0 8px var(--green)}
  .dot.gold{background:var(--gold);box-shadow:0 0 8px var(--gold)}

  .card h3{
    font-size:15px;font-weight:700;margin-bottom:14px;
    color:var(--gold);display:flex;align-items:center;gap:8px;
  }
  .step{display:flex;gap:12px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.03)}
  .step:last-child{border-bottom:none}
  .step-num{
    width:26px;height:26px;flex-shrink:0;border-radius:50%;
    background:rgba(240,192,64,.1);border:1px solid rgba(240,192,64,.25);
    display:flex;align-items:center;justify-content:center;
    font-size:11px;font-weight:700;color:var(--gold);
    font-family:'JetBrains Mono',monospace;
  }
  .step-text{font-size:13px;line-height:1.5;color:var(--text);padding-top:2px}
  .step-text b{color:var(--gold);font-weight:600}

  /* copy box */
  .copy-box{
    width:100%;
    background:rgba(240,192,64,.06);
    border:1px solid rgba(240,192,64,.15);
    border-radius:12px;
    padding:12px 14px;
    margin-bottom:16px;
    display:flex;align-items:center;justify-content:space-between;
    gap:10px;cursor:pointer;transition:all .2s;
  }
  .copy-box:hover{background:rgba(240,192,64,.1);border-color:rgba(240,192,64,.3)}
  .copy-box:active{transform:scale(.98)}
  .copy-url{
    font-family:'JetBrains Mono',monospace;
    font-size:11px;color:var(--gold);
    word-break:break-all;flex:1;user-select:all;
  }
  .copy-btn{
    background:var(--gold);color:var(--bg);
    border:none;border-radius:8px;
    padding:8px 14px;font-size:11px;font-weight:700;
    font-family:'Outfit',sans-serif;cursor:pointer;
    white-space:nowrap;transition:all .15s;
  }
  .copy-btn:hover{transform:scale(1.05);box-shadow:0 0 20px rgba(240,192,64,.3)}

  /* buttons */
  .btn-group{width:100%;display:flex;flex-direction:column;gap:10px;margin-bottom:20px}
  .btn{
    display:flex;align-items:center;justify-content:center;gap:10px;
    width:100%;padding:15px;border-radius:12px;
    font-size:14px;font-weight:600;
    font-family:'Outfit',sans-serif;
    text-decoration:none;transition:all .2s;cursor:pointer;border:none;
  }
  .btn:active{transform:scale(.97)}
  .btn-tg{background:linear-gradient(135deg,#2AABEE,#229ED9);color:#fff}
  .btn-tg:hover{box-shadow:0 4px 24px rgba(42,171,238,.3);transform:translateY(-1px)}
  .btn-ios{background:linear-gradient(135deg,var(--gold),var(--gold-dim));color:var(--bg)}
  .btn-ios:hover{box-shadow:0 4px 24px rgba(240,192,64,.3);transform:translateY(-1px)}
  .btn-android{background:linear-gradient(135deg,#34d399,#059669);color:#fff}
  .btn-android:hover{box-shadow:0 4px 24px rgba(52,211,153,.3);transform:translateY(-1px)}

  /* app list */
  .apps{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:28px}
  .app-tag{
    display:inline-flex;align-items:center;gap:5px;
    background:rgba(255,255,255,.05);border:1px solid var(--border);
    border-radius:8px;padding:7px 12px;font-size:11px;color:var(--muted);font-weight:500;
  }

  .footer{
    margin-top:auto;padding-top:24px;text-align:center;
    color:var(--muted);font-size:10px;letter-spacing:1px;text-transform:uppercase;
  }

  /* fade in */
  .fi{opacity:0;transform:translateY(16px);animation:fu .5s ease forwards}
  .fi:nth-child(2){animation-delay:.08s}
  .fi:nth-child(3){animation-delay:.14s}
  .fi:nth-child(4){animation-delay:.2s}
  .fi:nth-child(5){animation-delay:.26s}
  .fi:nth-child(6){animation-delay:.32s}
  .fi:nth-child(7){animation-delay:.36s}
  .fi:nth-child(8){animation-delay:.4s}
  .fi:nth-child(9){animation-delay:.44s}
  .fi:nth-child(10){animation-delay:.48s}
  @keyframes fu{to{opacity:1;transform:translateY(0)}}

  .toast{
    position:fixed;bottom:30px;left:50%;transform:translateX(-50%) translateY(80px);
    background:var(--gold);color:var(--bg);
    padding:12px 28px;border-radius:30px;font-weight:700;font-size:14px;
    box-shadow:0 8px 32px rgba(240,192,64,.4);
    transition:transform .3s cubic-bezier(.175,.885,.32,1.275);
    z-index:100;pointer-events:none;
  }
  .toast.show{transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>

<div class="bg-grid"></div>
<div class="glow-orb a"></div>
<div class="glow-orb b"></div>

<div class="wrapper">

  <div class="logo-ring fi"><div class="inner">M</div></div>
  <div class="brand fi">MILLENIUM GROUP</div>
  <div class="tagline fi">Premium VPN Service</div>

  <!-- Status -->
  <div class="card fi">
    <div class="status-row">
      <span class="status-label">Статус</span>
      <span class="status-value"><span class="dot green"></span> Онлайн</span>
    </div>
    <div class="status-row">
      <span class="status-label">Протоколы</span>
      <span class="status-value">VLESS · VMess · Shadowsocks</span>
    </div>
    <div class="status-row">
      <span class="status-label">Серверы</span>
      <span class="status-value"><span class="dot gold"></span> 10+ локаций</span>
    </div>
  </div>

  <!-- Instructions -->
  <div class="card fi">
    <h3>📲 Как подключиться</h3>
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-text">Скачайте <b>Happ</b> (iOS) или <b>v2rayNG</b> (Android)</div>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <div class="step-text">Скопируйте ссылку подписки ниже</div>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <div class="step-text">В приложении: <b>+</b> → <b>Импорт из буфера</b></div>
    </div>
    <div class="step">
      <div class="step-num">4</div>
      <div class="step-text">Нажмите <b>▶ Подключиться</b></div>
    </div>
  </div>

  <!-- Copy URL -->
  <div class="copy-box fi" onclick="copyLink()">
    <div class="copy-url" id="subUrl">{{SUB_URL}}</div>
    <button class="copy-btn" id="copyBtn">КОПИРОВАТЬ</button>
  </div>

  <!-- Buttons -->
  <div class="btn-group fi">
    <a href="https://t.me/milleniumgroupvpn" target="_blank" class="btn btn-tg">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
      Наш Telegram
    </a>
    <a href="https://apps.apple.com/app/happ-proxy-utility/id6504287215" target="_blank" class="btn btn-ios">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>
      Happ для iOS
    </a>
    <a href="https://play.google.com/store/apps/details?id=com.happ.proxy" target="_blank" class="btn btn-android">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3.609 1.814L13.792 12 3.61 22.186a.996.996 0 0 1-.61-.92V2.734a1 1 0 0 1 .609-.92zm10.89 10.893l2.302 2.302-10.937 6.333 8.635-8.635zm3.199-3.199l2.302 1.33-2.302 1.33-1.838-1.33 1.838-1.33zM5.864 2.658L16.8 8.991l-2.302 2.302-8.634-8.635z"/></svg>
      Happ для Android
    </a>
  </div>

  <!-- App badges -->
  <div class="apps fi">
    <div class="app-tag">Happ</div>
    <div class="app-tag">Streisand</div>
    <div class="app-tag">v2rayNG</div>
    <div class="app-tag">Napsternetv</div>
    <div class="app-tag">V2Box</div>
  </div>

  <div class="footer fi">© 2025 MILLENIUM GROUP · Premium VPN Service</div>

</div>

<div class="toast" id="toast">✓ Ссылка скопирована!</div>

<script>
function copyLink(){
  var url=document.getElementById('subUrl').textContent;
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(url).then(ok,fallback);
  }else{fallback()}
  function ok(){show()}
  function fallback(){
    var t=document.createElement('textarea');
    t.value=url;t.style.position='fixed';t.style.opacity='0';
    document.body.appendChild(t);t.select();
    try{document.execCommand('copy');show()}catch(e){}
    document.body.removeChild(t);
  }
  function show(){
    var toast=document.getElementById('toast');
    toast.classList.add('show');
    document.getElementById('copyBtn').textContent='ГОТОВО ✓';
    setTimeout(function(){toast.classList.remove('show')},2000);
    setTimeout(function(){document.getElementById('copyBtn').textContent='КОПИРОВАТЬ'},3000);
  }
}
</script>
</body>
</html>"""

# ===================================================================
#  УТИЛИТЫ
# ===================================================================

def decode_token(token: str) -> str:
    try:
        decoded = base64.urlsafe_b64decode(token + "==").decode("utf-8")
        return unquote(decoded)
    except Exception:
        return token

def extract_username_from_token(token: str) -> str:
    try:
        decoded = decode_token(token)
        if "," in decoded:
            return decoded.split(",")[0]
        return decoded[:20]
    except Exception:
        return "subscription"

def is_browser(user_agent: str) -> bool:
    """Определяет — это браузер или VPN-приложение?"""
    ua = user_agent.lower()
    # VPN клиенты
    vpn_clients = [
        "happ", "streisand", "v2ray", "xray", "clash",
        "shadowrocket", "quantumult", "surge", "napster",
        "sing-box", "nekoray", "nekobox", "v2box", "lancex",
        "stash", "loon", "pharos", "oneclick", "matsuri",
        "sagernet", "flyclash", "surfboard", "karing",
    ]
    for client in vpn_clients:
        if client in ua:
            return False
    # Браузеры
    browser_markers = ["mozilla", "chrome", "safari", "firefox", "edge", "opera", "webkit"]
    for marker in browser_markers:
        if marker in ua:
            return True
    return False

def is_vip_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith("#"):
        return False
    if "://" not in s:
        return False
    if "#" not in s:
        return False
    name_part = s.split("#", 1)[1]
    try:
        name_decoded = unquote(name_part)
    except Exception:
        name_decoded = name_part
    return "vip" in name_decoded.lower()

def filter_vip_hosts(content: bytes, is_vip: bool) -> bytes:
    if not content or len(content) == 0:
        return content
    try:
        decoded_bytes = base64.b64decode(content)
        text = decoded_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"❌ base64 error: {e}")
        return content

    lines = text.splitlines()
    vpn_lines = [l for l in lines if l.strip() and "://" in l]
    total_vpn = len(vpn_lines)

    filtered_lines = []
    removed = 0
    for line in lines:
        line_is_vip = is_vip_line(line)
        if is_vip:
            if line_is_vip or not (line.strip() and "://" in line):
                filtered_lines.append(line)
            else:
                removed += 1
        else:
            if line_is_vip:
                removed += 1
            else:
                filtered_lines.append(line)

    kept = len([l for l in filtered_lines if l.strip() and "://" in l])
    logger.info(f"✅ {'VIP' if is_vip else 'Reg'}: {kept}/{total_vpn} (удалено {removed})")

    if total_vpn > 0 and kept == 0:
        return content

    return base64.b64encode("\n".join(filtered_lines).encode("utf-8"))

# ===================================================================
#  LANDING PAGE RENDER
# ===================================================================

def render_landing(sub_url: str) -> str:
    return LANDING_PAGE_HTML.replace("{{SUB_URL}}", sub_url)

# ===================================================================
#  ROUTES
# ===================================================================

@app.get("/")
async def root(request: Request):
    return HTMLResponse(render_landing(f"https://{DOMAIN}/regular/ВАШ_ТОКЕН"))

@app.get("/regular/{token}")
@app.get("/url/{token}")
async def get_regular_subscription(token: str, request: Request):
    return await handle_subscription(token, is_vip=False, request=request)

@app.get("/vip/{token}")
async def get_vip_subscription(token: str, request: Request):
    return await handle_subscription(token, is_vip=True, request=request)

async def handle_subscription(token: str, is_vip: bool, request: Request):
    start_time = time.time()
    user_type = "⭐VIP" if is_vip else "👤Reg"
    user_agent = request.headers.get("user-agent", "")
    endpoint = "vip" if is_vip else "regular"
    sub_url = f"https://{DOMAIN}/{endpoint}/{token}"

    logger.info(f"📥 {user_type} | token={token[:20]}... | UA: {user_agent[:60]}")

    # ===== БРАУЗЕР → КРАСИВЫЙ ЛЕНДИНГ =====
    if is_browser(user_agent):
        logger.info(f"🌐 Браузер → лендинг")
        return HTMLResponse(render_landing(sub_url))

    # ===== VPN КЛИЕНТ → ПОДПИСКА =====
    decoded_token = decode_token(token)
    username = extract_username_from_token(token)
    subscription_url = f"{MARZBAN_PANEL}/sub/{decoded_token}"

    try:
        fwd = {}
        if user_agent:
            fwd["User-Agent"] = user_agent
        accept = request.headers.get("accept", "")
        if accept:
            fwd["Accept"] = accept

        r = await http_client.get(subscription_url, headers=fwd)
        elapsed = time.time() - start_time
        logger.info(f"⏱️ Marzban: {r.status_code} за {elapsed:.2f}с")

        if r.status_code != 200:
            return Response(content=f"Error: {r.status_code}", status_code=r.status_code, media_type="text/plain; charset=utf-8")
        if len(r.content) == 0:
            return Response(content="Error: Empty", status_code=500, media_type="text/plain; charset=utf-8")

        filtered_content = filter_vip_hosts(r.content, is_vip=is_vip)

        # ===== ЗАГОЛОВКИ =====
        h = {}

        # Пробрасываем от Marzban (включая support-url и profile-web-page-url)
        for key in ["subscription-userinfo", "profile-title", "profile-update-interval", "support-url", "profile-web-page-url"]:
            if key in r.headers:
                h[key] = r.headers[key]

        # content-disposition — ОБЯЗАТЕЛЬНО для iOS
        h["content-disposition"] = f'attachment; filename="{username}"'

        # profile-web-page-url — кнопка "i" (info) → канал
        if "profile-web-page-url" not in h:
            h["profile-web-page-url"] = TELEGRAM_CHANNEL

        # support-url — кнопка Telegram (поддержка) → личка админа
        if "support-url" not in h:
            h["support-url"] = TELEGRAM_SUPPORT

        # profile-title (если Marzban не отдал)
        if "profile-title" not in h:
            h["profile-title"] = f"base64:{base64.b64encode(BRAND_NAME.encode()).decode()}"

        # profile-update-interval (авто-обновление каждый час)
        if "profile-update-interval" not in h:
            h["profile-update-interval"] = "1"

        # Анти-кэш iOS
        h["Cache-Control"] = "no-cache, no-store, must-revalidate"
        h["Pragma"] = "no-cache"
        h["Expires"] = "0"

        # Content-Length для iOS
        h["Content-Length"] = str(len(filtered_content))
        h["Connection"] = "keep-alive"

        logger.info(f"📤 {user_type}: {len(filtered_content)}B | {time.time()-start_time:.2f}с")

        return Response(
            content=filtered_content,
            status_code=200,
            media_type="text/plain; charset=utf-8",
            headers=h,
        )

    except httpx.TimeoutException:
        logger.error(f"❌ TIMEOUT")
        return Response(content="Error: timeout", status_code=504, media_type="text/plain; charset=utf-8")
    except Exception as e:
        logger.error(f"❌ {e}")
        return Response(content=f"Error: {e}", status_code=500, media_type="text/plain; charset=utf-8")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.4.0", "brand": BRAND_NAME}

# HEAD для iOS
@app.head("/regular/{token}")
@app.head("/url/{token}")
@app.head("/vip/{token}")
async def head_subscription(token: str):
    return Response(status_code=200, headers={"Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-cache"})

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
