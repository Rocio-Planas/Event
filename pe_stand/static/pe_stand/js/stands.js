// Stands Management - JavaScript

document.addEventListener("DOMContentLoaded", function () {
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
    // "Ver Detalles" buttons are now real links, so we do not intercept their clicks here.

    // "Crear Stand" form submission
    const createStandForm = document.getElementById("createStandForm");
    if (createStandForm) {
        createStandForm.addEventListener("submit", handleCreateStand);
    }
}

/**
 * View stand details
 * @param {string} standTitle - The title of the stand
 */
function viewStandDetails(standTitle) {
    alert("Showing details for: " + standTitle);
}

/**
 * Handle create stand form submission
 * @param {Event} e - The form submit event
 */
function handleCreateStand(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = {
        name: formData.get("name"),
        location: formData.get("location"),
        capacity: parseInt(formData.get("capacity")),
    };

    // Get event_id from multiple possible sources
    let eventId = null;
    
    // Try data attribute on body or html element
    const bodyElement = document.querySelector("body[data-event-id]");
    if (bodyElement) {
        eventId = bodyElement.dataset.eventId;
    }
    
    // Try specific element
    if (!eventId) {
        const eventIdElement = document.querySelector("[data-event-id]");
        if (eventIdElement) {
            eventId = eventIdElement.dataset.eventId;
        }
    }
    
    // Try URL path
    if (!eventId) {
        const pathMatch = window.location.pathname.match(/\/evento(\d+)\//);
        if (pathMatch) {
            eventId = pathMatch[1];
        }
    }
    
    if (!eventId) {
        showToast("Error: No se pudo obtener el ID del evento", "error");
        return;
    }

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

                // Reload page immediately
                window.location.reload();
            } else {
                showToast(result.error || "Error al crear el stand", "error");
            }
        })
        .catch((error) => {
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
}

// Export functions for external use
window.standsModule = {
    viewStandDetails,
    updateResourceStatus,
};
