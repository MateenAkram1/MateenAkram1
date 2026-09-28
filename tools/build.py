#!/usr/bin/env python3
"""Build dark.svg, light.svg and README.md from profile.json + tools/portrait.json.

Standard library only:  python3 tools/build.py [--static OUTDIR]
--static writes animation-free copies (for previews) into OUTDIR instead.
"""
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1180, 610
MONO = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "dark": dict(
        bg0="#030712", bg1="#07111F", bg2="#0B1220",
        glass="#FFFFFF", glass_op=".035", glass_op2=".06",
        stroke="#FFFFFF", stroke_op=".10",
        text="#F8FAFC", muted="#94A3B8", dim="#64748B", label="#67E8F9",
        a1="#7C3AED", a2="#22D3EE", a3="#10B981",
        name1="#F8FAFC", name2="#C4B5FD", name3="#67E8F9",
        ascii1="#A78BFA", ascii2="#67E8F9", ascii3="#6EE7B7",
        pill="#0F172A", pill_op=".55", pill_stroke="#22D3EE", pill_stroke_op=".28",
        grid_op=".045", noise_op=".05", blob_op=".22", particle="#67E8F9",
        glow=True, shadow_op="0", sweep_op=".05", scan="#22D3EE",
        online="#10B981",
    ),
    "light": dict(
        bg0="#FFFFFF", bg1="#F8FAFC", bg2="#EEF6FF",
        glass="#FFFFFF", glass_op=".62", glass_op2=".75",
        stroke="#94A3B8", stroke_op=".35",
        text="#0F172A", muted="#475569", dim="#64748B", label="#2563EB",
        a1="#7C3AED", a2="#2563EB", a3="#0891B2",
        name1="#0F172A", name2="#1E40AF", name3="#0E7490",
        ascii1="#4C1D95", ascii2="#1D4ED8", ascii3="#0E7490",
        pill="#FFFFFF", pill_op=".85", pill_stroke="#2563EB", pill_stroke_op=".22",
        grid_op=".06", noise_op=".025", blob_op=".16", particle="#2563EB",
        glow=False, shadow_op=".10", sweep_op=".35", scan="#2563EB",
        online="#059669",
    ),
}

STATIC = False


def e(s):
    return escape(str(s), quote=True)


def reveal(delay, dur=0.5, dy=6):
    """Fade + rise in, once. Elements stay visible where SMIL is unsupported."""
    if STATIC:
        return ""
    total = delay + dur
    k = f"{delay / total:.3f}"
    out = (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k};1" '
           f'dur="{total:.2f}s" fill="freeze"/>')
    if dy:
        out += (f'<animateTransform attributeName="transform" type="translate" '
                f'values="0 {dy};0 {dy};0 0" keyTimes="0;{k};1" dur="{total:.2f}s" '
                f'calcMode="spline" keySplines="0 0 1 1;.2 .7 .2 1" fill="freeze"/>')
    return out


def xs(x, text, cw):
    return " ".join(f"{x + i * cw:.1f}" for i in range(len(text)))


def anim(s):
    return "" if STATIC else s


# ---------------------------------------------------------------- pieces

