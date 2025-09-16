const baseUrl = window.location.hostname.includes("localhost")
  ? "http://127.0.0.1:8000"
  : window.location.origin;

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
const preloaded = [];
frames.forEach(src => {
  const img = new Image();
  img.src = src;
  preloaded.push(img);
});

let animInterval;
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
  zoltarImg.src = "/img/Zoltar_1.png";
  zoltarImg.parentElement.classList.remove("thinking");
  soundThinking.pause();
  soundThinking.currentTime = 0;
  if (success) {
    soundReveal.currentTime = 0;
    soundReveal.play().catch(() => {});
  }
}

async function typeText(text, outputEl) {
  outputEl.textContent = "";
  for (let i = 0; i < text.length; i++) {
    outputEl.textContent += text[i];
    await new Promise(res => setTimeout(res, 20));
  }
}

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

document.getElementById("askBtn").addEventListener("click", async () => {
  const input = document.getElementById("question");
  const output = document.getElementById("output");
  const mode = document.querySelector("input[name='mode']:checked").value;
  const msg = input.value.trim();
  if (!msg) return;

  input.value = "";
  output.textContent = "Zoltar está pensando...";
  startAnimation();

  const endpoint = mode === "rag" ? "/api/teacher" : "/api/generate";

  try {
    const res = await fetch(`${baseUrl}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: msg, mode }),
    });

    const data = await res.json();
    stopAnimation(res.ok);
    await typeText(data.text || "⚠️ Respuesta inesperada", output);
  } catch (err) {
    stopAnimation(false);
    output.textContent = "❌ No se pudo conectar con backend";
    console.error(err);
  }
});






