document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM loaded, checking Bootstrap...");
    console.log("Bootstrap available:", typeof bootstrap);

    // Verificar si hay parámetro para abrir modal
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("modal") === "create") {
        const modal = new bootstrap.Modal(
            document.getElementById("createActivityModal"),
        );
        modal.show();
    }

    // Manejar envío del formulario del modal
    const form = document.querySelector("#createActivityForm");
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(form);

            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": document.querySelector(
                        "[name=csrfmiddlewaretoken]",
                    ).value,
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        // Cerrar modal y recargar página
                        const modal = bootstrap.Modal.getInstance(
                            document.getElementById("createActivityModal"),
                        );
                        modal.hide();
                        location.reload();
                    } else {
                        // Mostrar errores en el modal
                        const modalBody = document.querySelector(
                            "#createActivityModal .modal-body",
                        );
                        let errorHtml =
                            '<div class="alert alert-danger alert-dismissible fade show" role="alert">';
                        errorHtml +=
                            "<strong>Error al crear la actividad:</strong><br>";

                        if (data.errors) {
                            for (const [field, errors] of Object.entries(
                                data.errors,
                            )) {
                                errorHtml += `${field}: ${errors.join(", ")}<br>`;
                            }
                        } else {
                            errorHtml += "Ha ocurrido un error inesperado.";
                        }

                        errorHtml +=
                            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';

                        // Insertar errores al inicio del modal body
                        modalBody.insertAdjacentHTML("afterbegin", errorHtml);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("Error al procesar la solicitud");
                });
        });
    }

    function updateSpeakerEmailField(selectId, hiddenId) {
        const selectEl = document.getElementById(selectId);
        const hiddenInput = document.getElementById(hiddenId);
        if (!selectEl || !hiddenInput) return;

        const updateValue = () => {
            const option = selectEl.selectedOptions[0];
            hiddenInput.value = option?.dataset?.email || "";
        };

        selectEl.addEventListener("change", updateValue);
        updateValue();
    }

    updateSpeakerEmailField("createSpeakerName", "createSpeakerEmail");
    updateSpeakerEmailField("editSpeakerName", "editSpeakerEmail");

    // Código para otros modales
    const editModal = document.getElementById("editActivityModal");
    const viewModal = document.getElementById("viewActivityModal");
    const deleteModal = document.getElementById("deleteActivityModal");

    const baseUrl =
        window.activitiesBaseUrl || `/agenda/activities/${window.eventId}/`;

    // Edit Modal - populate form
    if (editModal) {
        editModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const activityId = button.getAttribute("data-activity-id");
            const activity = window.activitiesData.find(
                (a) => a.id == activityId,
            );

            if (activity) {
                document.getElementById("editActivityId").value = activity.id;
                document.getElementById("editTitle").value = activity.title;
                document.getElementById("editDescription").value =
                    activity.description || "";
                document.getElementById("editStartTime").value =
                    activity.start_time;
                document.getElementById("editEndTime").value =
                    activity.end_time;
                document.getElementById("editLocation").value =
                    activity.location;
                document.getElementById("editSpeakerName").value =
                    activity.speaker_name || "";

                const form = document.getElementById("editActivityForm");
                form.action = `${baseUrl}edit/${activity.id}/`;
            }
        });
    }

    // View Modal - populate data
    if (viewModal) {
        viewModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const activityId = button.getAttribute("data-activity-id");
            const activity = window.activitiesData.find(
                (a) => a.id == activityId,
            );

            if (activity) {
                // Título
                document.getElementById("viewActivityTitle").textContent =
                    activity.title;

                // Estado
                const statusMap = {
                    programada: { text: "Programada", class: "bg-primary" },
                    en_curso: {
                        text: "En Curso",
                        class: "bg-warning text-dark",
                    },
                    completada: { text: "Completada", class: "bg-success" },
                    cancelada: { text: "Cancelada", class: "bg-danger" },
                };
                const statusInfo = statusMap[activity.status] || {
                    text: activity.status,
                    class: "bg-secondary",
                };
                const statusBadge =
                    document.getElementById("viewActivityStatus");
                statusBadge.textContent = statusInfo.text;
                statusBadge.className = `badge ${statusInfo.class} mb-3`;

                // Descripción
                document.getElementById("viewActivityDescription").textContent =
                    activity.description || "Sin descripción";

                // Horario
                const startDate = new Date(activity.start_time);
                const endDate = new Date(activity.end_time);
                document.getElementById("viewActivityStartDate").textContent =
                    startDate.toLocaleDateString("es-ES", {
                        day: "numeric",
                        month: "long",
                    });
                document.getElementById("viewActivityStartTime").textContent =
                    startDate.toLocaleTimeString("es-ES", {
                        hour: "numeric",
                        minute: "2-digit",
                    });
                document.getElementById("viewActivityEndDate").textContent =
                    endDate.toLocaleDateString("es-ES", {
                        day: "numeric",
                        month: "long",
                    });
                document.getElementById("viewActivityEndTime").textContent =
                    endDate.toLocaleTimeString("es-ES", {
                        hour: "numeric",
                        minute: "2-digit",
                    });

                // Duración
                const durationMs = endDate - startDate;
                const durationMins = Math.round(durationMs / 60000);
                let durationText = "";
                if (durationMins >= 60) {
                    const hours = Math.floor(durationMins / 60);
                    const mins = durationMins % 60;
                    durationText =
                        mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
                } else {
                    durationText = `${durationMins}min`;
                }
                document.getElementById("viewActivityDuration").textContent =
                    `Duración: ${durationText}`;

                // Ubicación
                document.getElementById("viewActivityLocation").textContent =
                    activity.location || "No asignada";

                // Ponente
                const speakerEmail = activity.speaker_email || "";
                const speakerProfile =
                    window.ponenteProfiles &&
                    window.ponenteProfiles[speakerEmail];

                if (activity.speaker_name) {
                    document.getElementById("viewSpeakerName").textContent =
                        activity.speaker_name;
                    document.getElementById("viewSpeakerEmail").textContent =
                        speakerEmail || "Sin email";
                    document.getElementById("viewSpeakerPhone").textContent =
                        (speakerProfile && speakerProfile.phone) ||
                        "Sin teléfono";
                    document.getElementById("viewSpeakerBio").textContent =
                        (speakerProfile && speakerProfile.bio) ||
                        "Sin biografía";
                    document.getElementById("viewSpeakerWebsite").textContent =
                        (speakerProfile && speakerProfile.website) ||
                        "No disponible";
                    document.getElementById("viewSpeakerTwitter").textContent =
                        (speakerProfile && speakerProfile.twitter) ||
                        "No disponible";
                    document.getElementById(
                        "viewSpeakerInstagram",
                    ).textContent =
                        (speakerProfile && speakerProfile.instagram) ||
                        "No disponible";
                    document.getElementById("viewSpeakerLinkedin").textContent =
                        (speakerProfile && speakerProfile.linkedin) ||
                        "No disponible";
                } else {
                    document.getElementById("viewSpeakerName").textContent =
                        "No asignado";
                    document.getElementById("viewSpeakerEmail").textContent =
                        "-";
                    document.getElementById("viewSpeakerPhone").textContent =
                        "-";
                    document.getElementById("viewSpeakerBio").textContent = "-";
                    document.getElementById("viewSpeakerWebsite").textContent =
                        "-";
                    document.getElementById("viewSpeakerTwitter").textContent =
                        "-";
                    document.getElementById(
                        "viewSpeakerInstagram",
                    ).textContent = "-";
                    document.getElementById("viewSpeakerLinkedin").textContent =
                        "-";
                }
            }
        });
    }

    // Delete Modal - confirmation
    // Delete Modal - confirmation
    if (deleteModal) {
        deleteModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const activityId =
                button.getAttribute("data-bs-id") ||
                button.getAttribute("data-activity-id");

            const activity = window.activitiesData.find(
                (a) => a.id == activityId,
            );

            if (activity) {
                document.getElementById("deleteActivityTitle").textContent =
                    activity.title;
                document.getElementById("deleteActivityId").value = activity.id;

                const deleteForm =
                    document.getElementById("deleteActivityForm");

                // CAMBIO EXACTO: Usar la variable global definida en el HTML
                const baseUrl = window.activitiesBaseUrl;
                deleteForm.action = `${baseUrl}delete/${activity.id}/`;
            }
        });
    }

    // Cancel Modal - confirmation
    const cancelModal = document.getElementById("cancelActivityModal");
    if (cancelModal) {
        cancelModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const activityId = button.getAttribute("data-activity-id");
            const activity = window.activitiesData.find(
                (a) => a.id == activityId,
            );

            if (activity) {
                document.getElementById("cancelActivityTitle").textContent =
                    activity.title;
                document.getElementById("cancelActivityId").value = activity.id;

                const cancelForm =
                    document.getElementById("cancelActivityForm");
                const baseUrl = window.activitiesBaseUrl;
                cancelForm.action = `${baseUrl}cancel/${activity.id}/`;
                console.log("Cancel URL:", cancelForm.action);
            }
        });

        // Intercept submit to show loading state
        const cancelForm = document.getElementById("cancelActivityForm");
        if (cancelForm) {
            cancelForm.addEventListener("submit", function (e) {
                console.log("Cancel form submitted to:", this.action);
            });
        }
    }

    // No se intercepta el submit de eliminación para que el formulario
    // se envíe de forma normal y redirija a la vista de actividades.

    // Initialize Lucide icons
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }
});
