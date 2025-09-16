// =============================
// Configuración
// =============================

// URL del backend FastAPI
// Detecta si corre en local o en Render
const baseUrl = window.location.hostname.includes("localhost")
  ? "http://127.0.0.1:8000"
  : window.location.origin;

// Logs de los dos paneles
const logA = document.getElementById("logA");
const logB = document.getElementById("logB");

// Formularios
const formA = document.getElementById("formA");
const formB = document.getElementById("formB");

// =============================
// Utilidad para mostrar mensajes
// =============================
function appendMessage(log, text, who = "ai") {
  const div = document.createElement("div");
  div.className = who === "me" ? "msg me" : "msg ai";
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight; // scroll al final
}

// =============================
// Panel A: Baseline vs Engineered
// =============================
if (formA) {
  formA.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = document.getElementById("msgA").value.trim();
    if (!msg) return;

    appendMessage(logA, msg, "me");
    document.getElementById("msgA").value = "";

    const mode = document.querySelector("input[name='modeA']:checked").value;

    try {
      startAnimation();

      const res = await fetch(`${baseUrl}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: msg, mode }), // unificado: usa `text`
      });

      stopAnimation(res.ok);

      if (!res.ok) {
        let errMsg = `⚠️ Error backend (${res.status})`;
        try {
          const errData = await res.json();
          if (errData.detail) errMsg += `: ${errData.detail}`;
        } catch {
          const errText = await res.text();
          if (errText) errMsg += `: ${errText}`;
        }
        appendMessage(logA, errMsg, "ai");
        console.error("Respuesta del servidor:", res);
        return;
      }

      const data = await res.json();
      appendMessage(logA, data.text || "⚠️ Respuesta inesperada", "ai");
    } catch (err) {
      stopAnimation(false);
      appendMessage(logA, "❌ No se pudo conectar con backend", "ai");
      console.error(err);
    }
  });
}

// =============================
// Panel B: Teacher con RAG
// =============================
if (formB) {
  formB.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = document.getElementById("msgB").value.trim();
    if (!msg) return;

    appendMessage(logB, msg, "me");
    document.getElementById("msgB").value = "";

    try {
      startAnimation();

      const res = await fetch(`${baseUrl}/api/teacher`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: msg }), // unificado: usa `text`
      });

      stopAnimation(res.ok);

      if (!res.ok) {
        let errMsg = `⚠️ Error backend (${res.status})`;
        try {
          const errData = await res.json();
          if (errData.detail) errMsg += `: ${errData.detail}`;
        } catch {
          const errText = await res.text();
          if (errText) errMsg += `: ${errText}`;
        }
        appendMessage(logB, errMsg, "ai");
        console.error("Respuesta del servidor:", res);
        return;
      }

      const data = await res.json();
      appendMessage(logB, data.text || "⚠️ Respuesta inesperada", "ai");
    } catch (err) {
      stopAnimation(false);
      appendMessage(logB, "❌ No se pudo conectar con backend", "ai");
      console.error(err);
    }
  });
}

// =============================
// Chequeo de conexión inicial
// =============================
async function checkBackend() {
  const statusEl = document.getElementById("backendStatus");
  try {
    const res = await fetch(`${baseUrl}/health`);
    if (res.ok) {
      statusEl.textContent = "✅ Conectado";
      statusEl.style.color = "lime";
    } else {
      statusEl.textContent = "⚠️ Backend no responde";
      statusEl.style.color = "orange";
    }
  } catch {
    statusEl.textContent = "❌ No conectado";
    statusEl.style.color = "red";
  }
}
checkBackend();

// =============================
// Animación + Sonidos de Zoltar
// =============================
let animInterval;
const zoltarImg = document.querySelector("#zoltarImg");

const soundCoin = document.querySelector("#soundCoin");
const soundReveal = document.querySelector("#soundReveal");
const soundThinking = document.querySelector("#soundThinking");

const frames = [
  "/img/Zoltar_1.png",
  "/img/Zoltar_2.png",
  "/img/Zoltar_3.png",
  "/img/Zoltar_4.png",
  "/img/Zoltar_5.png",
  "/img/Zoltar_4.png",
  "/img/Zoltar_3.png",
  "/img/Zoltar_2.png",
];
let frameIndex = 0;

function startAnimation() {
  stopAnimation();
  frameIndex = 0;
  soundThinking.currentTime = 0;
  soundThinking.play().catch(() => {});

  animInterval = setInterval(() => {
    zoltarImg.src = frames[frameIndex];
    frameIndex = (frameIndex + 1) % frames.length;
  }, 150);
}

function stopAnimation(success = true) {
  if (animInterval) clearInterval(animInterval);
  zoltarImg.src = "/img/Zoltar_1.png";
  soundThinking.pause();
  soundThinking.currentTime = 0;

  if (success) {
    soundReveal.currentTime = 0;
    soundReveal.play().catch(() => {});
  }
}

// =============================
// Animación de la moneda
// =============================
const coinBtn = document.getElementById("coinBtn");
const slot = document.getElementById("slot");
let hasCoin = false;

if (coinBtn && slot) {
  coinBtn.addEventListener("click", () => {
    const coinClone = document.createElement("img");
    coinClone.src = "/img/coin.png";
    coinClone.className = "moving-coin";

    const rectCoin = coinBtn.getBoundingClientRect();
    const rectSlot = slot.getBoundingClientRect();

    coinClone.style.left = rectCoin.left + "px";
    coinClone.style.top = rectCoin.top + "px";

    document.body.appendChild(coinClone);
    void coinClone.offsetWidth;

    const dx = rectSlot.left - rectCoin.left;
    const dy = rectSlot.top - rectCoin.top;

    coinClone.style.transform = `translate(${dx}px, ${dy}px) scale(0.6) rotate(360deg)`;
    coinClone.style.opacity = "0";

    setTimeout(() => coinClone.remove(), 800);

    hasCoin = true;
    document.getElementById("question").disabled = false;
    document.getElementById("askBtn").disabled = false;
    soundCoin.currentTime = 0;
    soundCoin.play().catch(() => {});
  });
}




