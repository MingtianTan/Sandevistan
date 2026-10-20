"""Draw the SPINE / Sandevistan figures as SVG (rendered to PNG with headless Chrome by render.sh)."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent
BG, PANEL, LINE = "#0b0f15", "#121824", "#243041"
INK, SOFT, FAINT = "#e8eef5", "#a9b6c5", "#6f7f92"
CYAN, MAG, YEL, GRN, ORG = "#19e6ff", "#ff2fd1", "#ffe34d", "#3dff9a", "#ff8a3d"
SANS = "font-family=\"'Source Sans 3','Segoe UI',system-ui,sans-serif\""
DISP = "font-family=\"'Rajdhani','Source Sans 3',system-ui,sans-serif\""
MONO = "font-family=\"'IBM Plex Mono',ui-monospace,Menlo,monospace\""


def head(w, h, label):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">',
            '<defs>'
            '<marker id="a-cyan" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#19e6ff"/></marker>'
            '<marker id="a-mag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#ff2fd1"/></marker>'
            '<marker id="a-yel" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#ffe34d"/></marker>'
            '<marker id="a-soft" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#a9b6c5"/></marker>'
            '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#1a2230" stroke-width="1"/></pattern>'
            '</defs>',
            f'<rect width="{w}" height="{h}" fill="{BG}"/>', f'<rect width="{w}" height="{h}" fill="url(#grid)" opacity="0.6"/>']


def box(svg, x, y, w, h, color, title, lines, sub=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{PANEL}" stroke="{LINE}"/>')
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{color}" filter="url(#glow)"/>')
    svg.append(f'<text x="{x + 16}" y="{y + 36}" font-size="22" font-weight="700" fill="{color}" {DISP}>{title}</text>')
    if sub:
        svg.append(f'<text x="{x + w - 16}" y="{y + 36}" font-size="13" fill="{FAINT}" text-anchor="end" {MONO}>{sub}</text>')
    for i, line in enumerate(lines):
        svg.append(f'<text x="{x + 16}" y="{y + 62 + i * 19}" font-size="14" fill="{SOFT}" {SANS}>{line}</text>')


# ---------------- Figure 1: three loops ----------------
W, H = 1180, 440
svg = head(W, H, "Three control loops: VLA, SPINE reflex layer, low-level controller")
box(svg, 40, 70, 320, 230, MAG, "VLA  ·  cortex", ["language, images, proprioception", "plans an action chunk: 50 steps at 20 Hz", "inference 100–300 ms, re-plans at 1–10 Hz", "", "knows what to do, not how the", "world moved in the last 50 ms"], "1–10 Hz")
box(svg, 430, 70, 320, 230, CYAN, "SPINE  ·  spinal cord", ["IMU, joint and body velocities,", "fast visual features, the VLA's chunk", "and intent token", "", "outputs a correction, a time-scaling", "of the plan, or a takeover"], "100–500 Hz")
box(svg, 820, 70, 320, 230, YEL, "controller  ·  muscle", ["MPC / PID / joint servos", "tracks whatever target it is given", "", "per-robot adapter: body twist", "and wrench targets → this robot's", "actuators"], "120–1000 Hz")
# arrows
svg.append(f'<line x1="362" y1="150" x2="428" y2="150" stroke="{MAG}" stroke-width="2.5" marker-end="url(#a-mag)"/>')
svg.append(f'<text x="395" y="128" font-size="11.5" fill="{MAG}" text-anchor="middle" {MONO}>chunk +</text><text x="395" y="141" font-size="11.5" fill="{MAG}" text-anchor="middle" {MONO}>intent</text>')
svg.append(f'<line x1="428" y1="222" x2="362" y2="222" stroke="{CYAN}" stroke-width="2.5" marker-end="url(#a-cyan)"/>')
svg.append(f'<text x="395" y="243" font-size="11.5" fill="{CYAN}" text-anchor="middle" {MONO}>state</text>')
svg.append(f'<text x="395" y="256" font-size="11.5" fill="{CYAN}" text-anchor="middle" {MONO}>token</text>')
svg.append(f'<line x1="752" y1="185" x2="818" y2="185" stroke="{CYAN}" stroke-width="2.5" marker-end="url(#a-cyan)"/>')
svg.append(f'<text x="785" y="163" font-size="11.5" fill="{CYAN}" text-anchor="middle" {MONO}>corrected</text>')
svg.append(f'<text x="785" y="176" font-size="11.5" fill="{CYAN}" text-anchor="middle" {MONO}>target</text>')
# sensors
svg.append(f'<rect x="430" y="330" width="320" height="60" rx="8" fill="{PANEL}" stroke="{CYAN}" stroke-dasharray="4 3"/>')
svg.append(f'<text x="590" y="356" font-size="14" fill="{INK}" text-anchor="middle" {SANS}>fast senses: IMU · joint encoders · optical flow / event camera</text>')
svg.append(f'<text x="590" y="376" font-size="12" fill="{FAINT}" text-anchor="middle" {MONO}>the vestibular system and muscle spindles of the robot</text>')
svg.append(f'<line x1="590" y1="328" x2="590" y2="304" stroke="{CYAN}" stroke-width="2" marker-end="url(#a-cyan)"/>')
svg.append(f'<rect x="40" y="330" width="320" height="60" rx="8" fill="{PANEL}" stroke="{MAG}" stroke-dasharray="4 3"/>')
svg.append(f'<text x="200" y="356" font-size="14" fill="{INK}" text-anchor="middle" {SANS}>slow senses: cameras at 20 Hz · language</text>')
svg.append(f'<text x="200" y="376" font-size="12" fill="{FAINT}" text-anchor="middle" {MONO}>what the eyes and ears tell the cortex</text>')
svg.append(f'<line x1="200" y1="328" x2="200" y2="304" stroke="{MAG}" stroke-width="2" marker-end="url(#a-mag)"/>')
svg.append(f'<rect x="820" y="330" width="320" height="60" rx="8" fill="{PANEL}" stroke="{YEL}" stroke-dasharray="4 3"/>')
svg.append(f'<text x="980" y="356" font-size="14" fill="{INK}" text-anchor="middle" {SANS}>any body: hexarotor · quadruped · wheeled arm</text>')
svg.append(f'<text x="980" y="376" font-size="12" fill="{FAINT}" text-anchor="middle" {MONO}>same reflex layer, new adapter</text>')
svg.append(f'<line x1="980" y1="304" x2="980" y2="328" stroke="{YEL}" stroke-width="2" marker-end="url(#a-yel)"/>')
svg.append(f'<text x="40" y="36" font-size="15" fill="{FAINT}" {MONO}>slow · deliberate</text>')
svg.append(f'<text x="1140" y="36" font-size="15" fill="{FAINT}" text-anchor="end" {MONO}>fast · reflexive</text>')
svg.append(f'<line x1="190" y1="31" x2="975" y2="31" stroke="{LINE}" stroke-width="1.5" marker-end="url(#a-soft)"/>')
svg.append(f'<text x="590" y="425" font-size="13" fill="{FAINT}" text-anchor="middle" {SANS}>SPINE sits between the plan and the actuators: it never needs the language model to close the loop.</text>')
svg.append("</svg>")
(OUT / "three_loops.svg").write_text("\n".join(svg))

# ---------------- Figure 2: latency ladder ----------------
W, H = 1180, 420
svg = head(W, H, "Reaction latencies of animal reflexes and of robot control loops on one logarithmic time axis")
x0, x1 = 90, 1120
lo, hi = math.log10(1), math.log10(3000)
def X(ms): return x0 + (math.log10(ms) - lo) / (hi - lo) * (x1 - x0)
axis_y = 230
svg.append(f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{SOFT}" stroke-width="1.5"/>')
for ms, lab in ((1, "1 ms"), (10, "10 ms"), (100, "100 ms"), (1000, "1 s")):
    svg.append(f'<line x1="{X(ms):.1f}" y1="{axis_y - 6}" x2="{X(ms):.1f}" y2="{axis_y + 6}" stroke="{SOFT}"/>')
    svg.append(f'<text x="{X(ms):.1f}" y="{axis_y + 24}" font-size="13" fill="{SOFT}" text-anchor="middle" {MONO}>{lab}</text>')
    for k in range(2, 10):
        if ms * k < 3000:
            svg.append(f'<line x1="{X(ms * k):.1f}" y1="{axis_y - 3}" x2="{X(ms * k):.1f}" y2="{axis_y + 3}" stroke="{LINE}"/>')
svg.append(f'<text x="{x1}" y="{axis_y + 44}" font-size="13" fill="{FAINT}" text-anchor="end" {MONO}>time from stimulus to response (log scale)</text>')
# biology (above)
bio = [("vestibulo-ocular reflex", 7, 15, CYAN), ("fish C-start (Mauthner cell)", 5, 15, CYAN), ("knee-jerk stretch reflex", 20, 40, CYAN),
       ("cockroach wind escape", 30, 60, CYAN), ("long-loop (transcortical) reflex", 50, 100, GRN), ("voluntary reaction to a visual cue", 180, 300, MAG)]
svg.append(f'<text x="{x0}" y="46" font-size="17" font-weight="700" fill="{INK}" {DISP}>ANIMALS</text>')
for i, (lab, a, b, col) in enumerate(bio):
    y = 66 + i * 24
    svg.append(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b) - X(a):.1f}" height="12" rx="3" fill="{col}" opacity="0.85"/>')
    svg.append(f'<text x="{X(b) + 8:.1f}" y="{y + 11}" font-size="13" fill="{SOFT}" {SANS}>{lab}</text>')
# robots (below)
rob = [("MPC / PID update", 1, 8, YEL), ("SPINE reflex layer (target)", 2, 10, CYAN), ("VLA inference (π0.5, GR00T N1 System 2)", 80, 300, MAG),
       ("one 20 Hz action chunk of 50 steps", 2500, 2500, MAG)]
svg.append(f'<text x="{x0}" y="286" font-size="17" font-weight="700" fill="{INK}" {DISP}>ROBOTS</text>')
for i, (lab, a, b, col) in enumerate(rob):
    y = 302 + i * 24
    w = max(X(b) - X(a), 4)
    svg.append(f'<rect x="{X(a):.1f}" y="{y}" width="{w:.1f}" height="12" rx="3" fill="{col}" opacity="0.85"/>')
    anchor_x = X(b) + 8 if X(b) + 150 < x1 else X(a) - 8
    anchor = "start" if X(b) + 150 < x1 else "end"
    svg.append(f'<text x="{anchor_x:.1f}" y="{y + 11}" font-size="13" fill="{SOFT}" text-anchor="{anchor}" {SANS}>{lab}</text>')
svg.append(f'<text x="590" y="404" font-size="13" fill="{FAINT}" text-anchor="middle" {SANS}>A VLA answers in the time a human needs for a conscious decision; a spinal reflex has already acted ten times over. Order-of-magnitude figures from the literature.</text>')
svg.append("</svg>")
(OUT / "latency_ladder.svg").write_text("\n".join(svg))

# ---------------- Figure 3: bullet time ----------------
W, H = 1180, 420
svg = head(W, H, "Bullet time: the reflex layer slows the plan's phase while it corrects a disturbance")
px, py, pw, ph = 80, 60, 640, 280
svg.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{PANEL}" stroke="{LINE}" rx="6"/>')
# disturbance band
svg.append(f'<rect x="{px + 230}" y="{py}" width="150" height="{ph}" fill="{ORG}" opacity="0.12"/>')
svg.append(f'<text x="{px + 305}" y="{py + 20}" font-size="12" fill="{ORG}" text-anchor="middle" {MONO}>gust / push</text>')
# phase lines: nominal (dashed) vs with bullet time
def pt(t, phase): return (px + t * pw, py + ph - phase * (ph - 30) - 10)
nominal = " ".join(f"{pt(t, t)[0]:.1f},{pt(t, t)[1]:.1f}" for t in [i / 40 for i in range(41)])
svg.append(f'<polyline points="{nominal}" fill="none" stroke="{MAG}" stroke-width="2" stroke-dasharray="6 5" opacity="0.8"/>')
pts = []
phase = 0.0
for i in range(0, 81):
    t = i / 80
    speed = 1.0
    if 0.36 <= t < 0.46: speed = 0.08
    elif 0.46 <= t < 0.60: speed = 0.55
    elif t >= 0.60: speed = 1.35 if phase < t - 0.02 else 1.0
    phase = min(1.0, phase + speed / 80)
    pts.append(pt(t, phase))
svg.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{CYAN}" stroke-width="3" filter="url(#glow)"/>')
svg.append(f'<text x="{px + pw - 8}" y="{py + ph + 18}" font-size="12" fill="{FAINT}" text-anchor="end" {MONO}>wall-clock time →</text>')
svg.append(f'<text x="{px - 12}" y="{py + 20}" font-size="12" fill="{FAINT}" text-anchor="end" transform="rotate(-90 {px - 12} {py + 20})" {MONO}></text>')
svg.append(f'<text x="{px - 18}" y="{py + ph / 2}" font-size="13" fill="{SOFT}" text-anchor="middle" transform="rotate(-90 {px - 18} {py + ph / 2})" {MONO}>progress through the VLA chunk (phase)</text>')
svg.append(f'<text x="{px + 150}" y="{py + 60}" font-size="13" fill="{MAG}" {SANS}>nominal: the chunk plays at 20 Hz regardless</text>')
svg.append(f'<text x="{px + 395}" y="{py + 232}" font-size="13" fill="{CYAN}" {SANS}>with SPINE: phase slows to a crawl, pose is corrected,</text>')
svg.append(f'<text x="{px + 395}" y="{py + 250}" font-size="13" fill="{CYAN}" {SANS}>then the plan catches up — the world ran slower for it</text>')
# right: three override levels
rx, ry = 770, 60
levels = [(GRN, "level 1 · residual", "small error: add a correction to the chunk;", "the plan keeps its timing"),
          (CYAN, "level 2 · bullet time", "large error: scale the plan's phase velocity down,", "correct, then catch up"),
          (MAG, "level 3 · takeover", "unrecoverable: run the safety behaviour, send the", "VLA a 'plan broken' token, ask for a new chunk")]
for i, (col, title, l1, l2) in enumerate(levels):
    y = ry + i * 92
    svg.append(f'<rect x="{rx}" y="{y}" width="370" height="78" rx="8" fill="{PANEL}" stroke="{LINE}"/>')
    svg.append(f'<rect x="{rx}" y="{y}" width="4" height="78" rx="2" fill="{col}" filter="url(#glow)"/>')
    svg.append(f'<text x="{rx + 18}" y="{y + 28}" font-size="18" font-weight="700" fill="{col}" {DISP}>{title}</text>')
    svg.append(f'<text x="{rx + 18}" y="{y + 50}" font-size="13" fill="{SOFT}" {SANS}>{l1}</text>')
    svg.append(f'<text x="{rx + 18}" y="{y + 67}" font-size="13" fill="{SOFT}" {SANS}>{l2}</text>')
svg.append(f'<text x="590" y="404" font-size="13" fill="{FAINT}" text-anchor="middle" {SANS}>Phase control is how dynamic movement primitives handle perturbations; here the reflex layer owns the phase of the VLA\'s chunk.</text>')
svg.append("</svg>")
(OUT / "bullet_time.svg").write_text("\n".join(svg))
print("svg written")
