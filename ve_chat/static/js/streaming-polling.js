// streaming-polling.js - Versión FINAL (encuestas funcionales)
class StreamingPolling {
  constructor(eventSlug, isOrganizer) {
    this.eventSlug = eventSlug;
    this.isOrganizer = isOrganizer;
    this.pollingInterval = null;
    this.pollRefreshInterval = null;
    this.chatContainer = document.getElementById("sr-chat-messages");
    this.pollSection = document.getElementById("sr-poll-section");
    this.currentPollId = null;
    this.hasVoted = false;
    this.handsInterval = null;
    this.lastHandsCount = 0;

    this.init();
    if (this.isOrganizer) {
      this.startHandsMonitoring();
    }
    this.lastRaiseHandTime = 0;
  }

  init() {
    this.startPolling();
    this.bindEvents();
    this.loadActivePoll();
    this.startPollRefresh();
  }

  startPolling() {
    this.pollingInterval = setInterval(() => this.fetchMessages(), 2000);
  }

  startPollRefresh() {
    if (this.pollRefreshInterval) clearInterval(this.pollRefreshInterval);
    this.pollRefreshInterval = setInterval(() => this.fetchActivePoll(), 5000);
  }

  async fetchActivePoll() {
    try {
      const res = await fetch(`/chat/api/${this.eventSlug}/poll/active/`);
      if (!res.ok) return;
      const data = await res.json();

      // Si hay encuesta activa
      if (data.active_poll && data.poll_id) {
        const pollId = data.poll_id;
        const votedKey = `poll_voted_${this.eventSlug}_${pollId}`;
        const alreadyVoted = localStorage.getItem(votedKey) === "true";

        if (pollId !== this.currentPollId) {
          this.currentPollId = pollId;
          this.hasVoted = alreadyVoted;

          if (this.isOrganizer) {
            this.fetchPollResults(pollId);
          } else {
            if (alreadyVoted) {
              this.fetchPollResults(pollId);
            } else {
              this.showPoll(data);
            }
          }
        } else {
          // misma encuesta: refrescar resultados si corresponde
          if (this.isOrganizer || this.hasVoted) {
            this.fetchPollResults(pollId);
          }
        }
      }
      // No hay encuesta activa
      else if (this.currentPollId !== null) {
        this.clearPollSection();
        this.currentPollId = null;
        this.hasVoted = false;
      }
    } catch (err) {
      console.error("Error refrescando encuesta:", err);
    }
  }

