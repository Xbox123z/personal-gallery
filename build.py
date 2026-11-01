#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the personal gallery static site from collected data files."""
import json, html, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/home/hatch/workspace/goals/gallery-github-b/hidden_files"
CST = datetime.timezone(datetime.timedelta(hours=8))
NOW = datetime.datetime.now(CST)
GEN_TIME = NOW.strftime("%Y-%m-%d %H:%M")

gh = json.load(open(f"{DATA}/github.json"))
bili = json.load(open(f"{DATA}/bili-final.json"))
blog1 = json.load(open(f"{DATA}/blogger-xbox123z-github.json"))
blog2 = json.load(open(f"{DATA}/blogger-1644z114514lzp.json"))

prof = gh["profile"]
repos = gh["repos"]
pub_repos = [r for r in repos if not r["private"]]
priv_repos = [r for r in repos if r["private"]]

LANG_COLORS = {"Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
               "Kotlin": "#A97BFF", "Rust": "#dea584", "Go": "#00ADD8", "Java": "#b07219",
               "Dart": "#00B4AB", "C#": "#178600", "HTML": "#e34c26", "Shell": "#89e051",
               "PowerShell": "#012456", "CSS": "#663399"}

def esc(s): return html.escape(s or "", quote=True)

def fmt_date(iso):
    if not iso: return ""
    try:
        d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(CST)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return iso[:10]

# ---------- repo cards ----------
langs = sorted({r["language"] for r in pub_repos if r["language"]})
chips = ['<button class="chip active" data-lang="all">全部</button>'] + \
        [f'<button class="chip" data-lang="{esc(l)}">{esc(l)}</button>' for l in langs]

cards = []
for r in pub_repos:
    lang = r["language"] or "其他"
    color = LANG_COLORS.get(r["language"] or "", "#8b949e")
    desc = r["description"] or "暂无简介，点进去看看源码和 README。"
    badges = ""
    if r["fork"]: badges += '<span class="badge">fork</span>'
    if r["stars"]: badges += f'<span class="badge star">★ {r["stars"]}</span>'
    cards.append(f'''<a class="card repo" href="{esc(r['html_url'])}" target="_blank" rel="noopener"
   data-name="{esc(r['name'].lower())}" data-lang="{esc(lang)}" data-desc="{esc((r['description'] or '').lower())}">
  <div class="card-top"><span class="repo-name">{esc(r['name'])}</span>{badges}</div>
  <p class="card-desc">{esc(desc)}</p>
  <div class="card-meta"><span class="dot" style="background:{color}"></span>{esc(lang)}
    <span class="sep">·</span>更新 {fmt_date(r['pushed_at'])}</div>
</a>''')
repos_html = "\n".join(cards)

priv_html = ""
if priv_repos:
    items = []
    for r in priv_repos:
        items.append(f'''<div class="card repo priv">
  <div class="card-top"><span class="repo-name">{esc(r['name'])}</span><span class="badge lock">🔒 私有</span></div>
  <p class="card-desc">{esc(r['description'] or '')}</p>
  <div class="card-meta">仅账号本人可见</div>
</div>''')
    priv_html = f'''<h3 class="sub-h">私有仓库（{len(priv_repos)}）</h3>
<div class="grid">{''.join(items)}</div>'''

# ---------- bilibili ----------
bp = bili["profile"]
vids = []
for v in bili["videos"]:
    vids.append(f'''<article class="card video">
  <button class="thumb" data-bvid="{esc(v['bvid'])}" data-title="{esc(v['title'])}" aria-label="内嵌播放">
    <img src="{esc(v['pic'])}" alt="{esc(v['title'])}" loading="lazy" referrerpolicy="no-referrer">
    <span class="play-btn">▶</span><span class="dur">{esc(v['length'])}</span>
  </button>
  <div class="v-body">
    <h4>{esc(v['title'])}</h4>
    <div class="card-meta">播放 {v['play']} · {esc(v.get('pubdate') or v['date_shown'])}</div>
    <div class="v-actions">
      <button class="mini primary" data-bvid="{esc(v['bvid'])}" data-title="{esc(v['title'])}">▶ 内嵌播放</button>
      <a class="mini" href="{esc(v['url'])}" target="_blank" rel="noopener">B站打开 ↗</a>
    </div>
  </div>
</article>''')
videos_html = "\n".join(vids)

