// streaming-room.js - Versión con persistencia de satisfacción y emoji funcional
class StreamingRoomExtras {
  constructor(eventSlug, eventId) {
    this.eventSlug = eventSlug;
    this.eventId = eventId; // para localStorage
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.init();
  }

  init() {
    this.bindRecording();
    this.bindSatisfaction();
    this.restoreSatisfaction(); // restaurar calificación guardada
  }

  // Pequeño helper para mostrar mensajes (toast o alert)
  showMessage(msg, type = "info") {
    if (typeof window.showToast === "function") {
      window.showToast(msg, type);
    } else {
      // Fallback
      console.log(`[${type.toUpperCase()}] ${msg}`);
      // alert(msg); // no recomendado, mejor console
    }
  }

  bindRecording() {
    const recordBtn = document.getElementById("sr-record-btn");
    if (recordBtn) {
      const newBtn = recordBtn.cloneNode(true);
      recordBtn.parentNode.replaceChild(newBtn, recordBtn);
      newBtn.addEventListener("click", () => this.toggleRecording());
    }
  }

  async toggleRecording() {
    const btn = document.getElementById("sr-record-btn");
    if (!btn) return;

    const icon = btn.querySelector("i");
    const textSpan = btn.querySelector("span");

    if (!this.mediaRecorder || this.mediaRecorder.state === "inactive") {
      try {
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: true,
        });
        this.mediaRecorder = new MediaRecorder(stream);
        this.recordedChunks = [];

        this.mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) this.recordedChunks.push(e.data);
        };

        this.mediaRecorder.onstop = () => {
          const blob = new Blob(this.recordedChunks, { type: "video/webm" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `grabacion-${this.eventSlug}.webm`;
          a.click();
          URL.revokeObjectURL(url);
          if (icon) icon.className = "bi bi-camera-video";
          if (textSpan) textSpan.textContent = "Grabar pantalla";
          btn.classList.remove("btn-danger");
          btn.classList.add("btn-outline-secondary");
        };

        this.mediaRecorder.start();
        if (icon) icon.className = "bi bi-stop-circle sr-recording-active";
        if (textSpan) textSpan.textContent = "Detener grabación";
        btn.classList.remove("btn-outline-secondary");
        btn.classList.add("btn-danger");
      } catch (err) {
        console.error("Error al grabar:", err);
        alert("No se pudo iniciar la grabación. Asegúrate de dar permisos.");
      }
    } else {
      this.mediaRecorder.stop();
      this.mediaRecorder.stream.getTracks().forEach((track) => track.stop());
    }
  }

  bindSatisfaction() {
    // ===== 1. BOTÓN EMOJI (😊) =====
    const satisfactionBtn = document.getElementById("sr-satisfaction-btn");
    if (satisfactionBtn) {
      // Eliminar listeners anteriores
      const newBtn = satisfactionBtn.cloneNode(true);
      satisfactionBtn.parentNode.replaceChild(newBtn, satisfactionBtn);
      newBtn.addEventListener("click", () => {
        console.log("Emoji satisfaction clicked");
        // Enviar satisfacción máxima (5)
        if (window.room && typeof window.room.sendSatisfaction === "function") {
          window.room.sendSatisfaction(5);
          // Guardar en localStorage para persistencia
          localStorage.setItem(`satisfaction_${this.eventId}`, "5");
          this.highlightStars(5); // resaltar estrellas
          this.showMessage("¡Gracias por tu valoración! ⭐", "success");
        } else {
          console.warn("sendSatisfaction no disponible");
          this.showMessage(
            "No se pudo enviar la valoración. Intenta más tarde.",
            "error",
          );
        }
      });
    }

    // ===== 2. SATISFACCIÓN ESTRELLAS =====
    const starsContainer = document.querySelector(".sr-star-rating");
    if (starsContainer) {
      // Recrear inputs para asegurar listeners frescos
      const inputs = starsContainer.querySelectorAll("input");
      inputs.forEach((input) => {
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);

        newInput.addEventListener("change", (e) => {
          const rating = parseInt(e.target.value);
          console.log(`Estrella seleccionada: ${rating}`);
          if (
            window.room &&
            typeof window.room.sendSatisfaction === "function"
          ) {
            window.room.sendSatisfaction(rating);
            // Guardar en localStorage
            localStorage.setItem(`satisfaction_${this.eventId}`, rating);
            this.highlightStars(rating);
            this.showMessage(
              `Valoración: ${rating} estrellas. ¡Gracias!`,
              "success",
            );
          } else {
            console.error("sendSatisfaction NO está disponible en window.room");
            this.showMessage("No se pudo enviar la valoración.", "error");
          }
        });
      });
    }
  }

  // Resalta las estrellas según la puntuación
  highlightStars(rating) {
    const starsContainer = document.querySelector(".sr-star-rating");
    if (!starsContainer) return;
    const labels = starsContainer.querySelectorAll("label");
    labels.forEach((label, idx) => {
      if (idx < rating) {
        label.style.color = "#fbbf24"; // amarillo
      } else {
        label.style.color = ""; // color por defecto
      }
    });
    // Opcional: marcar el radio correspondiente
    const radioToCheck = starsContainer.querySelector(
      `input[value="${rating}"]`,
    );
    if (radioToCheck) radioToCheck.checked = true;
  }

  // Restaurar satisfacción guardada en localStorage al cargar la página
  restoreSatisfaction() {
    const savedRating = localStorage.getItem(`satisfaction_${this.eventId}`);
    if (savedRating) {
      const rating = parseInt(savedRating);
      console.log(`Restaurando satisfacción guardada: ${rating}`);
      this.highlightStars(rating);
      // Enviar al backend opcionalmente (para que el servidor también lo sepa)
      if (window.room && typeof window.room.sendSatisfaction === "function") {
        window.room.sendSatisfaction(rating);
      }
    }
  }
}

