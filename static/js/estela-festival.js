(() => {
  "use strict";

  // Revelado editorial al entrar en pantalla, sin bloquear contenido ni accesibilidad.
  const revealMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (!revealMotion.matches && "IntersectionObserver" in window) {
    const revealTargets = document.querySelectorAll(
      ".container > section:not(.hero):not(.form-card), .container > article:not(.form-card), .festival-aside, .voting-entry, .admin-item, .result-row, .stats article, .login"
    );
    const siblingOrder = new Map();
    revealTargets.forEach(element => {
      const parent = element.parentElement;
      const order = siblingOrder.get(parent) || 0;
      siblingOrder.set(parent, order + 1);
      element.classList.add("scroll-reveal");
      element.style.setProperty("--reveal-order", String(Math.min(order, 4)));
    });
    if (revealTargets.length) {
      document.documentElement.classList.add("scroll-reveal-ready");
      const revealObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        });
      }, { threshold: 0.12, rootMargin: "0px 0px -36px 0px" });
      revealTargets.forEach(element => revealObserver.observe(element));
    }
  }

  const enabledInput = document.querySelector("#festivalTrailEnabled");
  const intensityInput = document.querySelector("#festivalTrailIntensity");
  const intensityOutput = document.querySelector("#festivalTrailValue");
  const settings = document.querySelector(".trail-settings");
  if (!enabledInput || !intensityInput || !settings) return;

  const storageKey = "festival-estela-preferencias";
  const labels = ["Suave", "Media", "Intensa"];
  const gaps = [48, 30, 16];
  const symbols = ["♪", "♫", "♬"];
  const colors = ["#fbc867", "#ed7608", "#ffccaa", "#c25061"];
  const activeParticles = new Set();
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (reducedMotion.matches) {
  enabledInput.checked = false;
  enabledInput.disabled = true;

  const toggleLabel = enabledInput
    .closest(".trail-settings__toggle")
    ?.querySelector("span");

  if (toggleLabel) {
    toggleLabel.textContent = "Desactivada por accesibilidad";
  }
}
  let lastPoint = null;

  function isInteractiveTarget(target) {
    if (!(target instanceof Element)) return false;
    return Boolean(
      target.closest(
        "a, button, input, textarea, select, option, label, " +
        "form, summary, details, table, [role='button'], " +
        "[contenteditable='true']"
      )
    );
  }
  function isInteractiveTarget(target) {
  return Boolean(
    target.closest(
      "a, button, input, textarea, select, option, label, " +
      "form, summary, details, table, [role='button'], " +
      "[contenteditable='true']"
    )
  );
}

  function readPreferences() {
    try {
      const value = JSON.parse(localStorage.getItem(storageKey) || "{}");
      if (typeof value.enabled === "boolean") enabledInput.checked = value.enabled;
      if (["1", "2", "3"].includes(String(value.intensity))) intensityInput.value = value.intensity;
    } catch (_) { /* Preferencias inválidas: usar los valores iniciales. */ }
  }

  function applyPreferences() {
    const enabled = enabledInput.checked && !reducedMotion.matches;
    document.body.classList.toggle("trail-off", !enabled);
    intensityOutput.value = labels[Number(intensityInput.value) - 1];
    intensityOutput.textContent = intensityOutput.value;
    try {
      localStorage.setItem(storageKey, JSON.stringify({ enabled, intensity: intensityInput.value }));
    } catch (_) { /* El efecto continúa durante esta visita aunque el almacenamiento esté bloqueado. */ }
    if (!enabled) clearParticles();
  }

  function removeParticle(particle) {
    particle.remove();
    activeParticles.delete(particle);
  }

  function clearParticles() {
    for (const particle of activeParticles) removeParticle(particle);
    lastPoint = null;
  }

  function addParticle(x, y) {
    if (!enabledInput.checked || activeParticles.size >= 34) return;
    const particle = document.createElement("span");
    const drift = () => (Math.random() - .5) * (Number(intensityInput.value) * 28 + 22);
    const duration = reducedMotion.matches ? 180 : 620 + Math.random() * 480;
    particle.className = "festival-particle";
    particle.setAttribute("aria-hidden", "true");
    particle.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    particle.style.setProperty("--particle-x", `${x}px`);
    particle.style.setProperty("--particle-y", `${y}px`);
    particle.style.setProperty("--particle-dx", `${drift()}px`);
    particle.style.setProperty("--particle-dy", `${-14 - Math.random() * 30}px`);
    particle.style.setProperty("--particle-rotate", `${Math.random() * 50 - 25}deg`);
    particle.style.setProperty("--particle-duration", `${duration}ms`);
    particle.style.setProperty("--particle-color", colors[Math.floor(Math.random() * colors.length)]);
    particle.style.fontSize = `${13 + Math.random() * (Number(intensityInput.value) * 5)}px`;
    document.body.append(particle);
    activeParticles.add(particle);
    window.setTimeout(() => removeParticle(particle), duration + 80);
  }

  document.addEventListener("pointermove", event => {
    if (event.pointerType === "touch" || !enabledInput.checked) return;
    const current = { x: event.clientX, y: event.clientY };
    const threshold = gaps[Number(intensityInput.value) - 1];
    if (lastPoint && Math.hypot(current.x - lastPoint.x, current.y - lastPoint.y) < threshold) return;
    lastPoint = current;
    addParticle(current.x, current.y);
  }, { passive: true });

  document.addEventListener("pointerdown", event => {
    if (
      event.pointerType === "touch" ||
      !enabledInput.checked ||
      event.button > 0 ||
      settings.contains(event.target) ||
      isInteractiveTarget(event.target)
    ) {
      return;
    }
    addParticle(event.clientX, event.clientY);
    if (Number(intensityInput.value) === 3 && !reducedMotion.matches) {
      for (let i = 0; i < 4; i++) window.setTimeout(() => addParticle(event.clientX, event.clientY), i * 28);
    }
  }, { passive: true });

  enabledInput.addEventListener("change", applyPreferences);
  intensityInput.addEventListener("input", applyPreferences);
  document.addEventListener("pointerdown", event => {
    if (settings.open && !settings.contains(event.target)) settings.open = false;
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") settings.open = false;
  });

  readPreferences();

  if (reducedMotion.matches) {
    enabledInput.checked = false;
    enabledInput.disabled = true;
    const toggleLabel = enabledInput
      .closest(".trail-settings__toggle")
      ?.querySelector("span");
    if (toggleLabel) {
      toggleLabel.textContent = "Desactivada por accesibilidad";
    }
  }

  applyPreferences();
})();
