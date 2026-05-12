var currentStandId = parseInt(
    document.querySelector("[data-stand-id]").getAttribute("data-stand-id"),
);

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
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

function addSelectedStaff() {
    var selectedCheckboxes = document.querySelectorAll(
        ".staff-checkbox:checked",
    );
    var selectedUsers = Array.from(selectedCheckboxes).map(function (cb) {
        return { user_id: cb.value, role: cb.dataset.role };
    });

    if (selectedUsers.length === 0) return;

    var btn = document.getElementById("confirmAddStaffBtn");
    btn.disabled = true;
    btn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-1"></span> Añadiendo...';

    fetch("/stands/api/" + currentStandId + "/add-staff/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ users: selectedUsers }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || "Error desconocido");
                btn.disabled = false;
                btn.textContent = "Aceptar";
            }
        })
        .catch(function (error) {
            alert("Error de conexión");
            btn.disabled = false;
            btn.textContent = "Aceptar";
        });
}

function openNotificationModal(userId, userName) {
    document.getElementById("notificationUserId").value = userId;
    document.getElementById("notificationUserName").textContent = userName;
    var modal = new bootstrap.Modal(
        document.getElementById("notificationModal"),
    );
    modal.show();
}

function sendNotification() {
    var userId = document.getElementById("notificationUserId").value;
    var title = document.getElementById("notificationTitle").value;
    var message = document.getElementById("notificationMessage").value;

    if (!title || !message) {
        alert("Completa todos los campos");
        return;
    }

    var btn = document.getElementById("sendNotificationBtn");
    btn.disabled = true;
    btn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-1"></span> Enviando...';

    fetch("/comunicacion/send/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            user_id: userId,
            title: title,
            message: message,
        }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                alert("Notificación enviada");
                bootstrap.Modal.getInstance(
                    document.getElementById("notificationModal"),
                ).hide();
                document.getElementById("notificationTitle").value = "";
                document.getElementById("notificationMessage").value = "";
            } else {
                alert(data.error || "Error al enviar");
            }
            btn.disabled = false;
            btn.textContent = "Enviar";
        })
        .catch(function (error) {
            alert("Error de conexión");
            btn.disabled = false;
            btn.textContent = "Enviar";
        });
}

document.addEventListener("change", function (e) {
    if (e.target.classList.contains("staff-checkbox")) {
        var anyChecked =
            document.querySelectorAll(".staff-checkbox:checked").length > 0;
        document.getElementById("confirmAddStaffBtn").disabled = !anyChecked;
    }
    if (e.target.classList.contains("activity-checkbox")) {
        var anyChecked =
            document.querySelectorAll(".activity-checkbox:checked").length > 0;
        document.getElementById("confirmAssignActivityBtn").disabled =
            !anyChecked;
    }
    if (e.target.classList.contains("resource-checkbox")) {
        var anyChecked =
            document.querySelectorAll(".resource-checkbox:checked").length > 0;
        document.getElementById("confirmAddBtn").disabled = !anyChecked;
    }
});

function removeStaffFromStand(userId, userName) {
    document.getElementById("removeStaffUserId").value = userId;
    document.getElementById("removeStaffUserName").textContent = userName;
    var modal = new bootstrap.Modal(
        document.getElementById("removeStaffModal"),
    );
    modal.show();
}

function confirmRemoveStaff() {
    var userId = document.getElementById("removeStaffUserId").value;

    fetch("/stands/api/" + currentStandId + "/remove-staff/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ user_id: userId }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                bootstrap.Modal.getInstance(
                    document.getElementById("removeStaffModal"),
                ).hide();
                location.reload();
            } else {
                alert(data.error || "Error al remover");
            }
        })
        .catch(function (error) {
            alert("Error de conexión");
        });
}

function addSelectedActivities() {
    var selectedCheckboxes = document.querySelectorAll(
        ".activity-checkbox:checked",
    );
    var selectedActivities = Array.from(selectedCheckboxes).map(function (cb) {
        return { activity_id: cb.value };
    });

    if (selectedActivities.length === 0) return;

    var btn = document.getElementById("confirmAssignActivityBtn");
    btn.disabled = true;
    btn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-1"></span> Asignando...';

    fetch("/stands/api/" + currentStandId + "/add-activities/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ activities: selectedActivities }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || "Error desconocido");
                btn.disabled = false;
                btn.textContent = "Asignar";
            }
        })
        .catch(function (error) {
            alert("Error de conexión");
            btn.disabled = false;
            btn.textContent = "Asignar";
        });
}