opus_html = "\n".join(
    f'''<a class="opus-row" href="{esc(o['url'])}" target="_blank" rel="noopener">
  <span class="opus-title">{esc(o['title'])}</span><span class="opus-date">{esc(o['date'])}</span></a>'''
    for o in bili["opus"])

# m3u8 playlist
lines = ["#EXTM3U",
         f"#PLAYLIST:千早爱圣音 · Bilibili 视频索引（生成于 {GEN_TIME} CST）",
         "# x-tvg-url=\"\""]
for v in bili["videos"]:
    if v.get("stream_mp4"):
        dur = "12"
        mm, ss = v["length"].split(":"); dur = str(int(mm) * 60 + int(ss))
        lines.append(f'#EXTINF:{dur},千早爱圣音 - {v["title"]} [{v["bvid"]}]')
        lines.append("#EXTVLCOPT:http-referrer=https://www.bilibili.com/")
        lines.append(v["stream_mp4"])
m3u8_text = "\n".join(lines) + "\n"
open(os.path.join(HERE, "index.m3u8"), "w", encoding="utf-8").write(m3u8_text)

# ---------- blogs ----------
def blog_posts_html(blog):
    rows = []
    for p in blog["posts"]:
        rows.append(f'''<a class="post-row" href="{esc(p['url'])}" target="_blank" rel="noopener">
  <span class="post-title">{esc(p['title'])}</span>
  <span class="post-meta">{fmt_date(p['published'])} · {esc(blog['blog'])}</span></a>''')
    return "\n".join(rows)
blog_posts_html_all = blog_posts_html(blog1)

