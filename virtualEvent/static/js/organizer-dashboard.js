// organizer-dashboard.js - Dashboard del organizador (VERSIÓN VDO.Ninja)
// Funcionalidades: edición de evento, invitaciones, métricas en tiempo real, PDF y VDO.Ninja
document.addEventListener("DOMContentLoaded", function () {
  // --- Variables globales desde el template ---
  const eventId = typeof EVENT_ID !== "undefined" ? EVENT_ID : null;
  const csrfToken = typeof CSRF_TOKEN !== "undefined" ? CSRF_TOKEN : "";
  const saveVdoNinjaUrl =
    typeof SAVE_VDO_NINJA_URL !== "undefined" ? SAVE_VDO_NINJA_URL : null;
  const metricsUrl = typeof METRICS_URL !== "undefined" ? METRICS_URL : null;

  // ========================
  // Toast de notificación (sin alert molestos)
  // ========================
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
  // 4. Métricas en tiempo real (usando API real)
  // ========================
  function loadMetrics() {
    if (!eventId || !metricsUrl) return;
    fetch(metricsUrl)
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

  if (eventId && metricsUrl) {
    loadMetrics();
    setInterval(loadMetrics, 5000);
  }

  // ========================
  // 5. Botón de exportar PDF
  // ========================
  const exportPdfBtn = document.getElementById("od-btn-export-pdf");
  if (exportPdfBtn && eventId) {
    exportPdfBtn.addEventListener("click", function () {
      window.location.href = `/eventos/evento/${eventId}/pdf-report/`;
    });
  }

  // ========================
  // 6. VDO.Ninja: Guardar URL de transmisión
  // ========================
  const vdoInput = document.getElementById("od-vdoninja-url");
  const saveVdoBtn = document.getElementById("od-btn-save-vdoninja");
  const statusDiv = document.getElementById("od-vdo-status");

  function isValidVdoNinjaUrl(url) {
    if (!url) return false;
    return url.includes("vdo.ninja") && url.includes("view=");
  }

  function saveVdoNinjaUrl(url) {
    if (!saveVdoNinjaUrl) {
      showToast("Error: URL de guardado no configurada", true);
      return Promise.reject("No endpoint");
    }
    if (!eventId || !csrfToken) {
      showToast("Error de autenticación", true);
      return Promise.reject("Auth error");
    }
    let cleanUrl = url.trim();
    return fetch(saveVdoNinjaUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ vdoninja_url: cleanUrl }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "ok") {
          showToast("✓ Enlace de transmisión guardado correctamente");
          if (data.url && vdoInput && data.url !== vdoInput.value) {
            vdoInput.value = data.url;
          }
          if (statusDiv) {
            statusDiv.innerHTML =
              '<span class="text-success"><i class="bi bi-check-circle"></i> Enlace guardado. La transmisión se mostrará en la sala de streaming.</span>';
            setTimeout(() => {
              if (statusDiv) statusDiv.innerHTML = "";
            }, 5000);
          }
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

  if (saveVdoBtn && vdoInput) {
    saveVdoBtn.addEventListener("click", function () {
      let url = vdoInput.value.trim();
      if (!url) {
        showToast("Por favor, pega el enlace de VDO.Ninja", true);
        if (statusDiv)
          statusDiv.innerHTML =
            '<span class="text-warning"><i class="bi bi-exclamation-triangle"></i> El enlace no puede estar vacío.</span>';
        return;
      }
      if (!isValidVdoNinjaUrl(url)) {
        showToast(
          "El enlace no parece ser de VDO.Ninja (debe contener 'vdo.ninja' y 'view=')",
          true,
        );
        if (statusDiv)
          statusDiv.innerHTML =
            '<span class="text-danger"><i class="bi bi-x-circle"></i> Enlace inválido. Asegúrate de copiar la URL VIEW correcta.</span>';
        return;
      }
      saveVdoNinjaUrl(url);
    });
  }

  if (vdoInput && vdoInput.value.trim() && statusDiv) {
    statusDiv.innerHTML =
      '<span class="text-info"><i class="bi bi-info-circle"></i> Enlace actual cargado. Puedes cambiarlo si es necesario.</span>';
  }
});

// Funciones globales por si se llaman desde onclick (no se usan en el nuevo flujo, pero se mantienen por compatibilidad)
function copyToClipboard() {
  const urlText = document.getElementById("od-copy-url")?.innerText.trim();
  if (urlText) {
    navigator.clipboard.writeText(urlText).catch(console.error);
  }
}
function exportReport() {
  alert("Funcionalidad en desarrollo");
}
