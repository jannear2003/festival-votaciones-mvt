(() => {
  "use strict";
  const stage = document.querySelector("#stage");
  const trailToggle = document.querySelector("#trailToggle");
  const burstToggle = document.querySelector("#burstToggle");
  const intensity = document.querySelector("#intensity");
  const intensityValue = document.querySelector("#intensityValue");
  const colorInput = document.querySelector("#particleColor");
  const clearButton = document.querySelector("#clearButton");
  const demoButton = document.querySelector("#demoButton");
  const statusText = document.querySelector("#statusText");
  const statusDot = document.querySelector("#statusDot");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const symbols = ["♪", "♫", "♬"];
  const limits = { trail: 65, burst: 90, total: 120 };
  const distances = [34, 23, 14];
  const labels = ["Suave", "Media", "Intensa"];
  const particles = new Map();
  let lastPoint = null;
  let trailCount = 0;
  let burstCount = 0;
  let liveCount = 0;

  function updateStatus() {
    const active = [];
    if (trailToggle.checked) active.push("estela");
    if (burstToggle.checked) active.push("explosiones");
    statusText.textContent = active.length ? `${active[0]}${active[1] ? " y " + active[1] : ""} activas` : "Efectos pausados";
    statusDot.classList.toggle("is-off", active.length === 0);
  }

  function removeParticle(note) {
    const particle = particles.get(note);
    if (!particle) return;
    window.clearTimeout(particle.timer);
    note.remove();
    particles.delete(note);
    liveCount--;
    if (particle.kind === "burst") burstCount--; else trailCount--;
  }

  function addParticle(x, y, options = {}) {
    if (liveCount >= limits.total) return;
    const kind = options.kind || "trail";
    const kindCount = kind === "burst" ? burstCount : trailCount;
    if (kindCount >= limits[kind]) return;
    const rect = stage.getBoundingClientRect();
    const note = document.createElement("span");
    const angle = options.angle ?? Math.random() * Math.PI * 2;
    const distance = options.distance ?? (24 + Math.random() * 36);
    const duration = reducedMotion.matches ? 30 : (options.duration ?? 800 + Math.random() * 550);
    note.className = "particle";
    note.setAttribute("aria-hidden", "true");
    note.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    note.style.setProperty("--x", `${x - rect.left}px`);
    note.style.setProperty("--y", `${y - rect.top}px`);
    note.style.setProperty("--dx", `${Math.cos(angle) * distance}px`);
    note.style.setProperty("--dy", `${Math.sin(angle) * distance - (kind === "trail" ? 18 : 0)}px`);
    note.style.setProperty("--rotate", `${Math.random() * 36 - 18}deg`);
    note.style.setProperty("--spin", `${Math.random() * 70 - 35}deg`);
    note.style.setProperty("--duration", `${duration}ms`);
    note.style.setProperty("--particle-color", colorInput.value);
    note.style.fontSize = `${16 + Math.random() * (kind === "burst" ? 15 : 10)}px`;
    stage.append(note);
    liveCount++;
    if (kind === "burst") burstCount++; else trailCount++;
    const timer = window.setTimeout(() => removeParticle(note), duration + 60);
    particles.set(note, { timer, kind });
  }

  function burstAt(x, y) {
    if (!burstToggle.checked) {
      burstToggle.checked = true;
      updateStatus();
    }
    const count = reducedMotion.matches ? 1 : 10;
    for (let i = 0; i < count; i++) {
      addParticle(x, y, {
        kind: "burst",
        angle: (Math.PI * 2 * i) / count + Math.random() * .25,
        distance: 45 + Math.random() * 66,
        duration: 700 + Math.random() * 500
      });
    }
  }

  function onPointerMove(event) {
    if (!trailToggle.checked || event.pointerType === "touch") return;
    const current = { x: event.clientX, y: event.clientY };
    if (lastPoint) {
      const dx = current.x - lastPoint.x;
      const dy = current.y - lastPoint.y;
      if (Math.hypot(dx, dy) < distances[Number(intensity.value) - 1]) return;
    }
    lastPoint = current;
    addParticle(current.x, current.y, { kind: "trail" });
  }

  function onPointerDown(event) {
    if (!burstToggle.checked || event.button > 0) return;
    burstAt(event.clientX, event.clientY);
  }

  function clearParticles() {
    for (const note of particles.keys()) removeParticle(note);
    lastPoint = null;
  }

  function showDemo() {
    stage.scrollIntoView({ behavior: reducedMotion.matches ? "auto" : "smooth", block: "center" });
    window.requestAnimationFrame(() => {
      const rect = stage.getBoundingClientRect();
      burstAt(rect.left + rect.width / 2, rect.top + rect.height / 2);
      stage.focus({ preventScroll: true });
    });
  }

  trailToggle.addEventListener("change", () => { lastPoint = null; updateStatus(); });
  burstToggle.addEventListener("change", updateStatus);
  stage.addEventListener("pointermove", onPointerMove, { passive: true });
  stage.addEventListener("pointerdown", onPointerDown, { passive: true });
  stage.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      const rect = stage.getBoundingClientRect();
      burstAt(rect.left + rect.width / 2, rect.top + rect.height / 2);
    }
  });
  intensity.addEventListener("input", () => { intensityValue.textContent = labels[Number(intensity.value) - 1]; });
  clearButton.addEventListener("click", clearParticles);
  demoButton.addEventListener("click", showDemo);
  updateStatus();
})();