CSS = """
:root{--bg:#0a0d13;--panel:#11151d;--panel2:#161b26;--line:#232a38;--txt:#e8ecf3;--sub:#9aa5b5;
--pink:#fb7299;--cyan:#22d3ee;--violet:#8b7cf6;--radius:16px}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:radial-gradient(900px 480px at 85% -5%,rgba(251,114,153,.14),transparent 60%),
radial-gradient(800px 420px at -10% 20%,rgba(34,211,238,.10),transparent 60%),
radial-gradient(700px 500px at 50% 110%,rgba(139,124,246,.10),transparent 60%),var(--bg);
color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px 80px}
nav{position:sticky;top:0;z-index:40;backdrop-filter:blur(14px);background:rgba(10,13,19,.72);border-bottom:1px solid var(--line)}
.nav-in{max-width:1120px;margin:0 auto;padding:12px 20px;display:flex;gap:18px;align-items:center;overflow-x:auto;white-space:nowrap}
.nav-in b{font-size:15px;margin-right:6px}
.nav-in a{color:var(--sub);font-size:14px}
.nav-in a:hover{color:var(--txt)}
.hero{text-align:center;padding:64px 0 30px}
.avatar{width:118px;height:118px;border-radius:50%;padding:3px;background:linear-gradient(135deg,var(--pink),var(--violet),var(--cyan));display:inline-block}
.avatar img{width:100%;height:100%;border-radius:50%;display:block;border:3px solid var(--bg)}
.hero h1{font-size:38px;margin-top:16px;letter-spacing:.5px}
.hero .handles{color:var(--sub);margin-top:6px;font-size:14px}
.hero .slogan{margin:18px auto 4px;font-size:17px;color:#f5c6d6;font-style:italic}
.hero .bio{color:var(--sub);font-size:14px;white-space:pre-line}
.jump{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:24px}
.jump a{padding:9px 18px;border-radius:999px;border:1px solid var(--line);background:var(--panel);font-size:14px;transition:.2s}
.jump a:hover{transform:translateY(-2px);border-color:var(--pink)}
.stats{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin:34px 0 6px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px 22px;text-align:center;min-width:110px}
.stat b{display:block;font-size:22px}
.stat span{color:var(--sub);font-size:12px}
section{margin-top:56px}
.sec-h{display:flex;align-items:baseline;gap:12px;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:20px}
.sec-h h2{font-size:24px}
.sec-h .cnt{color:var(--pink);font-size:14px}
.sec-h .more{margin-left:auto;color:var(--sub);font-size:13px}
.sub-h{font-size:16px;color:var(--sub);margin:26px 0 14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px;display:block;transition:.2s}
a.card:hover{transform:translateY(-3px);border-color:#33405a;background:var(--panel2)}
.card-top{display:flex;align-items:center;gap:8px}
.repo-name{font-weight:600;font-size:15px;color:#7dd3fc;word-break:break-all}
.badge{font-size:11px;color:var(--sub);border:1px solid var(--line);border-radius:999px;padding:1px 8px}
.badge.star{color:#fbbf24;border-color:#4a3a17}
.badge.lock{color:#f5c6d6}
.card-desc{color:var(--sub);font-size:13.5px;margin:8px 0 12px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:42px}
.card-meta{color:#6b7688;font-size:12.5px;display:flex;align-items:center;gap:5px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.sep{opacity:.5}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px;align-items:center}
.toolbar input{flex:1;min-width:200px;background:var(--panel);border:1px solid var(--line);color:var(--txt);
border-radius:999px;padding:9px 16px;font-size:14px;outline:none}
.toolbar input:focus{border-color:var(--pink)}
.chip{background:var(--panel);border:1px solid var(--line);color:var(--sub);border-radius:999px;padding:6px 13px;font-size:13px;cursor:pointer}
.chip.active{color:#fff;border-color:var(--pink);background:rgba(251,114,153,.16)}
.profile-strip{display:flex;flex-wrap:wrap;gap:18px;align-items:center;background:linear-gradient(120deg,rgba(251,114,153,.12),rgba(139,124,246,.08));
border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px;margin-bottom:20px}
.profile-strip .who b{font-size:19px}
.profile-strip .who p{color:var(--sub);font-size:13px}
.profile-strip .nums{display:flex;gap:20px;margin-left:auto;flex-wrap:wrap}
.profile-strip .nums div{text-align:center}
.profile-strip .nums b{display:block;font-size:18px}
.profile-strip .nums span{color:var(--sub);font-size:12px}
.btn{display:inline-block;padding:9px 18px;border-radius:999px;background:var(--pink);color:#fff;font-size:14px;font-weight:600}
.card.video{padding:0;overflow:hidden}
.thumb{position:relative;display:block;width:100%;border:0;background:none;cursor:pointer;padding:0}
.thumb img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}
.play-btn{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:34px;color:#fff;
background:rgba(5,8,14,.28);opacity:0;transition:.2s}
.thumb:hover .play-btn{opacity:1}
.dur{position:absolute;right:8px;bottom:8px;background:rgba(0,0,0,.72);color:#fff;font-size:12px;padding:1px 7px;border-radius:6px}
.v-body{padding:14px 16px 16px}
.v-body h4{font-size:15px;margin-bottom:6px}
.v-actions{display:flex;gap:8px;margin-top:12px}
.mini{border:1px solid var(--line);background:var(--panel2);color:var(--txt);border-radius:999px;padding:6px 14px;font-size:13px;cursor:pointer}
.mini.primary{background:var(--pink);border-color:var(--pink);color:#fff;font-weight:600}
.m3u8-panel{margin-top:22px;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px}
.m3u8-panel h3{font-size:16px;margin-bottom:6px}
.m3u8-panel p{color:var(--sub);font-size:13px}
.m3u8-panel pre{margin-top:12px;background:#07090e;border:1px solid var(--line);border-radius:10px;padding:12px;
font-size:11.5px;color:#8fd3a8;overflow-x:auto;max-height:180px;overflow-y:auto;white-space:pre-wrap;word-break:break-all}
.opus-row{display:flex;justify-content:space-between;gap:14px;padding:11px 6px;border-bottom:1px dashed var(--line);font-size:14.5px}
.opus-row:hover{color:#f5c6d6}
.opus-date{color:#6b7688;font-size:12.5px;white-space:nowrap}
.post-row{display:flex;flex-direction:column;padding:12px 6px;border-bottom:1px dashed var(--line)}
.post-row:hover .post-title{color:#7dd3fc}
.post-title{font-size:15px}
.post-meta{color:#6b7688;font-size:12.5px}
.social-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.social-card .card-top b{font-size:16px}
.social-card ul{list-style:none;margin-top:10px}
.social-card li{padding:7px 0;border-bottom:1px dashed var(--line);font-size:14px}
.social-card li:last-child{border:0}
.social-card li a:hover{color:#f5c6d6}
footer{margin-top:70px;border-top:1px solid var(--line);padding-top:22px;color:#6b7688;font-size:13px;text-align:center}
footer .fl{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-bottom:10px}
.modal{position:fixed;inset:0;background:rgba(3,5,9,.82);display:none;align-items:center;justify-content:center;z-index:80;padding:18px}
.modal.open{display:flex}
.modal-box{width:min(880px,100%);background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden}
.modal-box .m-h{display:flex;align-items:center;gap:10px;padding:13px 16px}
.modal-box .m-h b{flex:1;font-size:15px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.modal-box .x{background:none;border:0;color:var(--sub);font-size:22px;cursor:pointer}
.ratio{position:relative;padding-top:56.25%;background:#000}
.ratio iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.modal-box .m-f{display:flex;gap:8px;padding:13px 16px;flex-wrap:wrap}
@media (max-width:560px){.hero h1{font-size:30px}.grid{grid-template-columns:1fr}}
"""

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>天狗线人 · Xbox123z — 个人主页 Gallery</title>
<meta name="description" content="天狗线人（Xbox123z）的个人主页：GitHub 全部仓库、Bilibili「千早爱圣音」视频与动态、谷歌博客、Instagram 与 Facebook 一站展示。">
<style>{CSS}</style>
</head>
<body>
<nav><div class="nav-in">
  <b>🖼️ 天狗线人 Gallery</b>
  <a href="#github">GitHub 仓库</a><a href="#bilibili">Bilibili</a><a href="#blog">博客</a><a href="#social">社交</a>
  <a href="https://github.com/Xbox123z" target="_blank" rel="noopener">GitHub ↗</a>
  <a href="https://space.bilibili.com/3493110919203314" target="_blank" rel="noopener">B站空间 ↗</a>
