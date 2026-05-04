// chat-counter.js - Actualiza el badge de chat para administradores
(function () {
  "use strict";

  function actualizarContadorChat() {
    const badge = document.getElementById("chat-badge");
    if (!badge) return;

    fetch("/chat/contar-no-leidos/")
      .then((response) => {
        if (!response.ok) throw new Error("Error al obtener el conteo");
        return response.json();
      })
      .then((data) => {
        if (data.count > 0) {
          badge.textContent = data.count;
          badge.style.display = "block";
        } else {
          badge.style.display = "none";
        }
      })
      .catch((error) => {
        console.error("Error al actualizar contador de chat:", error);
        badge.style.display = "none";
      });
  }

  // Ejecutar al cargar la página y cada 30 segundos
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      if (document.getElementById("chat-badge")) {
        actualizarContadorChat();
        setInterval(actualizarContadorChat, 30000);
      }
    });
  } else {
    if (document.getElementById("chat-badge")) {
      actualizarContadorChat();
      setInterval(actualizarContadorChat, 30000);
    }
  }
})();
