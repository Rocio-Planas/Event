document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("modal") === "create") {
        const modal = new bootstrap.Modal(
            document.getElementById("createActivityModal"),
        );
        modal.show();
    }

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
                        const modal = bootstrap.Modal.getInstance(
                            document.getElementById("createActivityModal"),
                        );
                        modal.hide();
                        location.reload();
                    } else {
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

                        modalBody.insertAdjacentHTML("afterbegin", errorHtml);
                    }
                })
                .catch((error) => {
                    showToast("Error al procesar la solicitud", "error");
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

    // Limpiar errores al abrir modal de crear actividad
    const createModal = document.getElementById("createActivityModal");
    if (createModal) {
        createModal.addEventListener("show.bs.modal", function() {
            const startError = document.getElementById("createStartTimeError");
            const startInput = createModal.querySelector('input[name="start_time"]');
            const endInput = createModal.querySelector('input[name="end_time"]');
            if (startError) startError.remove();
            if (startInput) startInput.classList.remove("is-invalid");
            if (endInput) endInput.classList.remove("is-invalid");
            const submitBtn = createModal.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = false;
        });
    }

    // Validación de fechas para crear actividad
    const createStartTime = document.getElementById("createActivityForm")?.querySelector('input[name="start_time"]');
    const createEndTime = document.getElementById("createActivityForm")?.querySelector('input[name="end_time"]');
    const createSubmitBtn = document.getElementById("createActivityForm")?.querySelector('button[type="submit"]');

    function validateCreateDates() {
        if (!createStartTime || !createEndTime) return true;
        
        const startVal = createStartTime.value;
        const endVal = createEndTime.value;
        
        let startError = document.getElementById("createStartTimeError");
        
        if (startVal && endVal) {
            const startDate = new Date(startVal);
            const endDate = new Date(endVal);
            
            if (endDate <= startDate) {
                if (!startError) {
                    startError = document.createElement("div");
                    startError.id = "createStartTimeError";
                    startError.className = "text-danger small mt-1";
                    createStartTime.parentNode.appendChild(startError);
                }
                startError.textContent = "La hora de inicio debe ser anterior a la de finalización";
                createStartTime.classList.add("is-invalid");
                createEndTime.classList.add("is-invalid");
                if (createSubmitBtn) createSubmitBtn.disabled = true;
                return false;
            }
        }
        
        if (startError) {
            startError.remove();
            createStartTime.classList.remove("is-invalid");
        }
        createEndTime.classList.remove("is-invalid");
        if (createSubmitBtn) createSubmitBtn.disabled = false;
        return true;
    }

    if (createStartTime) createStartTime.addEventListener("change", validateCreateDates);
    if (createEndTime) createEndTime.addEventListener("change", validateCreateDates);

    // Validación de fechas para editar actividad
    const editStartTime = document.getElementById("editActivityForm")?.querySelector('input[name="start_time"]');
    const editEndTime = document.getElementById("editActivityForm")?.querySelector('input[name="end_time"]');
    const editSubmitBtn = document.getElementById("editActivityForm")?.querySelector('button[type="submit"]');

    function validateEditDates() {
        if (!editStartTime || !editEndTime) return true;
        
        const startVal = editStartTime.value;
        const endVal = editEndTime.value;
        
        let startError = document.getElementById("editStartTimeError");
        
        if (startVal && endVal) {
            const startDate = new Date(startVal);
            const endDate = new Date(endVal);
            
            if (endDate <= startDate) {
                if (!startError) {
                    startError = document.createElement("div");
                    startError.id = "editStartTimeError";
                    startError.className = "text-danger small mt-1";
                    editStartTime.parentNode.appendChild(startError);
                }
                startError.textContent = "La hora de inicio debe ser anterior a la de finalización";
                editStartTime.classList.add("is-invalid");
                editEndTime.classList.add("is-invalid");
                if (editSubmitBtn) editSubmitBtn.disabled = true;
                return false;
            }
        }
        
        if (startError) {
            startError.remove();
            editStartTime.classList.remove("is-invalid");
        }
        editEndTime.classList.remove("is-invalid");
        if (editSubmitBtn) editSubmitBtn.disabled = false;
        return true;
    }

    if (editStartTime) editStartTime.addEventListener("change", validateEditDates);
    if (editEndTime) editEndTime.addEventListener("change", validateEditDates);

    const editModal = document.getElementById("editActivityModal");
    const viewModal = document.getElementById("viewActivityModal");
    const deleteModal = document.getElementById("deleteActivityModal");

    const baseUrl =
        window.activitiesBaseUrl || `/agenda/activities/${window.eventId}/`;

    if (editModal) {
        editModal.addEventListener("show.bs.modal", function (event) {
            // Limpiar errores de validación de fechas
            const startError = document.getElementById("editStartTimeError");
            const startInput = editModal.querySelector('input[name="start_time"]');
            const endInput = editModal.querySelector('input[name="end_time"]');
            if (startError) startError.remove();
            if (startInput) startInput.classList.remove("is-invalid");
            if (endInput) endInput.classList.remove("is-invalid");
            const submitBtn = editModal.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = false;

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

    if (viewModal) {
        viewModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget;
            const activityId = button.getAttribute("data-activity-id");
            const activity = window.activitiesData.find(
                (a) => a.id == activityId,
            );

            if (activity) {
                document.getElementById("viewActivityTitle").textContent =
                    activity.title;

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

                document.getElementById("viewActivityDescription").textContent =
                    activity.description || "Sin descripción";

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

                document.getElementById("viewActivityLocation").textContent =
                    activity.location || "No asignada";

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

                const baseUrl = window.activitiesBaseUrl;
                deleteForm.action = `${baseUrl}delete/${activity.id}/`;
            }
        });
    }

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
            }
        });
    }

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }
});