</div></nav>
<div class="wrap">
<header class="hero">
  <span class="avatar"><img src="{esc(prof['avatar_url'])}" alt="天狗线人头像"></span>
  <h1>天狗线人</h1>
  <p class="handles">GitHub @Xbox123z · Bilibili 千早爱圣音 · Instagram @z8463384</p>
  <p class="slogan">「{esc(bp['slogan'])}」</p>
  <p class="bio">{esc((prof['bio'] or '').replace(chr(13), ''))}</p>
  <div class="jump">
    <a href="https://github.com/Xbox123z" target="_blank" rel="noopener">🐙 GitHub 主页</a>
    <a href="https://space.bilibili.com/3493110919203314" target="_blank" rel="noopener">📺 B站空间</a>
    <a href="https://www.instagram.com/z8463384/" target="_blank" rel="noopener">📸 Instagram</a>
    <a href="https://www.facebook.com/122142780963145822" target="_blank" rel="noopener">📘 Facebook</a>
    <a href="https://xbox123z-github.blogspot.com" target="_blank" rel="noopener">✍️ 博客 · xbox123z-github</a>

  </div>
  <div class="stats">
    <div class="stat"><b>{len(pub_repos)}</b><span>GitHub 公开仓库</span></div>
    <div class="stat"><b>{len(bili['videos'])}</b><span>B站投稿视频</span></div>
    <div class="stat"><b>{len(bili['opus'])}</b><span>精选图文动态</span></div>
    <div class="stat"><b>{len(blog1['posts'])}</b><span>博客文章</span></div>
    <div class="stat"><b>{bp['fans']}</b><span>B站粉丝</span></div>
  </div>
</header>

<section id="github">
  <div class="sec-h"><h2>🐙 GitHub 仓库</h2><span class="cnt">{len(pub_repos)} 个公开 · {len(priv_repos)} 个私有</span>
  <a class="more" href="https://github.com/Xbox123z?tab=repositories" target="_blank" rel="noopener">在 GitHub 查看全部 ↗</a></div>
  <div class="toolbar">
    <input id="repoSearch" type="search" placeholder="搜索仓库名或简介…">
    {''.join(chips)}
  </div>
  <div class="grid" id="repoGrid">
{repos_html}
  </div>
  <p id="repoEmpty" style="display:none;color:var(--sub);padding:12px 4px">没有匹配的仓库，换个关键词试试。</p>
  {priv_html}
</section>