// Inicialización - espera a que window.room esté disponible
document.addEventListener("DOMContentLoaded", () => {
  console.log("Inicializando StreamingRoomExtras...");

  // Obtener eventId (definido en el template)
  const eventId = window.EVENT_ID || null;
  if (!eventId) {
    console.warn(
      "No se encontró EVENT_ID, la satisfacción no se podrá persistir.",
    );
  }

  if (window.room && typeof window.room.sendSatisfaction === "function") {
    console.log("window.room detectado correctamente");
    new StreamingRoomExtras(window.room.eventSlug || window.eventSlug, eventId);
  } else {
    const checkInterval = setInterval(() => {
      if (window.room && typeof window.room.sendSatisfaction === "function") {
        console.log("window.room ahora disponible");
        clearInterval(checkInterval);
        new StreamingRoomExtras(
          window.room.eventSlug || window.eventSlug,
          eventId,
        );
      } else {
        console.log("Esperando window.room...");
      }
    }, 100);

    setTimeout(() => {
      clearInterval(checkInterval);
      if (!window.room || typeof window.room.sendSatisfaction !== "function") {
        console.error("No se pudo detectar window.room con sendSatisfaction");
      }
    }, 5000);
  }
  
  const confirmFinalizeBtn = document.getElementById("confirmFinalizeBtn");
  if (confirmFinalizeBtn) {
    // Construir la URL de finalización usando window.EVENT_ID (que existe)
    const finalizeUrl = `/eventos/finalizar/${window.EVENT_ID}/`; // Ajusta si tu URL es diferente
    confirmFinalizeBtn.addEventListener("click", function () {
      const form = document.createElement("form");
      form.method = "POST";
      form.action = finalizeUrl;
      // Obtener token CSRF
      let csrfToken = "";
      const csrfCookie = document.cookie
        .split(";")
        .find((c) => c.trim().startsWith("csrftoken="));
      if (csrfCookie) {
        csrfToken = csrfCookie.split("=")[1];
      }
      const csrfInput = document.createElement("input");
      csrfInput.type = "hidden";
      csrfInput.name = "csrfmiddlewaretoken";
      csrfInput.value = csrfToken;
      form.appendChild(csrfInput);
      document.body.appendChild(form);
      form.submit();
    });
  }
});
