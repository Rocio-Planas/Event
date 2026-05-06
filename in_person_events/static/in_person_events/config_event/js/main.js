document.addEventListener("DOMContentLoaded", () => {
    // Switch Toggling Logic
    const switchInput = document.getElementById("showAttendeeCountSwitch");
    if (switchInput) {
        switchInput.addEventListener("change", async () => {
            const csrftoken = getCookie("csrftoken");
            const body = new URLSearchParams({
                show_attendee_count: switchInput.checked ? "true" : "false",
            });

            try {
                const response = await fetch(window.location.pathname, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": csrftoken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body,
                });
                const data = await response.json();
                if (!data.success) {
                    switchInput.checked = !switchInput.checked;
                    alert("No se pudo actualizar la configuración.");
                }
            } catch (error) {
                switchInput.checked = !switchInput.checked;
                console.error("Error guardando configuración:", error);
                alert("Error al guardar la configuración.");
            }
        });
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    // Form submission simulation
    const saveBtn = document.querySelector(".btn-primary-custom");
    if (saveBtn) {
        saveBtn.addEventListener("click", () => {
            alert("Configuración guardada correctamente.");
        });
    }

    const discardBtn = document.querySelector(".btn-discard");
    if (discardBtn) {
        discardBtn.addEventListener("click", () => {
            if (confirm("¿Estás seguro de descartar los cambios?")) {
                location.reload();
            }
        });
    }
});