<section id="bilibili">
  <div class="sec-h"><h2>📺 Bilibili · 千早爱圣音</h2><span class="cnt">视频 {len(bili['videos'])} · 图文动态 {len(bili['opus'])} 精选</span>
  <a class="more" href="https://space.bilibili.com/3493110919203314" target="_blank" rel="noopener">去B站空间 ↗</a></div>
  <div class="profile-strip">
    <div class="who"><b>千早爱圣音</b> <span class="badge">{esc(bp['level'])}</span>
      <p>UID 3493110919203314 · BanG Dream!（MyGO!!!!!／Ave Mujica）同好杂记<br>「{esc(bp['slogan'])}」</p></div>
    <div class="nums">
      <div><b>{bp['fans']}</b><span>粉丝</span></div>
      <div><b>{bp['following']}</b><span>关注</span></div>
      <div><b>{bp['likes']}</b><span>获赞</span></div>
      <div><b>{bp['total_play']}</b><span>总播放</span></div>
    </div>
    <a class="btn" href="https://space.bilibili.com/3493110919203314" target="_blank" rel="noopener">访问空间</a>
  </div>
  <div class="grid">
{videos_html}
  </div>
  <div class="m3u8-panel">
    <h3>🎞️ 视频直链索引（m3u8 播放列表）</h3>
    <p>本站全部 B 站视频的直链索引，生成于 {GEN_TIME}（CST）。可下载为 index.m3u8 后用 VLC、PotPlayer 等播放器打开连播。
    注意：B 站直链带时效签名，数小时后失效属正常现象；失效时用上方卡片的「内嵌播放」照常观看。</p>
    <pre>{esc(m3u8_text)}</pre>
    <div class="v-actions">
      <a class="mini primary" href="index.m3u8" download>⬇ 下载 index.m3u8</a>
      <button class="mini" id="copyM3u8">复制索引内容</button>
    </div>
  </div>
  <h3 class="sub-h">图文动态精选（2026-11-01）</h3>
  <div>
{opus_html}
  </div>
</section>

<section id="blog">
  <div class="sec-h"><h2>✍️ 谷歌博客</h2><span class="cnt">{len(blog1['posts'])} 篇文章</span></div>
  <div class="grid" style="margin-bottom:8px">
    <a class="card" href="https://xbox123z-github.blogspot.com" target="_blank" rel="noopener">
      <div class="card-top"><span class="repo-name">xbox123z-github</span></div>
      <p class="card-desc">技术向博客：项目实录与折腾记录。</p>
      <div class="card-meta">xbox123z-github.blogspot.com</div></a>
  </div>
{blog_posts_html_all}
</section>

<section id="social">
  <div class="sec-h"><h2>🌐 社交账号</h2></div>
  <div class="social-grid">
    <div class="card social-card">
      <div class="card-top"><b>📸 Instagram</b><span class="badge">@z8463384</span></div>
      <ul>
        <li><a href="https://www.instagram.com/reel/DfKP7HDjOz2/" target="_blank" rel="noopener">短剧《猪脚饭立规人》Reel ↗</a></li>
        <li><a href="https://www.instagram.com/p/DfMukVqjqrF/" target="_blank" rel="noopener">AetherV2Anime 项目图文 ↗</a></li>
        <li><a href="https://www.instagram.com/p/DfKOlUfjN_F/" target="_blank" rel="noopener">huawei-apk-repatch-skill 项目图文 ↗</a></li>
      </ul>
      <div class="v-actions"><a class="mini primary" href="https://www.instagram.com/z8463384/" target="_blank" rel="noopener">去 Instagram 主页</a></div>
    </div>
    <div class="card social-card">
      <div class="card-top"><b>📘 Facebook</b><span class="badge">刘惠琪</span></div>
      <ul>
        <li><a href="https://www.facebook.com/122142780963145822" target="_blank" rel="noopener">AetherV2Anime 项目帖 ↗</a></li>
        <li><a href="https://www.facebook.com/122142657411145822" target="_blank" rel="noopener">huawei-apk-repatch-skill 项目帖 ↗</a></li>
      </ul>
      <div class="v-actions"><a class="mini primary" href="https://www.facebook.com/122142780963145822" target="_blank" rel="noopener">去 Facebook 看最新帖</a></div>
    </div>
  </div>
</section>