def defs(t, portrait_box):
    px, py, pw, ph = portrait_box
    cx, cy = px + pw / 2, py + ph / 2
    glow = ""
    if t["glow"]:
        glow = """
    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1.4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""
    return f"""
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t['bg1']}"/>
      <stop offset=".55" stop-color="{t['bg0']}"/>
      <stop offset="1" stop-color="{t['bg2']}"/>
    </linearGradient>
    <radialGradient id="blobA" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="{t['a1']}" stop-opacity="{t['blob_op']}"/>
      <stop offset="1" stop-color="{t['a1']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="blobB" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="{t['a2']}" stop-opacity="{t['blob_op']}"/>
      <stop offset="1" stop-color="{t['a2']}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="blobC" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="{t['a3']}" stop-opacity="{float(t['blob_op']) * .7:.3f}"/>
      <stop offset="1" stop-color="{t['a3']}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="border" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
      <stop offset="0" stop-color="{t['a1']}"/>
      <stop offset=".5" stop-color="{t['a2']}"/>
      <stop offset="1" stop-color="{t['a3']}"/>
      {anim(f'<animateTransform attributeName="gradientTransform" type="rotate" values="0 590 305;360 590 305" dur="18s" repeatCount="indefinite"/>')}
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t['a1']}"/>
      <stop offset=".5" stop-color="{t['a2']}"/>
      <stop offset="1" stop-color="{t['a3']}"/>
    </linearGradient>
    <linearGradient id="nameFill" gradientUnits="userSpaceOnUse" x1="528" y1="0" x2="1000" y2="0">
      <stop offset="0" stop-color="{t['name1']}"/>
      <stop offset=".55" stop-color="{t['name2']}"/>
      <stop offset="1" stop-color="{t['name3']}"/>
      {anim('<animate attributeName="x2" values="1000;1300;1000" dur="10s" repeatCount="indefinite"/>')}
    </linearGradient>
    <linearGradient id="asciiFill" gradientUnits="userSpaceOnUse" x1="{px}" y1="{py}" x2="{px + pw}" y2="{py + ph}">
      <stop offset="0" stop-color="{t['ascii1']}"/>
      <stop offset=".5" stop-color="{t['ascii2']}"/>
      <stop offset="1" stop-color="{t['ascii3']}"/>
      {anim(f'<animateTransform attributeName="gradientTransform" type="rotate" values="0 {cx:.0f} {cy:.0f};360 {cx:.0f} {cy:.0f}" dur="24s" repeatCount="indefinite"/>')}
    </linearGradient>
    <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['scan']}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{t['scan']}" stop-opacity=".22"/>
      <stop offset="1" stop-color="{t['scan']}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset=".5" stop-color="#FFFFFF" stop-opacity="{t['sweep_op']}"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="glassEdge" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t['stroke']}" stop-opacity="{float(t['stroke_op']) * 1.6:.2f}"/>
      <stop offset="1" stop-color="{t['stroke']}" stop-opacity="{float(t['stroke_op']) * .6:.2f}"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{t['muted']}" stroke-opacity="{t['grid_op']}" stroke-width="1"/>
    </pattern>
    <filter id="noise" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>
      <feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1 0"/>
    </filter>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#0F172A" flood-opacity="{t['shadow_op']}"/>
    </filter>{glow}
    <clipPath id="frameClip"><rect x="12" y="12" width="{W - 24}" height="{H - 24}" rx="24"/></clipPath>
    <clipPath id="leftClip"><rect x="36" y="76" width="436" height="498" rx="16"/></clipPath>
    <clipPath id="rightClip"><rect x="496" y="76" width="648" height="498" rx="16"/></clipPath>
    <clipPath id="portraitClip"><rect x="{px - 12}" y="{py - 6}" width="{pw + 24}" height="{ph + 12}"/></clipPath>
  </defs>"""


def background(t):
    particles = []
    pts = [(484, 160, 7), (484, 420, 9), (300, 68, 8), (820, 66, 10), (200, 590, 7),
           (700, 590, 9), (1156, 260, 11), (24, 360, 8), (1000, 588, 10), (484, 300, 12)]
    for i, (x, y, d) in enumerate(pts):
        r = 1.1 if i % 3 else 1.6
        particles.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{t["particle"]}" opacity=".35">'
            + anim(f'<animate attributeName="cy" values="{y};{y - 6};{y}" dur="{d}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values=".1;.45;.1" dur="{d * .8:.1f}s" repeatCount="indefinite"/>')
            + "</circle>")
    return f"""
  <g clip-path="url(#frameClip)">
    <rect x="12" y="12" width="{W - 24}" height="{H - 24}" fill="url(#bg)"/>
    <ellipse cx="220" cy="140" rx="340" ry="260" fill="url(#blobA)">
      {anim('<animate attributeName="cx" values="220;300;220" dur="22s" repeatCount="indefinite"/>')}
    </ellipse>
    <ellipse cx="1000" cy="480" rx="380" ry="280" fill="url(#blobB)">
      {anim('<animate attributeName="cx" values="1000;900;1000" dur="26s" repeatCount="indefinite"/>')}
    </ellipse>
    <ellipse cx="760" cy="80" rx="260" ry="180" fill="url(#blobC)">
      {anim('<animate attributeName="cy" values="80;140;80" dur="20s" repeatCount="indefinite"/>')}
    </ellipse>
    <rect x="12" y="12" width="{W - 24}" height="{H - 24}" fill="url(#grid)"/>
    <rect x="12" y="12" width="{W - 24}" height="{H - 24}" filter="url(#noise)" opacity="{t['noise_op']}"/>
    {''.join(particles)}
  </g>"""


def titlebar(t, p):
    host = f"{p.get('username') or 'developer'}@{p.get('host') or 'profile'}"
    tabs = ["Code", "Projects", "Experience", "Contact"]
    x, tab_svg = 112, []
    for i, name in enumerate(tabs):
        color = t["text"] if i == 0 else t["dim"]
        tab_svg.append(f'<text x="{x}" y="39" class="t11" fill="{color}">{name}</text>')
        if i == 0:
            tab_svg.append(f'<rect x="{x}" y="50" width="{len(name) * 6.6:.1f}" height="2" rx="1" fill="url(#accent)"/>')
        x += len(name) * 6.6 + 24
    return f"""
  <g>{reveal(0, .4, 0)}
    <line x1="12" y1="56" x2="{W - 12}" y2="56" stroke="{t['stroke']}" stroke-opacity="{t['stroke_op']}"/>
    <circle cx="40" cy="34" r="6" fill="#FF5F57"/>
    <circle cx="60" cy="34" r="6" fill="#FEBC2E"/>
    <circle cx="80" cy="34" r="6" fill="#28C840"/>
    {''.join(tab_svg)}
    <text x="{W / 2}" y="39" class="t12" fill="{t['muted']}" text-anchor="middle">{e(host)}:~</text>
    <rect x="1054" y="23" width="90" height="22" rx="11" fill="{t['online']}" fill-opacity=".12" stroke="{t['online']}" stroke-opacity=".45"/>
    <circle cx="1070" cy="34" r="3.5" fill="{t['online']}">
      {anim('<animate attributeName="opacity" values="1;.35;1" dur="2s" repeatCount="indefinite"/>')}
    </circle>
    <text x="1080" y="38.5" class="t11 b" fill="{t['online']}" letter-spacing="1.2">ONLINE</text>
  </g>"""


def panel(t, x, y, w, h, clip, delay):
    sweep = anim(f'<rect x="{x - 200}" y="{y}" width="160" height="{h}" fill="url(#sweep)" transform="skewX(-18)">'
                 f'<animate attributeName="x" values="{x - 260};{x + w + 200};{x + w + 200}" keyTimes="0;.35;1" '
                 f'dur="9s" begin="{delay + 1.5:.1f}s" repeatCount="indefinite"/></rect>')
    return f"""
  <g filter="url(#shadow)">{reveal(delay, .5, 0)}
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{t['glass']}" fill-opacity="{t['glass_op']}" stroke="url(#glassEdge)"/>
    <rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="40" rx="15" fill="{t['glass']}" fill-opacity="{t['glass_op2']}"/>
    <g clip-path="url(#{clip})">{sweep}</g>
  </g>"""


def portrait(t, rows, cols, box):
    px, py, pw, ph = box
    fs = ph / len(rows)
    lines = []
    for i, r in enumerate(rows):
        r = r.ljust(cols)
        y = py + fs * (i + 0.8)
        a = "" if STATIC else (
            f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{(0.25 + i * 0.02) / (0.5 + i * 0.02):.3f};1" '
            f'dur="{0.5 + i * 0.02:.2f}s" fill="freeze"/>')
        lines.append(f'<text x="{px}" y="{y:.2f}" textLength="{pw}" lengthAdjust="spacing">{e(r)}{a}</text>')
    glow = ' filter="url(#glow)"' if t["glow"] else ""
    return f"""
  <g clip-path="url(#portraitClip)">
    <g class="ascii" fill="url(#asciiFill)"{glow} font-size="{fs:.2f}" xml:space="preserve">
      {anim('<animate attributeName="opacity" values="1;1;.82;1;1;.9;1" keyTimes="0;.62;.63;.65;.9;.91;1" dur="9s" begin="2s" repeatCount="indefinite"/>')}
      {anim('<animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="7s" begin="2s" repeatCount="indefinite"/>')}
      {''.join(lines)}
    </g>
    <rect x="{px - 12}" y="{py - 40}" width="{pw + 24}" height="40" fill="url(#scan)">
      {anim(f'<animate attributeName="y" values="{py - 40};{py + ph};{py + ph}" keyTimes="0;.6;1" dur="6s" begin="1.6s" repeatCount="indefinite"/>')}
    </rect>
  </g>"""


def brackets(t, x, y, w, h, s=14):
    c = f'stroke="{t["a2"]}" stroke-opacity=".6" stroke-width="1.5" fill="none" stroke-linecap="round"'
    return (f'<path d="M{x} {y + s}V{y}H{x + s}M{x + w - s} {y}H{x + w}V{y + s}'
            f'M{x + w} {y + h - s}V{y + h}H{x + w - s}M{x + s} {y + h}H{x}V{y + h - s}" {c}/>')


def left(t, p, portrait_data):
    rows = portrait_data["dark" if t is THEMES["dark"] else "light"]
    cols = portrait_data["cols"]
    ph = 330
    fs = ph / len(rows)
    pw = round(cols * fs * 0.6)
    box = (254 - pw // 2, 126, pw, ph)
    out = [f"""
  <g>{reveal(.2, .4, 0)}
    <text x="56" y="101" class="t11 b" fill="{t['label']}" letter-spacing="2">VISUAL.MAP</text>
    <text x="452" y="101" class="t11" fill="{t['dim']}" text-anchor="end">portrait.ascii · {cols}×{len(rows)}</text>
    {brackets(t, box[0] - 18, box[1] - 10, pw + 36, ph + 20)}
  </g>"""]
    out.append(portrait(t, rows, cols, box))
    cy = 494
    if p.get("tag"):
        out.append(f'<g>{reveal(1.6)}<text x="254" y="{cy}" class="t11 b" fill="{t["label"]}" '
                   f'text-anchor="middle" letter-spacing="2">[ {e(p["tag"])} ]</text></g>')
        cy += 22
    if p.get("tagline"):
        out.append(f'<g>{reveal(1.8)}<text x="254" y="{cy}" class="t13" fill="{t["muted"]}" '
                   f'text-anchor="middle">{e(p["tagline"])}</text></g>')
    cmd = p.get("command") or "build --ship"
    prompt = f"~/profile $ {cmd}"
    cx = 70 + len(prompt) * 7.8 + 2
    out.append(f"""
  <g>{reveal(2.0)}
    <rect x="56" y="534" width="396" height="26" rx="8" fill="{t['pill']}" fill-opacity="{t['pill_op']}" stroke="{t['stroke']}" stroke-opacity="{t['stroke_op']}"/>
    <text x="{xs(70, prompt, 7.8)}" y="551.5" class="t13"><tspan fill="{t['a3']}">~/profile</tspan><tspan fill="{t['dim']}"> $ </tspan><tspan fill="{t['text']}">{e(cmd)}</tspan></text>
    <rect x="{cx:.1f}" y="540" width="8" height="15" fill="{t['a2']}">
      {anim('<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/>')}
    </rect>
  </g>""")
    return "".join(out), box


def role_rotator(t, roles, x, y, fs=17, begin=1.2):
    cw = fs * 0.6
    if len(roles) <= 1 or STATIC:
        text = roles[0] if roles else ""
        return (f'<text x="{xs(x, text, cw)}" y="{y}" class="b" font-size="{fs}" fill="{t["a2"]}">{e(text)}</text>'
                f'<rect x="{x + len(text) * cw + 3:.1f}" y="{y - fs * .8:.1f}" width="2.5" height="{fs:.1f}" fill="{t["a2"]}">'
                + anim('<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/>')
                + "</rect>")
    step, hold, fade = 0.065, 2.2, 0.35
    spans = []
    for r in roles:
        spans.append(0.3 + step * len(r) + hold + fade)
    total = sum(spans)
    starts = [sum(spans[:i]) for i in range(len(roles))]

    def kt(v):
        return f"{min(max(v / total, 0), 1):.4f}"

    parts = []
    cur_vals, cur_times = [], []
    for ri, r in enumerate(roles):
        s0 = starts[ri]
        t_end = s0 + spans[ri]
        t_fade = t_end - fade
        cur_vals.append(f"{x}"); cur_times.append(s0)
        for j, ch in enumerate(r):
            ta = s0 + 0.3 + j * step
            cur_vals.append(f"{x + (j + 1) * cw:.1f}"); cur_times.append(ta)
            if ch == " ":
                continue
            keys = [(0, 0), (ta, 0), (ta + 0.01, 1), (t_fade, 1), (t_end, 0)]
            if t_end < total - 1e-6:
                keys.append((total, 0))
            vals = ";".join(str(v) for _, v in keys)
            times = ";".join(kt(k) for k, _ in keys)
            base = "1" if ri == 0 else "0"
            parts.append(
                f'<tspan x="{x + j * cw:.1f}" opacity="{base}">{e(ch)}'
                f'<animate attributeName="opacity" values="{vals}" keyTimes="{times}" dur="{total:.2f}s" '
                f'begin="{begin}s" repeatCount="indefinite"/></tspan>')
    # Cursor follows the last typed character (discrete steps); keyTimes must start at 0.
    cur_times[0] = 0
    cursor_x = x + len(roles[0]) * cw
    return (f'<text y="{y}" class="b" font-size="{fs}" fill="{t["a2"]}">{"".join(parts)}</text>'
            f'<rect x="{cursor_x + 3:.1f}" y="{y - fs * .8:.1f}" width="2.5" height="{fs:.1f}" fill="{t["a2"]}">'
            f'<animate attributeName="x" values="{";".join(str(float(v) + 3) for v in cur_vals)}" '
            f'keyTimes="{";".join(kt(v) for v in cur_times)}" calcMode="discrete" dur="{total:.2f}s" '
            f'begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/>'
            f'</rect>')


def right(t, p):
    X, LBL, VAL, XR = 528, 636, 652, 1112
    host = f"{p.get('username') or 'developer'}@{p.get('host') or 'profile'}"
    out = [f"""
  <g>{reveal(.3, .4, 0)}
    <text x="{X}" y="101" class="t11 b" fill="{t['label']}" letter-spacing="2">SYSTEM.INFO</text>
    <text x="{XR}" y="101" class="t11" text-anchor="end"><tspan fill="{t['a3']}">{e(host)}</tspan><tspan fill="{t['dim']}">:~$ </tspan><tspan fill="{t['muted']}">./profile.sh</tspan></text>
  </g>"""]
    if p.get("name"):
        out.append(f'<g>{reveal(.9, .6, 8)}<text x="{X}" y="166" class="b" font-size="36" '
                   f'fill="url(#nameFill)" letter-spacing="-.5">{e(p["name"])}</text></g>')
    roles = p.get("roles") or ([p["headline"]] if p.get("headline") else [])
    if roles:
        out.append(f'<g>{reveal(1.1, .4, 4)}<text x="{X}" y="199" class="b" font-size="17" fill="{t["a1"]}">&gt;</text>'
                   f'{role_rotator(t, roles, X + 22, 199)}</g>')
    out.append(f'<line x1="{X}" y1="220" x2="{XR}" y2="220" stroke="{t["stroke"]}" stroke-opacity="{t["stroke_op"]}" stroke-dasharray="3 5"/>')

    rows = []
    for key, label in (("role", "ROLE"), ("company", "COMPANY"), ("location", "LOCATION"),
                       ("experience", "EXPERIENCE"), ("education", "EDUCATION")):
        if p.get(key):
            rows.append((label, p[key]))
    if p.get("focus"):
        rows.append(("FOCUS", "  ·  ".join(p["focus"])))
    rows = rows[-5:] if len(rows) > 5 else rows
    y, d = 248, 1.4
    for label, value in rows[:5]:
        check_fit(value, 13, XR - VAL, label)
        out.append(f'<g>{reveal(d, .4, 4)}<text x="{LBL}" y="{y}" class="t11 b" fill="{t["label"]}" '
                   f'text-anchor="end" letter-spacing="1.5">{label}</text>'
                   f'<text x="{VAL}" y="{y}" class="t13" fill="{t["text"]}">{e(value)}</text></g>')
        y += 26
        d += 0.12

    if p.get("stack"):
        y += 12
        out.append(f'<g>{reveal(d, .4, 4)}<text x="{LBL}" y="{y + 4}" class="t11 b" fill="{t["label"]}" '
                   f'text-anchor="end" letter-spacing="1.5">STACK</text></g>')
        px, py, row = VAL, y - 12, 0
        for i, tech in enumerate(p["stack"]):
            w = len(tech) * 7.2 + 30
            if px + w > XR:
                row += 1
                if row == 2:
                    break
                px, py = VAL, py + 32
            float_anim = anim(f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -1.5;0 0" '
                              f'dur="{4 + (i % 3)}s" begin="{3 + i * .3:.1f}s" repeatCount="indefinite"/>')
            out.append(
                f'<g>{reveal(d + .1 + i * .06, .35, 4)}<g>{float_anim}'
                f'<rect x="{px}" y="{py}" width="{w:.1f}" height="24" rx="12" fill="{t["pill"]}" fill-opacity="{t["pill_op"]}" '
                f'stroke="{t["pill_stroke"]}" stroke-opacity="{t["pill_stroke_op"]}"/>'
                f'<circle cx="{px + 13}" cy="{py + 12}" r="3" fill="{[t["a1"], t["a2"], t["a3"]][i % 3]}"/>'
                f'<text x="{px + 22}" y="{py + 16.5}" class="t12" fill="{t["text"]}">{e(tech)}</text></g></g>')
            px += w + 8
        y = py + 24 + 30
        d += 0.6

    projects = [pr for pr in p.get("projects", []) if pr.get("name") and not pr.get("readme_only")]
    if projects:
        y += 8
        out.append(f'<g>{reveal(d, .4, 4)}<text x="{LBL}" y="{y}" class="t11 b" fill="{t["label"]}" '
                   f'text-anchor="end" letter-spacing="1.5">BUILDING</text></g>')
        for pr in projects[:3]:
            if y > 516:
                break
            nx = VAL + len(pr["name"]) * 7.8 + 18
            desc = pr.get("description", "")
            check_fit(pr["name"] + "   " + desc, 13, XR - VAL, "project")
            out.append(f'<g>{reveal(d, .4, 4)}<text x="{VAL}" y="{y}" class="t13 b" fill="{t["a2"]}">{e(pr["name"])}</text>'
                       f'<text x="{nx:.1f}" y="{y}" class="t13" fill="{t["muted"]}">{e(desc)}</text></g>')
            y += 22
            d += 0.12

    links = link_list(p)
    if p.get("banner_links"):
        by_key = {k: (k, u, s) for k, u, s in links}
        links = [by_key[k] for k in p["banner_links"] if k in by_key]
    links = [(k, u, BANNER_LABEL.get(k, lambda s: s)(s)) for k, u, s in links]
    if links:
        out.append(f'<line x1="{X}" y1="528" x2="{XR}" y2="528" stroke="{t["stroke"]}" stroke-opacity="{t["stroke_op"]}" stroke-dasharray="3 5"/>')
        out.append(f'<g>{reveal(d + .2, .4, 4)}<text x="{LBL}" y="553" class="t11 b" fill="{t["label"]}" '
                   f'text-anchor="end" letter-spacing="1.5">LINKS</text>')
        lx = VAL
        for label, url, shown in links[:4]:
            out.append(f'<a href="{e(url)}" target="_blank"><text x="{lx:.1f}" y="553" class="t12" fill="{t["text"]}">'
                       f'<tspan fill="{t["a3"]}">↗ </tspan>{e(shown)}</text></a>')
            lx += (len(shown) + 2) * 7.2 + 20
        out.append("</g>")
        if lx - 20 > XR - 0:
            print(f"warning: banner links end at x={lx - 20:.0f}, past {XR} - use fewer banner_links", file=sys.stderr)
    return "".join(out)


BANNER_LABEL = {
    "github": lambda s: "github/" + s.split("/")[-1],
    "linkedin": lambda s: "LinkedIn",
    "portfolio": lambda s: "Portfolio",
    "x": lambda s: "x/" + s.split("/")[-1],
    "youtube": lambda s: "YouTube",
    "email": lambda s: "Email",
}


def link_list(p):
    links = p.get("links", {})
    out = []
    order = [("github", "https://github.com/"), ("linkedin", "https://linkedin.com/in/"), ("portfolio", ""),
             ("medium", ""), ("x", "https://x.com/"), ("youtube", ""), ("email", "mailto:")]
    for key, prefix in order:
        v = (links.get(key) or "").strip()
        if not v:
            continue
        url = v if v.startswith(("http", "mailto:")) else prefix + v
        shown = v.replace("https://", "").replace("http://", "").replace("www.", "").replace("mailto:", "").rstrip("/")
        out.append((key, url, shown))
    return out


def check_fit(text, fs, width, what):
    if len(text) * fs * 0.6 > width:
        print(f"warning: {what} '{text}' is ~{len(text) * fs * .6:.0f}px, wider than {width}px - shorten it",
              file=sys.stderr)


def aria(p):
    bits = [p.get("name") or "Developer profile"]
    if p.get("headline"):
        bits.append(p["headline"])
    if p.get("role") and p.get("company"):
        bits.append(f"{p['role']} at {p['company']}")
    if p.get("location"):
        bits.append(p["location"])
    if p.get("stack"):
        bits.append("Stack: " + ", ".join(p["stack"]))
    return " — ".join(bits) + ". ASCII portrait in a terminal-style banner."


def svg(theme, p, portrait_data):
    t = THEMES[theme]
    left_svg, box = left(t, p, portrait_data)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(aria(p))}">
  <title>{e(p.get('name') or 'Developer profile')}</title>
  <desc>{e(aria(p))}</desc>
  <style>
    text {{ font-family: {MONO}; }}
    .t11 {{ font-size: 11px; }} .t12 {{ font-size: 12px; }} .t13 {{ font-size: 13px; }}
    .b {{ font-weight: 700; }}
    .ascii text {{ font-family: {MONO}; white-space: pre; }}
  </style>
{defs(t, box)}
{background(t)}
  <rect x="12.5" y="12.5" width="{W - 25}" height="{H - 25}" rx="24" fill="none" stroke="{t['stroke']}" stroke-opacity="{t['stroke_op']}"/>
  <rect x="12.5" y="12.5" width="{W - 25}" height="{H - 25}" rx="24" fill="none" stroke="url(#border)" stroke-opacity=".55" stroke-width="1.2"/>
{titlebar(t, p)}
{panel(t, 36, 76, 436, 498, 'leftClip', .1)}
{panel(t, 496, 76, 648, 498, 'rightClip', .25)}
{left_svg}
{right(t, p)}
</svg>
"""


# ---------------------------------------------------------------- README

def readme(p):
    r = p.get("readme", {})
    name = p.get("name") or "Developer"
    lines = [
        '<div align="center">', "",
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="./dark.svg">',
        '  <source media="(prefers-color-scheme: light)" srcset="./light.svg">',
        f'  <img src="./dark.svg" alt="{e(aria(p))}" width="100%">',
        "</picture>", "", "</div>", "",
    ]
    if r.get("intro"):
        lines += [f"### Hi, I'm {name}", "", r["intro"], ""]
    if r.get("about") or p.get("focus"):
        lines += ["## About", ""]
        lines += [f"- {a}" for a in r.get("about", [])]
        if p.get("focus"):
            lines.append(f"- **Focus:** {' · '.join(p['focus'])}")
        lines.append("")
    if r.get("experience"):
        lines += ["## Experience", ""]
        for x in r["experience"]:
            title = " · ".join(v for v in (x.get("role"), x.get("company")) if v)
            meta = " · ".join(v for v in (x.get("dates"), x.get("location")) if v)
            lines.append(f"### {title}")
            if meta:
                lines.append(f"<sub>{meta}</sub>")
            lines.append("")
            if x.get("summary"):
                lines.append(x["summary"])
            lines += [f"- {h}" for h in x.get("highlights", [])]
            lines.append("")
    projects = [pr for pr in p.get("projects", []) if pr.get("name")]
    if projects:
        lines += ["## Featured Projects", "", "| Project | What it does | Built with |", "| --- | --- | --- |"]
        for pr in projects:
            nm = f"[**{pr['name']}**]({pr['url']})" if pr.get("url") else f"**{pr['name']}**"
            tech = " ".join(f"`{x}`" for x in pr.get("tech", []))
            lines.append(f"| {nm} | {pr.get('summary') or pr.get('description', '')} | {tech} |")
        lines.append("")
        if r.get("more_projects"):
            lines += ["<details>", "<summary><b>More projects</b></summary>", ""]
            lines += [f"- {m}" for m in r["more_projects"]]
            lines += ["", "</details>", ""]
    groups = {k: v for k, v in r.get("stack_groups", {}).items() if v}
    if groups:
        lines += ["## Engineering Stack", "", "| Area | Tools |", "| --- | --- |"]
        lines += [f"| {k} | {' · '.join(f'`{v}`' for v in vs)} |" for k, vs in groups.items()]
        lines.append("")
    elif p.get("stack"):
        lines += ["## Engineering Stack", "", " ".join(f"`{s}`" for s in p["stack"]), ""]
    for key, title in (("education", "Education"), ("certifications", "Certifications")):
        if r.get(key):
            lines += [f"## {title}", ""] + [f"- {v}" for v in r[key]] + [""]
    if r.get("writing"):
        lines += ["## Writing", ""]
        for w in r["writing"]:
            lines.append(f"- [{w['title']}]({w['url']})" if isinstance(w, dict) else f"- {w}")
        lines.append("")
    user = p.get("username")
    if user and r.get("github_stats", True):
        lines += ["## GitHub Activity", "", '<div align="center">', "",
                  "<picture>",
                  f'  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username={user}&show_icons=true&hide_border=true&bg_color=0B1220&title_color=22D3EE&icon_color=7C3AED&text_color=CBD5E1">',
                  f'  <img alt="GitHub stats for {user}" src="https://github-readme-stats.vercel.app/api?username={user}&show_icons=true&hide_border=true&title_color=2563EB&icon_color=7C3AED">',
                  "</picture>", "", "</div>", ""]
    links = link_list(p)
    if links:
        lines += ["## Connect", ""]
        names = {"github": "GitHub", "linkedin": "LinkedIn", "portfolio": "Portfolio", "medium": "Medium",
                 "x": "X", "youtube": "YouTube", "email": "Email"}
        lines.append(" · ".join(f"[{names[k]}]({u})" for k, u, _ in links))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


PLACEHOLDER_HINTS = ("Your ", "your-", "you@example.com", "N+ years", "project-one", "project-two",
                     "Focus Area", "One-line", "Short supporting phrase", "Language", "Framework")


def warn_placeholders(p, path="profile"):
    if isinstance(p, dict):
        for k, v in p.items():
            if not k.startswith("_"):
                warn_placeholders(v, f"{path}.{k}")
    elif isinstance(p, list):
        for i, v in enumerate(p):
            warn_placeholders(v, f"{path}[{i}]")
    elif isinstance(p, str) and any(h in p for h in PLACEHOLDER_HINTS):
        print(f"placeholder still set: {path} = {p!r}", file=sys.stderr)


def main():
    global STATIC
    out_dir = ROOT
    if "--static" in sys.argv:
        STATIC = True
        out_dir = Path(sys.argv[sys.argv.index("--static") + 1])
    p = json.loads((ROOT / "profile.json").read_text())
    warn_placeholders(p)
    portrait_data = json.loads((ROOT / "tools" / "portrait.json").read_text())
    for theme in ("dark", "light"):
        (out_dir / f"{theme}.svg").write_text(svg(theme, p, portrait_data))
    if not STATIC:
        (ROOT / "README.md").write_text(readme(p))
    print(f"built {out_dir}/dark.svg, light.svg" + ("" if STATIC else ", README.md"))


if __name__ == "__main__":
    main()
