(function () {
  const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- Parts: collapsed by default; a link into a part opens it ----------------------------------
  const parts = [...document.querySelectorAll("details.part-block")];
  function openPartOf(target) {
    const part = target.closest("details.part-block");
    if (part && !part.open) part.open = true;
  }
  document.querySelectorAll("a[href^='#']").forEach((link) => {
    link.addEventListener("click", () => {
      const target = document.getElementById(link.getAttribute("href").slice(1));
      if (target) openPartOf(target);
    });
  });
  function revealHash() {
    const target = location.hash && document.getElementById(location.hash.slice(1));
    if (!target || target.tagName === "SUMMARY") return;
    openPartOf(target);
    target.scrollIntoView({ behavior: "instant" });
  }
  // ?open=all expands every part (for printing or sharing a full view)
  if (new URLSearchParams(location.search).get("open") === "all") parts.forEach((p) => { p.open = true; });
  revealHash();
  window.addEventListener("hashchange", () => {
    const target = location.hash && document.getElementById(location.hash.slice(1));
    if (target && target.tagName !== "SUMMARY") openPartOf(target);
  });

  // ---- Nav highlight: the section's own link, else its part's ------------------------------------
  const links = [...document.querySelectorAll(".nav a[href^='#']")];
  const linkFor = new Map();
  document.querySelectorAll("main section, summary.part").forEach((el) => {
    const own = links.find((link) => link.getAttribute("href") === "#" + el.id);
    const summary = el.closest("details.part-block")?.querySelector("summary.part");
    const link = own || links.find((l) => summary && l.getAttribute("href") === "#" + summary.id);
    if (link) linkFor.set(el, link);
  });
  if ("IntersectionObserver" in window && linkFor.size) {
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const current = linkFor.get(entry.target);
        links.forEach((link) => { if (link === current) link.setAttribute("aria-current", "true"); else link.removeAttribute("aria-current"); });
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    linkFor.forEach((_, el) => spy.observe(el));
  }

  // ---- Cards slide in as they appear -------------------------------------------------------------
  const cards = [...document.querySelectorAll(".card")];
  if (reduceMotion || !("IntersectionObserver" in window)) {
    cards.forEach((c) => c.classList.add("in"));
  } else {
    const reveal = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (!entry.isIntersecting) return;
        setTimeout(() => entry.target.classList.add("in"), (i % 4) * 90);
        reveal.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    cards.forEach((c) => reveal.observe(c));
  }

  // ---- Clips under the title: still frames with controls when the system asks for less motion -------
  if (reduceMotion) {
    document.querySelectorAll(".reel video").forEach((video) => { video.removeAttribute("autoplay"); video.pause(); video.controls = true; });
  }

  // ---- Reaction test: you vs a spinal reflex vs a VLA re-plan ------------------------------------
  const lab = document.getElementById("reaction-lab");
  if (lab) {
    const pad = lab.querySelector("[data-rt-pad]");
    const msg = lab.querySelector("[data-rt-msg]");
    const start = lab.querySelector("[data-rt-start]");
    const bar = (k) => lab.querySelector(`[data-rt-bar="${k}"]`);
    const val = (k) => lab.querySelector(`[data-rt-val="${k}"]`);
    const SPINE_MS = 30, VLA_MS = 300;
    let state = "idle", timer = null, t0 = 0;
    function setBars(you) {
      const max = Math.max(600, you || 0, VLA_MS * 1.2);
      bar("you").style.width = you ? `${(you / max) * 100}%` : "0";
      bar("spine").style.width = `${(SPINE_MS / max) * 100}%`;
      bar("vla").style.width = `${(VLA_MS / max) * 100}%`;
    }
    setBars(0);
    function arm() {
      clearTimeout(timer);
      state = "armed";
      pad.className = "pad armed";
      pad.textContent = "wait for yellow…";
      msg.textContent = "armed";
      timer = setTimeout(() => {
        state = "go";
        pad.className = "pad go";
        pad.textContent = "NOW";
        t0 = performance.now();
      }, 1200 + Math.random() * 2600);
    }
    function hit() {
      if (state === "armed") {
        clearTimeout(timer);
        state = "idle";
        pad.className = "pad early";
        pad.textContent = "too early — that was a guess, not a reflex";
        msg.textContent = "false start";
        return;
      }
      if (state !== "go") return;
      const you = Math.round(performance.now() - t0);
      state = "idle";
      pad.className = "pad";
      pad.textContent = `${you} ms`;
      val("you").textContent = `${you} ms`;
      setBars(you);
      const ratio = (you / SPINE_MS).toFixed(1);
      msg.innerHTML = you < VLA_MS
        ? `<b>${you} ms</b>: faster than a VLA re-plan, about ${ratio}× slower than a spinal reflex.`
        : `<b>${you} ms</b>: a VLA would have replanned by now; a spinal reflex acted ${ratio}× sooner.`;
    }
    start.addEventListener("click", arm);
    pad.addEventListener("pointerdown", hit);
    pad.addEventListener("keydown", (e) => { if (e.key === " " || e.key === "Enter") { e.preventDefault(); hit(); } });
  }

  // ---- Bullet-time simulator ---------------------------------------------------------------------
  const sim = document.querySelector("[data-sim]");
  if (sim && sim.getContext) {
    const ctx = sim.getContext("2d");
    const W = sim.width, H = sim.height;
    const readout = document.querySelector("[data-sim-readout]");
    const modeButtons = [...document.querySelectorAll("[data-mode]")];
    let mode = "none";
    modeButtons.forEach((b) => b.addEventListener("click", () => {
      mode = b.dataset.mode;
      modeButtons.forEach((o) => o.setAttribute("aria-pressed", String(o === b)));
    }));
    const X0 = 60, X1 = W - 60, YC = H * 0.52, AMP = 70, PERIOD = 8; // seconds per pass
    const DT = 1 / 120;                                               // fixed physics step, independent of the frame rate
    const planPoint = (s) => ({ x: X0 + s * (X1 - X0), y: YC + AMP * Math.sin(s * Math.PI * 3) });
    let phase = 0, nominal = 0, clock = 1;
    const robot = { x: X0, y: YC, vx: 0, vy: 0 };
    let gust = 0, gustDir = 1, trail = [], target = planPoint(0), err = 0;
    document.querySelector("[data-gust]").addEventListener("click", () => { gust = 0.25; gustDir = Math.random() < 0.5 ? -1 : 1; });
    function restart() { // a new pass: the robot starts on the plan again instead of flying back across
      nominal = phase; target = planPoint(phase);
      robot.x = target.x; robot.y = target.y; robot.vx = 0; robot.vy = 0; trail = [];
    }
    function physics() {
      target = planPoint(phase);
      const ahead = planPoint(Math.min(1, phase + 0.002));
      const tvx = (ahead.x - target.x) / (0.002 * PERIOD) * clock, tvy = (ahead.y - target.y) / (0.002 * PERIOD) * clock;
      const ex = target.x - robot.x, ey = target.y - robot.y;
      err = Math.hypot(ex, ey);
      // the plan's clock
      nominal = (nominal + DT / PERIOD) % 1;
      if (mode === "bullet") {
        const slow = 1 / (1 + Math.pow(err / 28, 2));           // large error: the plan waits
        const behind = ((nominal - phase + 1.5) % 1) - 0.5;      // catch up once the error is small
        clock = Math.max(0.03, Math.min(2.2, slow * (1 + Math.max(0, behind) * 10)));
      } else {
        clock = 1;
      }
      // robot: a PD tracker with limited authority
      const kp = mode === "none" ? 18 : 45, kd = mode === "none" ? 6 : 11;
      let ax = kp * ex + kd * (tvx - robot.vx), ay = kp * ey + kd * (tvy - robot.vy);
      const amax = mode === "none" ? 900 : 1600;
      const a = Math.hypot(ax, ay); if (a > amax) { ax *= amax / a; ay *= amax / a; }
      if (gust > 0) { ay += gustDir * 3600; gust -= DT; }
      robot.vx += ax * DT; robot.vy += ay * DT;
      robot.x += robot.vx * DT; robot.y += robot.vy * DT;
      trail.push({ x: robot.x, y: robot.y }); if (trail.length > 180) trail.shift();
      const next = (phase + (DT / PERIOD) * clock) % 1;
      const wrapped = next < phase; phase = next;
      if (wrapped) restart();
    }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      ctx.strokeStyle = "rgba(255,47,209,0.45)"; ctx.setLineDash([6, 6]); ctx.lineWidth = 2; ctx.beginPath();
      for (let i = 0; i <= 200; i++) { const p = planPoint(i / 200); if (i) ctx.lineTo(p.x, p.y); else ctx.moveTo(p.x, p.y); }
      ctx.stroke(); ctx.setLineDash([]);
      ctx.strokeStyle = "rgba(25,230,255,0.35)"; ctx.lineWidth = 3; ctx.beginPath();
      trail.forEach((p, i) => { if (i) ctx.lineTo(p.x, p.y); else ctx.moveTo(p.x, p.y); }); ctx.stroke();
      ctx.strokeStyle = "rgba(255,227,77,0.5)"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(target.x, target.y); ctx.lineTo(robot.x, robot.y); ctx.stroke();
      ctx.shadowBlur = 16; ctx.shadowColor = "#ff2fd1"; ctx.fillStyle = "#ff2fd1"; ctx.beginPath(); ctx.arc(target.x, target.y, 7, 0, Math.PI * 2); ctx.fill();
      ctx.shadowColor = "#19e6ff"; ctx.fillStyle = "#19e6ff"; ctx.beginPath(); ctx.arc(robot.x, robot.y, 10, 0, Math.PI * 2); ctx.fill();
      ctx.shadowBlur = 0;
      if (gust > 0) {
        ctx.strokeStyle = "#ff8a3d"; ctx.lineWidth = 3; ctx.shadowBlur = 12; ctx.shadowColor = "#ff8a3d";
        for (let k = -1; k <= 1; k++) { ctx.beginPath(); ctx.moveTo(robot.x + k * 18, robot.y - gustDir * 70); ctx.lineTo(robot.x + k * 18, robot.y - gustDir * 24); ctx.stroke(); }
        ctx.shadowBlur = 0;
      }
      // plan clock bar
      ctx.fillStyle = "rgba(255,227,77,0.15)"; ctx.fillRect(X0, 18, X1 - X0, 8);
      ctx.fillStyle = "#ffe34d"; ctx.fillRect(X0, 18, (X1 - X0) * phase, 8);
      ctx.fillStyle = "#6b7a8e"; ctx.font = "12px 'IBM Plex Mono', monospace";
      ctx.fillText(`plan clock ${Math.round(clock * 100)} %`, X0, 44);
      ctx.fillText(`mode: ${mode}`, X1 - 110, 44);
      const note = mode === "bullet" && clock < 0.6 ? " · <b>bullet time</b>: the plan waits while the robot recovers"
        : mode === "bullet" && clock > 1.2 ? " · catching up with the plan's clock"
        : mode === "none" && err > 30 ? " · the plan runs on without the robot"
        : mode === "residual" && err > 30 ? " · stronger correction, same clock" : "";
      sim.__state = { mode, clock, err };
      if (readout) readout.innerHTML = `mode <b>${mode}</b> · error <b>${Math.round(err)} px</b> · plan clock <b>${Math.round(clock * 100)} %</b>${note}`;
    }
    let last = performance.now(), acc = 0;
    function frame(now) {
      acc += Math.min(0.1, (now - last) / 1000); last = now;   // a throttled tab runs in slow motion instead of skipping
      while (acc >= DT) { physics(); acc -= DT; }
      draw();
      requestAnimationFrame(frame);
    }
    sim.__advance = (seconds) => { for (let t = 0; t < seconds; t += DT) physics(); draw(); }; // deterministic hook for tests
    if (!reduceMotion) requestAnimationFrame(frame);
    else { ctx.fillStyle = "#6b7a8e"; ctx.font = "14px 'IBM Plex Mono', monospace"; ctx.fillText("animation disabled by the system's reduced-motion setting", 20, 40); }
  }
})();
