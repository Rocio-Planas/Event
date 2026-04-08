// organizer-dashboard.js - Dashboard del organizador
// Funcionalidades: edición de evento, invitaciones, métricas (placeholder) y YouTube (guardado + previsualización)

document.addEventListener("DOMContentLoaded", function () {
  // --- Variables globales desde el template ---
  const eventId = typeof EVENT_ID !== "undefined" ? EVENT_ID : null;
  const csrfToken = typeof CSRF_TOKEN !== "undefined" ? CSRF_TOKEN : "";
  const saveYoutubeUrlEndpoint =
    typeof SAVE_YOUTUBE_URL !== "undefined" ? SAVE_YOUTUBE_URL : null;

  // ========================
  // 1. Previsualización de imagen de portada
  // ========================
  const imageInput = document.getElementById("od-image-input");
  const imgPreview = document.getElementById("od-img-preview");
  if (imageInput && imgPreview) {
    imageInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          imgPreview.src = event.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // ========================
  // 2. Mostrar/ocultar invitaciones según acceso (público/privado)
  // ========================
  const radios = document.querySelectorAll(".od-access-radio");
  const invitationsContainer = document.getElementById(
    "od-invitations-container",
  );
  if (radios.length && invitationsContainer) {
    radios.forEach((radio) => {
      radio.addEventListener("change", function () {
        invitationsContainer.classList.toggle(
          "d-none",
          this.value !== "private",
        );
      });
    });
  }

  // ========================
  // 3. Copiar enlace de invitación al portapapeles
  // ========================
  const copyBtn = document.getElementById("od-btn-copy-link");
  const inviteLinkInput = document.getElementById("od-invite-link");
  const copyFeedback = document.getElementById("od-copy-feedback");
  if (copyBtn && inviteLinkInput) {
    copyBtn.addEventListener("click", function () {
      inviteLinkInput.select();
      document.execCommand("copy");
      if (copyFeedback) {
        copyFeedback.classList.remove("d-none");
        setTimeout(() => copyFeedback.classList.add("d-none"), 2000);
      }
    });
  }

  // ========================
  // 4. Métricas en tiempo real (placeholder – lo implementarás después)
  // ========================
  // Métricas en tiempo real usando la API real
  function loadMetrics() {
    if (!eventId) return;
    fetch(`/virtualEvent/${eventId}/metrics/`)
      .then((res) => res.json())
      .then((data) => {
        document.getElementById("metric-online").innerText =
          data.active_viewers || 0;
        document.getElementById("metric-messages").innerText =
          data.total_messages || 0;
        document.getElementById("metric-hands").innerText =
          data.total_hands || 0;
        document.getElementById("metric-participation").innerText =
          (data.participation_percent || 0) + "%";
        document.getElementById("metric-time").innerText =
          data.elapsed_time || "00:00:00";
        document.getElementById("metric-satisfaction").innerText =
          data.average_satisfaction || 0;
      })
      .catch((err) => console.error("Error cargando métricas:", err));
  }

  // Llamar cada 5 segundos
  if (eventId) {
    loadMetrics();
    setInterval(loadMetrics, 5000);
  }

  // ========================
  // Evento para el botón de exportar PDF 
  // ========================
  const exportPdfBtn = document.getElementById("od-btn-export-pdf");
  if (exportPdfBtn && eventId) {
    exportPdfBtn.addEventListener("click", function () {
      window.location.href = `/virtualEvent/${eventId}/pdf-report/`;
    });
  }

  // ========================
  // 5. YouTube: guardado, previsualización y modal (opcional)
  // ========================
  const ytInput = document.getElementById("od-youtube-url");
  const previewContainer = document.getElementById("od-yt-preview-container");
  const miniIframe = document.getElementById("od-yt-mini-iframe");
  const modalIframe = document.getElementById("od-modal-iframe");
  const modalElement = document.getElementById("od-youtube-modal");
  const testBtn = document.getElementById("od-btn-test-youtube");
  const previewBtn = document.getElementById("od-btn-preview-yt");

  let modal = null;
  if (modalElement) modal = new bootstrap.Modal(modalElement);

  // Notificaciones toast (sin alert molestos)
  function showToast(message, isError = false) {
    const toastEl = document.getElementById("od-toast");
    if (toastEl) {
      const toastBody = document.getElementById("od-toast-body");
      toastBody.textContent = message;
      toastEl.classList.toggle("bg-danger", isError);
      toastEl.classList.toggle("bg-success", !isError);
      const toast = new bootstrap.Toast(toastEl);
      toast.show();
      setTimeout(() => {
        toastEl.classList.remove("bg-danger", "bg-success");
      }, 3000);
    } else {
      console.log(message);
    }
  }

  // Limpiar y convertir URL de YouTube a formato embed (acepta cualquier formato)
  function cleanYoutubeUrl(url) {
    if (!url || url.trim() === "") return "";
    let clean = url.trim();

    // Eliminar parámetros (todo lo que siga a '?')
    if (clean.includes("?")) clean = clean.split("?")[0];

    // Si no tiene protocolo, añadir https://
    if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
      clean = "https://" + clean;
    }

    // Caso 1: youtube.com/watch?v=...
    if (clean.includes("youtube.com/watch?v=")) {
      const videoId = clean.split("v=")[1].split("&")[0];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    // Caso 2: youtu.be/...
    else if (clean.includes("youtu.be/")) {
      const videoId = clean.split("youtu.be/")[1].split("?")[0];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    // Caso 3: ya es embed (youtube.com/embed/...)
    else if (clean.includes("youtube.com/embed/")) {
      // Asegurar dominio correcto (www.)
      if (clean.includes("://youtube.com/embed/")) {
        clean = clean.replace(
          "://youtube.com/embed/",
          "://www.youtube.com/embed/",
        );
      } else if (clean.includes("://www.youtube.com/embed/")) {
        // ya está bien
      } else {
        // si no tiene www, agregarlo
        clean = clean.replace("youtube.com/embed/", "www.youtube.com/embed/");
      }
      return clean;
    }

    // Si no es una URL de YouTube reconocida, devolvemos vacío
    return "";
  }

  // Actualizar el mini iframe de previsualización (sin guardar)
  function updatePreview() {
    let rawUrl = ytInput ? ytInput.value.trim() : "";
    let cleanUrl = "";

    if (rawUrl !== "") {
      cleanUrl = cleanYoutubeUrl(rawUrl);
    }

    if (cleanUrl === "") {
      previewContainer.classList.add("d-none");
      if (miniIframe) miniIframe.src = "about:blank";
      return;
    }

    // Si la URL limpia es diferente a la original, actualizamos el campo visualmente
    if (cleanUrl !== rawUrl && ytInput) {
      ytInput.value = cleanUrl;
    }
    miniIframe.src = cleanUrl;
    previewContainer.classList.remove("d-none");
  }

  // Guardar URL en el backend
  function saveYoutubeUrl(url) {
    if (!saveYoutubeUrlEndpoint) {
      showToast("Error: URL de guardado no configurada", true);
      return Promise.reject("No endpoint");
    }
    if (!eventId || !csrfToken) {
      showToast("Error de autenticación", true);
      return Promise.reject("Auth error");
    }
    return fetch(saveYoutubeUrlEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ youtube_url: url }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "ok") {
          showToast("✓ URL guardada correctamente");
          if (data.url && ytInput && data.url !== ytInput.value) {
            ytInput.value = data.url;
          }
          // Actualizar previsualización después de guardar
          updatePreview();
          return true;
        } else {
          showToast(
            "Error al guardar: " + (data.message || "desconocido"),
            true,
          );
          return false;
        }
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        showToast("Error de red al guardar", true);
        return false;
      });
  }

  // --- Eventos ---

  // Botón "Probar": guarda y actualiza preview (sin abrir modal)
  if (testBtn && ytInput) {
    testBtn.addEventListener("click", function () {
      let rawUrl = ytInput.value.trim();
      if (!rawUrl) {
        showToast("Escribe una URL de YouTube", true);
        return;
      }
      const cleanUrl = cleanYoutubeUrl(rawUrl);
      if (!cleanUrl) {
        showToast("URL no válida (debe ser de YouTube)", true);
        return;
      }
      if (cleanUrl !== rawUrl) ytInput.value = cleanUrl;
      saveYoutubeUrl(cleanUrl); // Guarda y actualiza preview (updatePreview se llama dentro de saveYoutubeUrl)
    });
  }

  // Botón "Previsualizar": solo actualiza el mini iframe (no guarda)
  if (previewBtn) {
    previewBtn.addEventListener("click", function (e) {
      e.preventDefault();
      updatePreview();
    });
  }

  // Auto‑guardado al perder el foco (opcional, pero útil)
  if (ytInput) {
    ytInput.addEventListener("change", function () {
      let url = this.value.trim();
      if (url) {
        const cleanUrl = cleanYoutubeUrl(url);
        if (cleanUrl !== url) this.value = cleanUrl;
        if (cleanUrl) saveYoutubeUrl(cleanUrl);
        else updatePreview();
      } else {
        updatePreview();
      }
    });
  }

  // Inicializar previsualización al cargar la página
  if (ytInput) {
    const initialUrl = ytInput.value.trim();
    if (initialUrl && cleanYoutubeUrl(initialUrl)) {
      updatePreview();
    } else {
      previewContainer.classList.add("d-none");
      if (miniIframe) miniIframe.src = "about:blank";
    }
  }

  // El modal se mantiene por si quieres usarlo en otro lado, pero no se abre con "Probar"
  // Si quieres eliminar completamente el modal, puedes borrar el HTML del modal.
});

// Funciones globales (por si se llaman desde onclick en el HTML)
function copyToClipboard() {
  const urlText = document.getElementById("od-copy-url")?.innerText.trim();
  if (urlText) {
    navigator.clipboard
      .writeText(urlText)
      .then(() => alert("¡Enlace copiado!"))
      .catch(console.error);
  }
}
function exportReport() {
  alert("Funcionalidad en desarrollo");
}
