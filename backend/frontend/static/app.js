// ==============================
// CONFIG
// ==============================

const baseUrl = window.location.hostname.includes("localhost")
  ? "http://127.0.0.1:8000"
  : window.location.origin;

const zoltarImg = document.querySelector("#zoltarImg");
const zoltarBox = document.querySelector("#zoltarBox");
const soundCoin = document.getElementById("soundCoin");
const soundReveal = document.getElementById("soundReveal");
const soundThinking = document.getElementById("soundThinking");

const questionInput = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const conversation = document.getElementById("conversation");
const coinBtn = document.getElementById("coinBtn");
const slot = document.getElementById("slot");

let hasCoin = false;

// ==============================
// ANIMATION FRAMES
// ==============================

const frames = [
  "/static/img/Zoltar_1.png",
  "/static/img/Zoltar_2.png",
  "/static/img/Zoltar_3.png",
  "/static/img/Zoltar_4.png",
  "/static/img/Zoltar_5.png",
  "/static/img/Zoltar_4.png",
  "/static/img/Zoltar_3.png",
  "/static/img/Zoltar_2.png",
];

const preloaded = [];
frames.forEach(src => {
  const img = new Image();
  img.src = src;
  preloaded.push(img);
});

let animInterval = null;
let frameIndex = 0;

function startAnimation() {
  stopAnimation();
  frameIndex = 0;
  zoltarBox.classList.add("thinking");
  soundThinking.currentTime = 0;
  soundThinking.play().catch(() => {});
  animInterval = setInterval(() => {
    zoltarImg.src = frames[frameIndex];
    frameIndex = (frameIndex + 1) % frames.length;
  }, 150);
}

function stopAnimation(success = true) {
  clearInterval(animInterval);
  zoltarImg.src = "/static/img/Zoltar_1.png";
  zoltarBox.classList.remove("thinking");
  soundThinking.pause();
  soundThinking.currentTime = 0;
  if (success) {
    soundReveal.currentTime = 0;
    soundReveal.play().catch(() => {});
  }
}

// ==============================
// COIN ANIMATION
// ==============================

if (coinBtn && slot) {
  coinBtn.addEventListener("click", () => {
    if (hasCoin) return;

    const coinClone = document.createElement("img");
    coinClone.src = "/static/img/coin.png";
    coinClone.className = "moving-coin";

    const rectCoin = coinBtn.getBoundingClientRect();
    const rectSlot = slot.getBoundingClientRect();

    coinClone.style.position = "fixed";
    coinClone.style.left = `${rectCoin.left}px`;
    coinClone.style.top = `${rectCoin.top}px`;
    coinClone.style.width = `60px`;
    coinClone.style.height = `60px`;
    coinClone.style.pointerEvents = "none";
    coinClone.style.transition = "transform 0.8s ease-in-out, opacity 0.8s ease-in-out";
    coinClone.style.zIndex = "9999";

    document.body.appendChild(coinClone);
    void coinClone.offsetWidth;

    const dx = rectSlot.left - rectCoin.left;
    const dy = rectSlot.top - rectCoin.top;

    coinClone.style.transform = `translate(${dx}px, ${dy}px) scale(0.6) rotate(360deg)`;
    coinClone.style.opacity = "0";

    setTimeout(() => coinClone.remove(), 800);

    hasCoin = true;
    questionInput.disabled = false;
    askBtn.disabled = false;

    zoltarBox.classList.add("thinking");
    soundCoin.currentTime = 0;
    soundCoin.play().catch(() => {});
  });
}

// ==============================
// TEXT TYPING EFFECT
// ==============================

async function typeText(text) {
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  conversation.appendChild(bubble);
  conversation.scrollTop = conversation.scrollHeight;

  for (let i = 0; i < text.length; i++) {
    bubble.textContent += text[i];
    await new Promise(res => setTimeout(res, 20));
    conversation.scrollTop = conversation.scrollHeight;
  }
}

// ==============================
// LLAMADAS A BACKEND
// ==============================

async function callSimpleLLM(msg) {
  const conversation = [{ role: "user", content: msg }];
  const res = await fetch(`${baseUrl}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation }),
  });
  const data = await res.json();
  return data.text;
}

// ==============================
// MAIN ASK HANDLER
// ==============================

askBtn.addEventListener("click", async () => {
  const msg = questionInput.value.trim();
  if (!msg || !hasCoin) return;

  const mode = document.querySelector("input[name='mode']:checked").value;

  questionInput.value = "";
  startAnimation();
  await typeText("Zoltar está pensando...");

  let data = {};

  try {
    if (mode === "rag") {
      const res = await fetch(`${baseUrl}/api/teacher`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: msg }),
      });
      data = await res.json();
    } else {
      const text = await callSimpleLLM(msg);
      data.text = text;
    }

    stopAnimation(true);
    await typeText(data.text || "⚠️ Respuesta inesperada");

    if (mode === "rag" && Array.isArray(data.sources) && data.sources.length > 0) {
      const refs = document.createElement("div");
      refs.className = "refs";
      refs.innerHTML = `
        <strong>📚 Fuentes consultadas:</strong>
        <ul>
          ${data.sources.map(s => `<li>${s}</li>`).join("")}
        </ul>
      `;
      conversation.appendChild(refs);
      conversation.scrollTop = conversation.scrollHeight;
    }

    hasCoin = false;
    questionInput.disabled = true;
    askBtn.disabled = true;

  } catch (err) {
    stopAnimation(false);
    await typeText("❌ No se pudo conectar con backend");
    console.error(err);
  }
});

// ==============================
// (opcional) Precargar voces TTS
// ==============================

window.speechSynthesis.onvoiceschanged = () => {};