function addSelectedResources() {
    var selectedCheckboxes = document.querySelectorAll(
        ".resource-checkbox:checked",
    );
    var selectedItems = Array.from(selectedCheckboxes).map(function (cb) {
        return cb.value;
    });

    if (selectedItems.length === 0) return;

    var btn = document.getElementById("confirmAddBtn");
    btn.disabled = true;
    btn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-1"></span> Añadiendo...';

    fetch("/stands/api/" + currentStandId + "/add-resources/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ item_ids: selectedItems }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                location.reload();
            } else {
                alert("No se pudieron agregar los recursos");
                btn.disabled = false;
                btn.textContent = "Añadir Seleccionados";
            }
        })
        .catch(function (error) {
            alert("Error de conexión");
            btn.disabled = false;
            btn.textContent = "Añadir Seleccionados";
        });
}

function updateQuantity(assignmentId, delta, maxStock) {
    var currentQtySpan = document.querySelector(
        '[data-assignment-id="' + assignmentId + '"] .assigned-val',
    );
    var currentQty = parseInt(currentQtySpan.textContent);
    var newQty = currentQty + delta;

    if (newQty < 0 || newQty > maxStock) {
        return;
    }

    fetch("/stands/" + currentStandId + "/update-resource/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ assignment_id: assignmentId, quantity: newQty }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                location.reload();
            }
        })
        .catch(function (error) {
            console.error("Error:", error);
        });
}

function openActivityDetails(
    activityId,
    title,
    description,
    startDate,
    endDate,
    duration,
    location,
    speakerName,
    speakerEmail,
    status,
) {
    document.getElementById("detailActivityId").value = activityId;
    document.getElementById("detailActivityTitle").textContent = title;
    document.getElementById("detailActivityDescription").textContent =
        description || "Descripción no disponible";
    document.getElementById("detailActivityTime").textContent =
        "Inicio: " + startDate;
    document.getElementById("detailActivityDate").textContent =
        "Fin: " + endDate;
    document.getElementById("detailActivityDuration").textContent =
        duration + " min";
    document.getElementById("detailActivityLocation").textContent =
        location || "Sin ubicación";

    var statusLabel = "Programada";
    var statusClass = "bg-primary text-white";
    if (status === "en_curso") {
        statusLabel = "En curso";
        statusClass = "bg-warning text-dark";
    } else if (status === "completada") {
        statusLabel = "Completada";
        statusClass = "bg-success text-white";
    } else if (status === "cancelada") {
        statusLabel = "Cancelada";
        statusClass = "bg-danger text-white";
    }
    var statusElement = document.getElementById("detailActivityStatus");
    statusElement.textContent = statusLabel;
    statusElement.className = "badge fw-bold " + statusClass;

    if (speakerName && speakerName !== 'None' && speakerName.trim()) {
        document.getElementById("detailActivitySpeaker").textContent =
            speakerName;
        document.getElementById("detailActivitySpeakerEmail").textContent =
            speakerEmail && speakerEmail !== 'None' ? speakerEmail : "";
    } else {
        document.getElementById("detailActivitySpeaker").textContent =
            "Sin asignar";
        document.getElementById("detailActivitySpeakerEmail").textContent = "";
    }

    if (!location) {
        document.getElementById("detailActivityLocation").textContent =
            "No asignada";
    }

    var modal = new bootstrap.Modal(
        document.getElementById("activityDetailsModal"),
    );
    modal.show();
}

function openEditResourceModal(
    assignmentId,
    itemName,
    itemCategory,
    currentDetails,
    currentRequired,
) {
    document.getElementById("editAssignmentId").value = assignmentId;
    document.getElementById("editResourceName").textContent =
        itemName + " (" + itemCategory + ")";
    document.getElementById("editReqInput").value = currentDetails || "";
    document.getElementById("editRequiredInput").value = currentRequired || 0;
    var modal = new bootstrap.Modal(
        document.getElementById("editResourceModal"),
    );
    modal.show();
}

function saveResourceEdit() {
    var assignmentId = document.getElementById("editAssignmentId").value;
    var details = document.getElementById("editReqInput").value;
    var requiredQty = document.getElementById("editRequiredInput").value;

    if (details.length > 100) {
        alert("El texto no puede exceder 100 caracteres");
        return;
    }

    var btn = document.getElementById("saveResourceEditBtn");
    btn.disabled = true;
    btn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-1"></span> Guardando...';

    fetch("/stands/" + currentStandId + "/update-resource/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            assignment_id: assignmentId,
            details: details,
            required_quantity: parseInt(requiredQty) || 0,
        }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || "Error al guardar");
            }
        })
        .catch(function (error) {
            console.error("Error:", error);
        })
        .finally(function () {
            btn.disabled = false;
            btn.textContent = "Guardar Cambios";
        });
}

