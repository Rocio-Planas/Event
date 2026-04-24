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
                document.getElementById("editSpeakerEmail").value =
                    activity.speaker_email || "";
                document.getElementById("editStatus").value = activity.status;

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
                document.getElementById("viewTitle").textContent =
                    activity.title;
                document.getElementById("viewDescription").textContent =
                    activity.description || "Sin descripción";

                const startDate = new Date(activity.start_time);
                const endDate = new Date(activity.end_time);
                document.getElementById("viewStartTime").textContent =
                    startDate.toLocaleString("es-ES");
                document.getElementById("viewEndTime").textContent =
                    endDate.toLocaleString("es-ES");

                document.getElementById("viewLocation").textContent =
                    activity.location;
                document.getElementById("viewSpeaker").innerHTML =
                    activity.speaker_name
                        ? `${activity.speaker_name}<br><small class="text-muted">${activity.speaker_email}</small>`
                        : '<span class="text-muted">-</span>';

                const statusEl = document.getElementById("viewStatus");
                const statusMap = {
                    programada:
                        '<span class="badge bg-primary">Programada</span>',
                    en_curso:
                        '<span class="badge bg-warning text-dark">En Curso</span>',
                    completada:
                        '<span class="badge bg-success">Completada</span>',
                    cancelada: '<span class="badge bg-danger">Cancelada</span>',
                };
                statusEl.innerHTML =
                    statusMap[activity.status] || activity.status;
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
                (a) => a.id == activityId
            );

            if (activity) {
                document.getElementById("deleteActivityTitle").textContent = activity.title;
                document.getElementById("deleteActivityId").value = activity.id;

                const deleteForm = document.getElementById("deleteActivityForm");
                
                // CAMBIO EXACTO: Usar la variable global definida en el HTML
                const baseUrl = window.activitiesBaseUrl; 
                deleteForm.action = `${baseUrl}delete/${activity.id}/`;
            }
        });
    }

    // No se intercepta el submit de eliminación para que el formulario
    // se envíe de forma normal y redirija a la vista de actividades.

    // Initialize Lucide icons
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }
});
