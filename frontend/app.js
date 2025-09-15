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
formA.addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("msgA").value.trim();
  if (!msg) return;

  appendMessage(logA, msg, "me");
  document.getElementById("msgA").value = "";

  const mode = document.querySelector("input[name='modeA']:checked").value;

  try {
    const res = await fetch(`${baseUrl}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: msg, mode }),
    });

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
    if (data.ok && data.answer) {
      appendMessage(logA, data.answer, "ai");
    } else {
      appendMessage(logA, "⚠️ Respuesta inesperada del backend", "ai");
      console.error("Respuesta inesperada:", data);
    }
  } catch (err) {
    appendMessage(logA, "❌ No se pudo conectar con backend", "ai");
    console.error(err);
  }
});

// =============================
// Panel B: Teacher con RAG
// =============================
formB.addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("msgB").value.trim();
  if (!msg) return;

  appendMessage(logB, msg, "me");
  document.getElementById("msgB").value = "";

  const topic = document.getElementById("topicB").value.trim();
  const level = document.getElementById("levelB").value.trim();

  try {
    const res = await fetch(`${baseUrl}/api/teacher`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: msg, topic, level }),
    });

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
    if (data.ok && data.answer) {
      appendMessage(logB, data.answer, "ai");
    } else {
      appendMessage(logB, "⚠️ Respuesta inesperada del backend", "ai");
      console.error("Respuesta inesperada:", data);
    }
  } catch (err) {
    appendMessage(logB, "❌ No se pudo conectar con backend", "ai");
    console.error(err);
  }
});

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