  clearPollSection() {
    this.pollSection.innerHTML = `<div class="text-center py-5 text-muted">
        <i class="bi bi-inbox display-6 opacity-25"></i>
        <p class="mt-2 small fw-bold">No hay encuestas activas</p>
    </div>`;
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
        console.log("Pin toggled.");
      } else {
        console.error("Error al fijar/desfijar:", response.status);
      }
    } catch (err) {
      console.error("Error en togglePin:", err);
    }
  }

  async sendMessage(content, anonymous) {
    try {
      const response = await fetch(`/chat/api/${this.eventSlug}/send/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCsrfToken(),
        },
        body: JSON.stringify({ content, anonymous }),
      });
      if (!response.ok) {
        const error = await response.json();
        console.error("Error al enviar mensaje:", error);
        return false;
      }
      return true;
    } catch (err) {
      console.error("Error de red en sendMessage:", err);
      return false;
    }
  }

  async raiseHand() {
    // --- Throttle: evitar spam ---
    const now = Date.now();
    const minInterval = 20000;
    const timeSinceLast = now - this.lastRaiseHandTime;
    if (timeSinceLast < minInterval) {
      const secondsLeft = Math.ceil((minInterval - timeSinceLast) / 1000);
      if (typeof window.showToast === "function") {
        window.showToast(
          `Espera ${secondsLeft} segundos antes de volver a levantar la mano.`,
          "warning",
        );
      } else {
        console.log(`Espera ${secondsLeft} segundos.`);
      }
      return;
    }
    this.lastRaiseHandTime = now;

    const raiseBtn = document.getElementById("sr-raise-hand-btn");
    if (raiseBtn) raiseBtn.disabled = true;

    try {
      const response = await fetch(`/chat/api/${this.eventSlug}/raise/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": this.getCsrfToken(),
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error del backend:", errorData);
        if (
          errorData.error ===
          "Debes esperar unos segundos antes de volver a levantar la mano."
        ) {
          alert(errorData.error);
        } else {
          alert(
            "No se pudo levantar la mano: " +
              (errorData.error || "Error desconocido"),
          );
        }
        return;
      }

      const sendResult = await this.sendMessage(
        "✋ He levantado la mano",
        false,
      );
      console.log("Mensaje enviado:", sendResult);
      console.log("Mano levantada correctamente");

      if (typeof window.showToast === "function") {
        window.showToast(
          "¡Has levantado la mano! El organizador te atenderá en breve.",
          "success",
        );
      }
    } catch (err) {
      console.error("Error de red:", err);
      alert("Error de conexión al levantar la mano. Revisa tu red.");
    } finally {
      if (raiseBtn) {
        setTimeout(() => {
          raiseBtn.disabled = false;
        }, minInterval);
      }
    }
  }

  async loadActivePoll() {
    try {
      const res = await fetch(`/chat/api/${this.eventSlug}/poll/active/`);
      if (!res.ok) return;
      const data = await res.json();
      if (data.active_poll && data.poll_id) {
        this.currentPollId = data.poll_id;
        const votedKey = `poll_voted_${this.eventSlug}_${this.currentPollId}`;
        this.hasVoted = localStorage.getItem(votedKey) === "true";
        if (this.isOrganizer) {
          this.fetchPollResults(this.currentPollId);
        } else {
          if (this.hasVoted) {
            this.fetchPollResults(this.currentPollId);
          } else {
            this.showPoll(data);
          }
        }
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
      this.currentPollId = poll.poll_id;
      this.hasVoted = false;
      this.fetchPollResults(this.currentPollId);
    } else {
      const error = await res.json();
      alert("Error al crear encuesta: " + (error.error || "desconocido"));
    }
  }

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
        const votedKey = `poll_voted_${this.eventSlug}_${pollId}`;
        localStorage.setItem(votedKey, "true");
        this.hasVoted = true;
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
        pollForm.removeEventListener("submit", this._pollSubmitHandler);
        this._pollSubmitHandler = (e) => {
          e.preventDefault();
          e.stopPropagation();
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
          div.className = "input-group mb-2 sr-poll-option-input-group";
          div.innerHTML = `<input type="text" class="form-control bg-light border-0 rounded-3 sr-poll-option-input" placeholder="Opción"><button class="btn btn-outline-danger" type="button" onclick="this.parentElement.remove()">-</button>`;
          container.appendChild(div);
        });
      }
    }
  }

  async startHandsMonitoring() {
    if (this.handsInterval) clearInterval(this.handsInterval);
    // Obtener el valor actual inicial antes de empezar el intervalo
    try {
      const response = await fetch(
        `/chat/api/${this.eventSlug}/hands/unattended/`,
      );
      if (response.ok) {
        const data = await response.json();
        this.lastHandsCount = data.unattended_hands;
        // Si hay manos sin atender al cargar, mostrar badge pero sin notificación de sonido/toast
        if (this.lastHandsCount > 0) {
          const badgeContainer = document.getElementById(
            "hands-notification-badge",
          );
          const counterSpan = document.getElementById("hands-count");
          if (badgeContainer && counterSpan) {
            badgeContainer.classList.remove("d-none");
            counterSpan.textContent = this.lastHandsCount;
          }
        }
      }
    } catch (err) {
      console.error("Error initializing hands count:", err);
    }
    this.handsInterval = setInterval(() => this.checkHands(), 3000);
  }

  async checkHands() {
    try {
      const response = await fetch(
        `/chat/api/${this.eventSlug}/hands/unattended/`,
      );
      if (!response.ok) return;
      const data = await response.json();
      const currentCount = data.unattended_hands;

      if (currentCount > this.lastHandsCount) {
        this.playNotificationSound();
        this.showHandNotification(currentCount - this.lastHandsCount);
      }
      this.lastHandsCount = currentCount;
    } catch (err) {
      console.error("Error checking hands:", err);
    }
  }

  playNotificationSound() {
    try {
      const audio = new Audio("/static/sounds/bright-bell.mp3");
      audio.volume = 0.5;
      audio.play().catch((e) => console.log("Audio no pudo reproducirse", e));
    } catch (err) {
      console.log("Error con sonido:", err);
    }
  }

  showHandNotification(newCount) {
    const message = `🙋‍♂️ ${newCount} persona(s) ha(n) levantado la mano. Revisa el chat.`;
    if (typeof window.showToast === "function") {
      window.showToast(message, "warning");
    } else {
      console.warn("showToast no disponible:", message);
    }
    const badgeContainer = document.getElementById("hands-notification-badge");
    const counterSpan = document.getElementById("hands-count");
    if (badgeContainer && counterSpan) {
      badgeContainer.classList.remove("d-none");
      counterSpan.textContent = this.lastHandsCount;
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const eventSlug = document.body.dataset.eventSlug || window.eventSlug;
  const isOrganizer = window.isOrganizer || false;
  if (!eventSlug) {
    console.error("No se encontró el slug del evento");
    return;
  }
  window.room = new StreamingPolling(eventSlug, isOrganizer);
});
