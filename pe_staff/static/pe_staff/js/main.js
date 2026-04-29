// Datos del contexto de Django
let membersData = window.membersData || [];
let invitationsData = window.invitationsData || [];
let eventId = window.eventId || null;

// Mostrar/ocultar selector de rol según tipo de usuario
document.getElementById("userType")?.addEventListener("change", function () {
    const roleDiv = document.getElementById("roleSelectDiv");
    const roleSelect = document.getElementById("inviteRole");

    if (this.value === "staff") {
        roleDiv.style.display = "block";
        roleSelect.required = true;
    } else {
        roleDiv.style.display = "none";
        roleSelect.required = false;
        roleSelect.value = "";
    }
});

// Formulario de invitación
document
    .getElementById("inviteForm")
    ?.addEventListener("submit", async function (e) {
        e.preventDefault();

        const email = document.getElementById("inviteEmail").value.trim();
        const userType = document.getElementById("userType").value;
        const role = document.getElementById("inviteRole").value;

        if (!email) {
            alert("Por favor ingresa un correo electrónico");
            return;
        }

        if (userType === "staff" && !role) {
            alert("Por favor selecciona un rol para el staff");
            return;
        }

        try {
            const response = await fetch(`/equipo/staff/${eventId}/invite/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({
                    email: email,
                    user_type: userType,
                    role: role,
                }),
            });

            const data = await response.json();

            if (data.success) {
                alert("¡Invitación enviada con éxito!");
                // Cerrar modal y recargar
                const modal = bootstrap.Modal.getInstance(
                    document.getElementById("inviteStaffModal"),
                );
                modal.hide();
                window.location.reload();
            } else {
                alert(data.error || "Error al enviar invitación");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error al enviar invitación");
        }
    });

// Formulario de asignar zona
document
    .getElementById("assignZoneForm")
    ?.addEventListener("submit", async function (e) {
        e.preventDefault();

        const memberId = document.getElementById("memberId").value;
        const zone = document.getElementById("zoneName").value.trim();

        if (!memberId || !zone) {
            alert("Datos incompletos");
            return;
        }

        try {
            const response = await fetch(
                `/equipo/staff/${eventId}/assign-zone/${memberId}/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ zone: zone }),
                },
            );

            const data = await response.json();

            if (data.success) {
                alert("¡Zona asignada correctamente!");
                window.location.reload();
            } else {
                alert(data.error || "Error al asignar zona");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error al asignar zona");
        }
    });

// Configurar modal de asignar zona
document
    .getElementById("assignZoneModal")
    ?.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const memberId = button?.getAttribute("data-member-id");
        document.getElementById("memberId").value = memberId || "";
    });

// Obtener CSRF Token
function getCSRFToken() {
    const name = "csrftoken";
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1),
                );
                break;
            }
        }
    }
    return cookieValue;
}

// Cancelar invitación pendiente
document.addEventListener("click", async function (event) {
    const button = event.target.closest(".cancel-invitation-btn");
    if (!button) return;

    const invitationId = button.getAttribute("data-invitation-id");
    if (!invitationId) return;

    if (!confirm("¿Deseas cancelar esta invitación pendiente?")) {
        return;
    }

    try {
        const response = await fetch(
            `/equipo/staff/${eventId}/cancel-invitation/${invitationId}/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
            },
        );

        const data = await response.json();
        if (data.success) {
            alert("Invitación cancelada");
            window.location.reload();
        } else {
            alert(data.error || "Error al cancelar la invitación");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error al cancelar la invitación");
    }
});

// Eliminar miembro del equipo
document.addEventListener("click", async function (event) {
    const button = event.target.closest(".remove-member-btn");
    if (!button) return;

    const memberId = button.getAttribute("data-member-id");
    if (!memberId) return;

    if (!confirm("¿Deseas eliminar este miembro del equipo?")) {
        return;
    }

    try {
        const response = await fetch(
            `/equipo/staff/${eventId}/remove-member/${memberId}/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
            },
        );

        const data = await response.json();
        if (data.success) {
            alert("Miembro eliminado");
            window.location.reload();
        } else {
            alert(data.error || "Error al eliminar el miembro");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Error al eliminar el miembro");
    }
});

// Inicializar
document.addEventListener("DOMContentLoaded", function () {
    console.log("Staff management initialized");
});
