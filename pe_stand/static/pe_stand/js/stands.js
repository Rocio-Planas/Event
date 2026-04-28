// Stands Management - JavaScript

document.addEventListener("DOMContentLoaded", function () {
    console.log("Stands JS loaded");
    // Initialize tooltips if Bootstrap tooltips are needed
    initializeTooltips();

    // Setup event listeners
    setupEventListeners();
});

/**
 * Initialize Bootstrap tooltips for stand cards
 */
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(function (element) {
        new bootstrap.Tooltip(element);
    });
}

/**
 * Setup event listeners for stand management
 */
function setupEventListeners() {
    console.log("Setting up event listeners");
    // "Ver Detalles" buttons are now real links, so we do not intercept their clicks here.

    // "Crear Stand" form submission
    const createStandForm = document.getElementById("createStandForm");
    console.log("Create stand form:", createStandForm);
    if (createStandForm) {
        createStandForm.addEventListener("submit", handleCreateStand);
        console.log("Event listener added to form");
    } else {
        console.error("Create stand form not found!");
    }

    // "Asignar Stand" button
    const assignButton = document.querySelector(".btn-premium");
    if (assignButton) {
        assignButton.addEventListener("click", function (e) {
            e.preventDefault();
            showAssignStandModal();
        });
    }
}

/**
 * View stand details
 * @param {string} standTitle - The title of the stand
 */
function viewStandDetails(standTitle) {
    console.log("View details for stand:", standTitle);
    // TODO: Implement modal or redirect to stand detail page
    alert("Showing details for: " + standTitle);
}

/**
 * Handle create stand form submission
 * @param {Event} e - The form submit event
 */
function handleCreateStand(e) {
    console.log("Handle create stand called");
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = {
        name: formData.get("name"),
        location: formData.get("location"),
        capacity: parseInt(formData.get("capacity")),
    };

    // Get event_id from data attribute
    const eventId = document.querySelector("[data-event-id]").dataset.eventId;
    console.log("Event ID:", eventId);

    // Disable submit button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Creando...";

    fetch(`/stands/api/${eventId}/create-stand/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
                ?.value,
        },
        body: JSON.stringify(data),
    })
        .then((response) => response.json())
        .then((result) => {
            if (result.success) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(
                    document.getElementById("createStandModal"),
                );
                modal.hide();

                // Reset form
                e.target.reset();

                // Show success message
                showToast("Stand creado correctamente", "success");

                // Reload page to show new stand
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showToast(result.error || "Error al crear el stand", "error");
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            showToast("Error de conexión", "error");
        })
        .finally(() => {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        });
}

/**
 * Show toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of notification (success, error, warning)
 */
function showToast(message, type = "info") {
    // Create toast element
    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-white bg-${type === "error" ? "danger" : type} border-0`;
    toast.setAttribute("role", "alert");
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    // Add to page
    const container =
        document.querySelector(".container-fluid") || document.body;
    container.appendChild(toast);

    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove after shown
    toast.addEventListener("hidden.bs.toast", () => {
        toast.remove();
    });
}

/**
 * Update stand resource status
 * @param {string} resourceName - Name of the resource
 * @param {number} available - Available quantity
 * @param {number} total - Total quantity
 */
function updateResourceStatus(resourceName, available, total) {
    const percentage = (available / total) * 100;
    let status = "active"; // green

    if (percentage < 50) {
        status = "warning"; // orange
    }
    if (percentage === 0) {
        status = "error"; // red
    }

    console.log(
        `Resource: ${resourceName}, Available: ${available}/${total}, Status: ${status}`,
    );
    // TODO: Implement real-time update of resource indicators
}

// Export functions for external use
window.standsModule = {
    viewStandDetails,
    showAssignStandModal,
    updateResourceStatus,
};
