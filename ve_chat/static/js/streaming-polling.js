// streaming-polling.js - Versión CORREGIDA (encuestas funcionales, sin recarga)
class StreamingPolling {
  constructor(eventSlug, isOrganizer) {
    this.eventSlug = eventSlug;
    this.isOrganizer = isOrganizer;
    this.pollingInterval = null;
    this.chatContainer = document.getElementById("sr-chat-messages");
    this.pollSection = document.getElementById("sr-poll-section");

    this.init();
  }

  init() {
    this.startPolling();
    this.bindEvents();
    this.loadActivePoll();
  }

  startPolling() {
    this.pollingInterval = setInterval(() => this.fetchMessages(), 2000);
  }

  async fetchMessages() {
    try {
      const response = await fetch(`/chat/api/${this.eventSlug}/messages/`);
      const data = await response.json();
      this.chatContainer.innerHTML = "";
      this.renderMessages(data.messages);
    } catch (err) {
      console.error("Error fetching messages:", err);
    }
  }

  renderMessages(messages) {
    if (!messages.length) return;
    for (const msg of messages) {
      this.addMessageToDOM(msg);
    }
    const shouldScroll =
      this.chatContainer.scrollHeight - this.chatContainer.scrollTop < 300;
    if (shouldScroll)
      this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
  }

  addMessageToDOM(msg) {
    const div = document.createElement("div");
    div.className = `sr-chat-bubble ${msg.is_mine ? "sr-mine ms-auto" : ""}`;
    div.dataset.messageId = msg.id;
    div.dataset.pinned = msg.is_pinned;

    const time = new Date(msg.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    const pinButtonHtml = this.isOrganizer
      ? `<button class="pin-btn" data-message-id="${msg.id}" data-pinned="${msg.is_pinned}" title="${msg.is_pinned ? "Desfijar" : "Fijar"}">
            <i class="bi ${msg.is_pinned ? "bi-pin-fill" : "bi-pin"}"></i>
           </button>`
      : "";

    div.innerHTML = `
        <div class="message-row">
            <div class="message-content">
                <div class="sr-chat-meta"><strong>${this.escapeHtml(msg.username)}</strong> • ${time}</div>
                <div class="sr-chat-text">${this.escapeHtml(msg.content)}</div>
            </div>
            ${pinButtonHtml}
        </div>
    `;

    const btn = div.querySelector(".pin-btn");
    if (btn) {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const currentPinned = btn.dataset.pinned === "true";
        this.togglePin(msg.id, !currentPinned);
      });
    }