function removeResource(assignmentId) {
    if (
        !confirm(
            "¿Quitar este recurso del stand? La cantidad se liberará al stock available.",
        )
    ) {
        return;
    }

    fetch("/stands/" + currentStandId + "/delete-resource/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ assignment_id: assignmentId }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || "Error al eliminar");
            }
        })
        .catch(function (error) {
            console.error("Error:", error);
        });
}

function adjustQuantity(assignmentId, delta, button) {
    var td = button.closest("td");
    var span = td.querySelector("span");
    var currentText = span.textContent.trim();
    var parts = currentText.split(" / ");
    var currentQty = parseInt(parts[0]) || 0;
    var requiredQty = parseInt(parts[1]) || 0;

    var newQty = Math.max(0, currentQty + delta); // Don't go below 0

    fetch("/stands/" + currentStandId + "/update-resource/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ assignment_id: assignmentId, quantity: newQty }),
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                // Update the display
                span.textContent = newQty + " / " + requiredQty;
            } else {
                console.warn("No se pudo actualizar cantidad:", data.error);
            }
        })
        .catch(function (error) {
            console.error("Error:", error);
            alert("Error al actualizar cantidad: " + error.message);
        });
}

function openMoveModal() {
    var activityId = document.getElementById("detailActivityId").value;
    if (!activityId) {
        alert("Selecciona una actividad primero");
        return;
    }
    var detailsModal = bootstrap.Modal.getInstance(
        document.getElementById("activityDetailsModal"),
    );
    if (detailsModal) {
        detailsModal.hide();
    }
    var moveModal = new bootstrap.Modal(
        document.getElementById("moveActivityModal"),
    );
    moveModal.show();
}

function moveActivityToStand() {
    var activityId = document.getElementById("detailActivityId").value;
    var targetStandId = document.getElementById("moveStandSelect").value;

    if (!targetStandId) {
        alert("Selecciona un stand destino");
        return;
    }

    var btn = document.querySelector("#moveActivityModal .btn-signature");
    btn.disabled = true;
    btn.textContent = "Moviendo...";

    fetch("/stands/api/" + currentStandId + "/move-activity/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            activity_id: activityId,
            target_stand_id: targetStandId,
        }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                var moveModal = bootstrap.Modal.getInstance(
                    document.getElementById("moveActivityModal"),
                );
                if (moveModal) moveModal.hide();
                var detailsModal = bootstrap.Modal.getInstance(
                    document.getElementById("activityDetailsModal"),
                );
                if (detailsModal) detailsModal.hide();
                removeActivityCard(activityId);
            } else {
                alert(data.error || "Error al mover la actividad");
            }
        })
        .catch(function (error) {
            alert("Error de conexión");
        })
        .finally(function () {
            btn.disabled = false;
            btn.textContent = "Mover";
        });
}

function deleteActivityFromStand() {
    var activityId = document.getElementById("detailActivityId").value;
    if (!activityId) return;

    if (
        !confirm(
            "¿Deseas quitar esta actividad del stand y dejar su zona como no asignada?",
        )
    ) {
        return;
    }

    var btn = document.getElementById("deleteActivityBtn");
    btn.disabled = true;
    btn.textContent = "Quitando...";

    fetch("/stands/api/" + currentStandId + "/remove-activity/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ activity_id: activityId }),
    })
        .then(function (response) {
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            return response.json();
        })
        .then(function (data) {
            if (data.success) {
                var detailsModal = bootstrap.Modal.getInstance(
                    document.getElementById("activityDetailsModal"),
                );
                if (detailsModal) detailsModal.hide();
                removeActivityCard(activityId);
            } else {
                alert(data.error || "Error al quitar la actividad del stand");
            }
        })
        .catch(function (error) {
            alert("Error de conexión");
        })
        .finally(function () {
            btn.disabled = false;
            btn.textContent = "Quitar";
        });
}

function removeActivityCard(activityId) {
    var card = document.querySelector(
        '[data-activity-id="' + activityId + '"]',
    );
    if (card) {
        card.remove();
    }
}

function filterActivities() {
    var searchInput = document.getElementById("searchActivities");
    var filter = searchInput.value.toLowerCase();
    var activityCards = document.querySelectorAll(".activity-card");

    activityCards.forEach(function (card) {
        var title = card.getAttribute("data-title") || "";
        var titleLower = title.toLowerCase();

        if (titleLower.indexOf(filter) !== -1) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".modal").forEach(function (modal) {
        if (!modal.hasAttribute("inert")) {
            modal.setAttribute("inert", "");
        }

        modal.addEventListener("shown.bs.modal", function () {
            modal.removeAttribute("inert");
        });

        modal.addEventListener("hidden.bs.modal", function () {
            if (modal.contains(document.activeElement)) {
                document.activeElement.blur();
            }
            modal.setAttribute("inert", "");
        });
    });
});
