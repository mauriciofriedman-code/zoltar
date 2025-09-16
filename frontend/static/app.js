// ==============================
// CONFIG
// ==============================

const baseUrl = window.location.hostname.includes("localhost")
  ? "http://127.0.0.1:8000"
  : window.location.origin;

const zoltarImg = document.querySelector("#zoltarImg");
const soundCoin = document.querySelector("#soundCoin");
const soundReveal = document.querySelector("#soundReveal");
const soundThinking = document.querySelector("#soundThinking");

const questionInput = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
const conversation = document.getElementById("conversation");

// ==============================
// ZOLTAR ANIMATION FRAMES
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

// Preload Zoltar frames
frames.forEach(src => {
  const img = new Image();
  img.src = src;
});

let animInterval = null;
let frameIndex = 0;

function startAnimation() {
  stopAnimation();
  frameIndex = 0;
  zoltarImg.parentElement.classList.add("thinking");
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
  zoltarImg.parentElement.classList.remove("thinking");
  soundThinking.pause();
  soundThinking.currentTime = 0;
  if (success) {
    soundReveal.currentTime = 0;
    soundReveal.play().catch(() => {});
  }
}

// ==============================
// TEXT BUBBLE CREATION
// ==============================

function addBubble(text, isUser = false) {
  const bubble = document.createElement("div");
  bubble.className = "bubble" + (isUser ? " user" : "");
  bubble.textContent = text;
  conversation.appendChild(bubble);
  conversation.scrollTop = conversation.scrollHeight;
}

async function typeBubble(text) {
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  conversation.appendChild(bubble);
  conversation.scrollTop = conversation.scrollHeight;

  for (let i = 0; i < text.length; i++) {
    bubble.textContent += text[i];
    await new Promise(res => setTimeout(res, 20));
  }

  conversation.scrollTop = conversation.scrollHeight;
}

// ==============================
// COIN ANIMATION LOGIC
// ==============================

const coinBtn = document.getElementById("coinBtn");
const slot = document.getElementById("slot");
let hasCoin = false;

coinBtn.addEventListener("click", () => {
  const coinClone = document.createElement("img");
  coinClone.src = "/static/img/coin.png";
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
  questionInput.disabled = false;
  askBtn.disabled = false;

  soundCoin.currentTime = 0;
  soundCoin.play().catch(() => {});
});

// ==============================
// ASK ZOLTAR
// ==============================

askBtn.addEventListener("click", async () => {
  const msg = questionInput.value.trim();
  if (!msg || !hasCoin) return;

  const mode = document.querySelector("input[name='mode']:checked").value;
  const endpoint = mode === "rag" ? "/api/teacher" : "/api/generate";

  // Reset state
  questionInput.value = "";
  questionInput.disabled = true;
  askBtn.disabled = true;

  // Show user question
  addBubble(msg, true);

  // Show thinking text
  addBubble("Zoltar está pensando...");

  startAnimation();

  try {
    const res = await fetch(`${baseUrl}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: msg }),
    });

    const data = await res.json();
    stopAnimation(res.ok);

    // Remove "thinking..." bubble
    const lastBubble = conversation.querySelector(".bubble:last-child");
    if (lastBubble) lastBubble.remove();

    await typeBubble(data.text || "⚠️ Respuesta inesperada");
  } catch (err) {
    stopAnimation(false);

    const lastBubble = conversation.querySelector(".bubble:last-child");
    if (lastBubble) lastBubble.remove();

    addBubble("❌ No se pudo conectar con el oráculo.");
    console.error(err);
  }
});