<footer>
  <div class="fl">
    <a href="https://github.com/Xbox123z" target="_blank" rel="noopener">GitHub</a>
    <a href="https://space.bilibili.com/3493110919203314" target="_blank" rel="noopener">Bilibili</a>
    <a href="https://www.instagram.com/z8463384/" target="_blank" rel="noopener">Instagram</a>
    <a href="https://xbox123z-github.blogspot.com" target="_blank" rel="noopener">博客①</a>
    <a href="https://github.com/Xbox123z/personal-gallery" target="_blank" rel="noopener">本站源码</a>
  </div>
  <p>© 2026 天狗线人 Xbox123z · 本页数据汇总于 {GEN_TIME} CST · 部署于 Deno Deploy</p>
</footer>
</div>

<div class="modal" id="playerModal" role="dialog" aria-modal="true">
  <div class="modal-box">
    <div class="m-h"><b id="mTitle">视频播放</b><button class="x" id="mClose" aria-label="关闭">×</button></div>
    <div class="ratio"><iframe id="mFrame" src="" allow="autoplay; fullscreen; encrypted-media; picture-in-picture" allowfullscreen title="Bilibili 内嵌播放器"></iframe></div>
    <div class="m-f">
      <a class="mini primary" id="mOpen" href="#" target="_blank" rel="noopener">在 B 站打开 ↗</a>
      <button class="mini" id="mCopy">复制 BV 号</button>
    </div>
  </div>
</div>

<script>__GALLERY_JS__</script>
</body>
</html>
"""

GALLERY_JS = r"""
const grid = document.getElementById('repoGrid');
const cards = [...grid.querySelectorAll('.repo')];
const search = document.getElementById('repoSearch');
let curLang = 'all';
function applyFilter(){
  const q = search.value.trim().toLowerCase();
  let shown = 0;
  for (const c of cards){
    const okL = curLang === 'all' || c.dataset.lang === curLang;
    const okQ = !q || c.dataset.name.includes(q) || c.dataset.desc.includes(q);
    c.style.display = (okL && okQ) ? '' : 'none';
    if (okL && okQ) shown++;
  }
  document.getElementById('repoEmpty').style.display = shown ? 'none' : '';
}
search.addEventListener('input', applyFilter);
document.querySelectorAll('.chip').forEach(ch => ch.addEventListener('click', () => {
  document.querySelectorAll('.chip').forEach(x => x.classList.remove('active'));
  ch.classList.add('active'); curLang = ch.dataset.lang; applyFilter();
}));

const modal = document.getElementById('playerModal');
const frame = document.getElementById('mFrame');
let curBvid = '';
function openPlayer(bvid, title){
  curBvid = bvid;
  document.getElementById('mTitle').textContent = title;
  frame.src = 'https://player.bilibili.com/player.html?bvid=' + bvid + '&page=1&autoplay=0&danmaku=0&high_quality=1';
  document.getElementById('mOpen').href = 'https://www.bilibili.com/video/' + bvid + '/';
  modal.classList.add('open');
}
function closePlayer(){ modal.classList.remove('open'); frame.src = ''; }
document.querySelectorAll('[data-bvid]').forEach(el => el.addEventListener('click', () => openPlayer(el.dataset.bvid, el.dataset.title)));
document.getElementById('mClose').addEventListener('click', closePlayer);
modal.addEventListener('click', e => { if (e.target === modal) closePlayer(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closePlayer(); });
document.getElementById('mCopy').addEventListener('click', async e => {
  try { await navigator.clipboard.writeText(curBvid); e.target.textContent = '已复制 ' + curBvid; }
  catch { e.target.textContent = curBvid; }
  setTimeout(() => e.target.textContent = '复制 BV 号', 1600);
});
document.getElementById('copyM3u8').addEventListener('click', async e => {
  const text = document.querySelector('.m3u8-panel pre').textContent;
  try { await navigator.clipboard.writeText(text); e.target.textContent = '已复制'; }
  catch { e.target.textContent = '复制失败，请手动选择'; }
  setTimeout(() => e.target.textContent = '复制索引内容', 1600);
});
"""

open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(HTML.replace("__GALLERY_JS__", GALLERY_JS))
print("index.html bytes:", len(HTML.encode("utf-8")))
print("index.m3u8 lines:", m3u8_text.count("\n"))
print("repos:", len(pub_repos), "public /", len(priv_repos), "private | videos:", len(bili["videos"]))