    this.chatContainer.appendChild(div);
  }

  async togglePin(messageId, pinned) {
    try {
      const response = await fetch(
        `/chat/api/${this.eventSlug}/pin/${messageId}/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.getCsrfToken(),
          },
          body: JSON.stringify({ pinned }),
        },
      );
      if (response.ok) {
        console.log("Pin toggled. Esperando siguiente actualización...");
      } else {
        console.error("Error al fijar/desfijar:", response.status);
      }
    } catch (err) {
      console.error("Error en togglePin:", err);
    }
  }

  async sendMessage(content, anonymous) {
    try {
      await fetch(`/chat/api/${this.eventSlug}/send/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCsrfToken(),
        },
        body: JSON.stringify({ content, anonymous }),
      });
    } catch (err) {
      console.error(err);
    }
  }

  async raiseHand() {
    try {
      const response = await fetch(`/chat/api/${this.eventSlug}/raise/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCsrfToken(),
        },
      });

      if (
        response.status === 302 ||
        response.status === 401 ||
        response.status === 403
      ) {
        alert("Debes iniciar sesión para levantar la mano.");
        window.location.href =
          "/usuarios/login/?next=" + encodeURIComponent(window.location.href);
        return;
      }

      if (response.ok) {
        await this.sendMessage("✋ He levantado la mano", false);
        console.log("Mano levantada correctamente");
      } else {
        const errorData = await response.json();
        if (errorData.error === "Ya tienes la mano levantada") {
          console.warn("Ya tienes la mano levantada");
        } else {
          console.error("Error al levantar mano:", errorData.error);
        }
      }
    } catch (err) {
      console.error("Error de red:", err);
    }
  }

  async loadActivePoll() {
    try {
      const res = await fetch(`/chat/api/${this.eventSlug}/poll/active/`);
      if (!res.ok) return;
      const data = await res.json();
      if (data.active_poll !== null) {
        this.showPoll(data);
      }
    } catch (err) {
      console.error("Error al cargar encuesta activa:", err);
    }
  }

  async createPoll(question, options) {
    const res = await fetch(`/chat/api/${this.eventSlug}/poll/create/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": this.getCsrfToken(),
      },
      body: JSON.stringify({ question, options }),
    });
    if (res.ok) {
      const poll = await res.json();
      this.showPoll(poll); // Solo muestra la encuesta para votar, no resultados
    } else {
      const error = await res.json();
      alert("Error al crear encuesta: " + (error.error || "desconocido"));
    }
  }

  // ✅ MÉTODO DE VOTACIÓN (antes faltaba)
  async votePoll(pollId) {
    const selectedRadio = document.querySelector(
      'input[name="pollOption"]:checked',
    );
    if (!selectedRadio) {
      alert("Selecciona una opción antes de votar");
      return;
    }
    const optionId = parseInt(selectedRadio.value);

    try {
      const response = await fetch(
        `/chat/api/${this.eventSlug}/poll/${pollId}/vote/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": this.getCsrfToken(),
          },
          body: JSON.stringify({ option_id: optionId }),
        },
      );

      if (
        response.status === 302 ||
        response.status === 401 ||
        response.status === 403
      ) {
        alert("Debes iniciar sesión para votar. Serás redirigido.");
        window.location.href =
          "/usuarios/login/?next=" + encodeURIComponent(window.location.href);
        return;
      }

      if (response.ok) {
        // Voto exitoso: mostrar resultados actualizados
        await this.fetchPollResults(pollId);
      } else {
        const errorData = await response.json();
        alert("Error al votar: " + (errorData.error || "desconocido"));
      }
    } catch (err) {
      console.error("Error de red al votar:", err);
      alert("Error de conexión al votar");
    }
  }

  async fetchPollResults(pollId) {
    try {
      const res = await fetch(
        `/chat/api/${this.eventSlug}/poll/${pollId}/results/`,
      );
      if (!res.ok) return;
      const data = await res.json();
      this.updatePollResults(data);
    } catch (err) {
      console.error("Error al obtener resultados:", err);
    }
  }

  showPoll(poll) {
    this.pollSection.innerHTML = `
      <div class="sr-poll-card">
        <h5>${this.escapeHtml(poll.question)}</h5>
        <div id="sr-poll-options-list" class="mt-3">
          ${poll.options
            .map(
              (opt) => `
            <div class="form-check sr-poll-option">
              <input class="form-check-input" type="radio" name="pollOption" value="${opt.id}" id="opt-${opt.id}">
              <label class="form-check-label" for="opt-${opt.id}">${this.escapeHtml(opt.text)}</label>
            </div>
          `,
            )
            .join("")}
        </div>
        <button class="btn btn-primary w-100 mt-3" onclick="window.room.votePoll(${poll.poll_id})">Votar</button>
      </div>
    `;
  }

  updatePollResults(data) {
    this.pollSection.innerHTML = `
      <div class="sr-poll-card">
        <h5>Resultados: ${this.escapeHtml(data.question)}</h5>
        <div class="mt-3">
          ${data.results
            .map(
              (res) => `
            <div class="mb-2">
              <div class="d-flex justify-content-between small mb-1">
                <span>${this.escapeHtml(res.option)}</span>
                <span>${res.percentage}% (${res.votes})</span>
              </div>
              <div class="progress" style="height: 10px;">
                <div class="progress-bar" role="progressbar" style="width: ${res.percentage}%"></div>
              </div>
            </div>
          `,
            )
            .join("")}
        </div>
      </div>
    `;
  }

  sendAnonQuestion() {
    const textarea = document.getElementById("sr-anon-question-text");
    if (textarea.value.trim()) {
      this.sendMessage(textarea.value, true);
      textarea.value = "";
      bootstrap.Modal.getInstance(
        document.getElementById("anonymousQuestionModal"),
      ).hide();
    }
  }

  async sendSatisfaction(rating) {
    try {
      await fetch(`/chat/api/${this.eventSlug}/satisfaction/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCsrfToken(),
        },
        body: JSON.stringify({ rating }),
      });
    } catch (err) {
      console.error("Error al enviar satisfacción:", err);
    }
  }

  getCsrfToken() {
    let cookieValue = null;
    const name = "csrftoken";
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue || "";
  }

  escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>]/g, function (m) {
      if (m === "&") return "&amp;";
      if (m === "<") return "&lt;";
      if (m === ">") return "&gt;";
      return m;
    });
  }

  bindEvents() {
    const chatForm = document.getElementById("sr-chat-form");
    if (chatForm) {
      chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const input = document.getElementById("sr-chat-input");
        if (input.value.trim()) {
          this.sendMessage(input.value, false);
          input.value = "";
        }
      });
    }
    const raiseBtn = document.getElementById("sr-raise-hand-btn");
    if (raiseBtn) raiseBtn.addEventListener("click", () => this.raiseHand());

    if (this.isOrganizer) {
      const pollForm = document.getElementById("sr-create-poll-form");
      if (pollForm) {
        // Eliminar event listeners previos para evitar duplicados
        pollForm.removeEventListener("submit", this._pollSubmitHandler);
        this._pollSubmitHandler = (e) => {
          e.preventDefault();
          e.stopPropagation(); // Asegurar que no se propaga
          const question = document.getElementById("sr-poll-question").value;
          const optionInputs = document.querySelectorAll(
            ".sr-poll-option-input",
          );
          const options = Array.from(optionInputs)
            .map((i) => i.value)
            .filter((v) => v.trim());
          if (question && options.length >= 2) {
            this.createPoll(question, options);
          } else {
            alert("La pregunta y al menos 2 opciones son requeridas");
          }
          return false;
        };
        pollForm.addEventListener("submit", this._pollSubmitHandler);
      }
      const addOptionBtn = document.getElementById("sr-add-option-btn");
      if (addOptionBtn) {
        addOptionBtn.addEventListener("click", () => {
          const container = document.getElementById(
            "sr-poll-options-container",
          );
          const div = document.createElement("div");
          div.className = "input-group mb-2";
          div.innerHTML = `<input type="text" class="form-control bg-light border-0 rounded-3 sr-poll-option-input" placeholder="Opción"><button class="btn btn-outline-danger" type="button" onclick="this.parentElement.remove()">-</button>`;
          container.appendChild(div);
        });
      }
    }
  }
}

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  const eventSlug = document.body.dataset.eventSlug || window.eventSlug;
  const isOrganizer = window.isOrganizer || false;
  if (!eventSlug) {
    console.error("No se encontró el slug del evento");
    return;
  }
  window.room = new StreamingPolling(eventSlug, isOrganizer);
});
