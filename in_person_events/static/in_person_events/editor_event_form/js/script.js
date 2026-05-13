/* Stratos Event Suite - Interactive Logic */

// Toast notification system
function showToast(message, type = 'error') {
    const existingToast = document.querySelector('.custom-toast');
    if (existingToast) existingToast.remove();

    const toast = document.createElement('div');
    toast.className = `custom-toast toast-notification position-fixed start-50 translate-middle-x`;
    toast.style.cssText = 'min-width: 350px; max-width: 90vw; box-shadow: 0 4px 12px rgba(0,0,0,0.25); font-size: 0.95rem; z-index: 9999; border-radius: 8px; top: 70px;';
    toast.innerHTML = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} d-flex align-items-center justify-content-between p-3 m-0">
            <span>${message}</span>
            <button type="button" class="btn-close ms-3" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 4000);
}

function clearFieldError(field) {
    const errorDiv = field.parentElement.querySelector('.invalid-feedback');
    if (errorDiv) errorDiv.remove();
}

function validateDateInPast(field) {
    const now = new Date();
    const fieldDate = new Date(field.value);
    
    if (fieldDate < now) {
        let errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback d-block';
            field.parentElement.appendChild(errorDiv);
        }
        errorDiv.textContent = 'La fecha no puede ser en el pasado.';
        return false;
    }
    
    clearFieldError(field);
    return true;
}

// Date Validation - Prevent past dates and ensure end_date > start_date
const startDateField = document.querySelector('input[name="start_date"]');
const endDateField = document.querySelector('input[name="end_date"]');

if (startDateField && endDateField) {
    startDateField.addEventListener("change", () => {
        if (startDateField.value) {
            endDateField.setAttribute("min", startDateField.value);
            if (endDateField.value && endDateField.value <= startDateField.value) {
                endDateField.value = "";
            }
        }
        validateDateInPast(startDateField);
    });

    endDateField.addEventListener("change", () => {
        validateDateInPast(endDateField);
    });
}

// Capacity Slider
const capacitySlider = document.getElementById("capacitySlider");
const capacityValue = document.getElementById("capacityValue");

if (capacitySlider && capacityValue) {
    capacityValue.textContent = capacitySlider.value;

    capacitySlider.addEventListener("input", (e) => {
        capacityValue.textContent = e.target.value;
    });
}

// Handle Privacy Selection
const privacyOptions = document.querySelectorAll(".privacy-option");
privacyOptions.forEach((option) => {
    option.addEventListener("click", () => {
        privacyOptions.forEach((opt) => opt.classList.remove("active"));
        option.classList.add("active");
        const radio = option.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;
    });
});

// Ticket Management
const addTicketBtn = document.getElementById("addTicketBtn");
const ticketContainer = document.getElementById("ticketContainer");
const ticketsDataInput = document.getElementById("ticketsData");

function updateTicketsData() {
    if (!ticketContainer || !ticketsDataInput) {
        return;
    }

    const tickets = [];
    const ticketItems = ticketContainer.querySelectorAll(".ticket-item");

    ticketItems.forEach((item) => {
        const nameInput = item.querySelector('input[type="text"]');
        const priceInput = item.querySelector('input[type="number"]');

        if (nameInput && priceInput) {
            const name = nameInput.value.trim();
            let priceValue = priceInput.value;
            let price = parseFloat(priceValue) || 0;
            
            if (price < 0) {
                price = 0;
                priceInput.value = 0;
            }

            if (name && price >= 0) {
                tickets.push({
                    name: name,
                    price: price,
                });
            }
        }
    });

    ticketsDataInput.value = JSON.stringify(tickets);
}

function createTicketItem(ticketId, name = "", price = 0) {
    return `
        <div class="ticket-item" id="ticket-${ticketId}">
            <div class="ticket-input">
                <label class="form-label mb-1">Nombre del Ticket</label>
                <input
                    type="text"
                    class="form-control border-0 bg-transparent p-0 fw-medium shadow-none"
                    placeholder="Nombre del ticket"
                    value="${name}"
                />
            </div>
            <div class="ticket-price">
                <label class="form-label mb-1">Precio</label>
                <div class="d-flex align-items-center">
                    <input
                        type="number"
                        class="form-control border-0 bg-transparent p-0 fw-bold shadow-none"
                        value="${price}"
                        min="0"
                        step="0.01"
                    />
                </div>
            </div>
            <button type="button" class="btn text-danger p-2 remove-ticket" data-ticket-id="${ticketId}">
                <span class="material-symbols-outlined">delete</span>
            </button>
        </div>
    `;
}

function initializeTicketItems() {
    if (!ticketContainer || !ticketsDataInput) {
        return;
    }

    try {
        const jsonValue = ticketsDataInput.value || "[]";
        const tickets = JSON.parse(jsonValue);

        if (!Array.isArray(tickets)) {
            return;
        }

        ticketContainer.innerHTML = "";

        if (tickets.length === 0) {
            // No hay tickets
        } else {
            tickets.forEach((ticket) => {
                const ticketId = Date.now() + Math.random();
                ticketContainer.insertAdjacentHTML(
                    "beforeend",
                    createTicketItem(ticketId, ticket.name, ticket.price),
                );
            });
        }
        updateTicketsData();
    } catch (error) {
        // Error al inicializar tickets
    }
}

if (addTicketBtn && ticketContainer) {
    addTicketBtn.addEventListener("click", () => {
        const ticketId = Date.now();
        ticketContainer.insertAdjacentHTML(
            "beforeend",
            createTicketItem(ticketId),
        );
        updateTicketsData();
    });
}

if (ticketContainer) {
    ticketContainer.addEventListener("click", (e) => {
        const removeButton = e.target.closest(".remove-ticket");
        if (!removeButton) return;

        const ticketElement = removeButton.closest(".ticket-item");
        if (ticketElement) {
            ticketElement.remove();
            updateTicketsData();
        }
    });

    ticketContainer.addEventListener("input", updateTicketsData);
}

initializeTicketItems();

// Handle Form Submission
const eventForm = document.getElementById("eventForm");
if (eventForm) {
    eventForm.addEventListener("submit", (e) => {
        updateTicketsData();
        
        // Validate dates on submit
        let isValid = true;
        if (startDateField && !validateDateInPast(startDateField)) {
            isValid = false;
        }
        if (endDateField && !validateDateInPast(endDateField)) {
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
            showToast('Por favor corrige los errores antes de enviar el formulario.');
        }
    });
}

// Image Upload Preview
const evImageInput = document.getElementById("evImageInput");
const evDropZoneContent = document.getElementById("evDropZoneContent");
const evPreviewContainer = document.getElementById("evPreviewContainer");
const evImagePreview = document.getElementById("evImagePreview");
const evRemoveImage = document.getElementById("evRemoveImage");

function showPreview(src) {
    if (evDropZoneContent && evPreviewContainer && evImagePreview) {
        evDropZoneContent.classList.add("d-none");
        evPreviewContainer.classList.remove("d-none");
        evImagePreview.src = src;
    }
}

function hidePreview() {
    if (evDropZoneContent && evPreviewContainer) {
        evDropZoneContent.classList.remove("d-none");
        evPreviewContainer.classList.add("d-none");
        if (evImagePreview) evImagePreview.src = "";
    }
    if (evImageInput) evImageInput.value = "";
    // Set the remove_image flag
    const removeImageInput = document.getElementById('removeImage');
    if (removeImageInput) removeImageInput.value = 'true';
}

if (evImageInput) {
    evImageInput.addEventListener("change", function(e) {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(evt) { showPreview(evt.target.result); };
            reader.readAsDataURL(this.files[0]);
            // Reset remove flag when new image is selected
            const removeImageInput = document.getElementById('removeImage');
            if (removeImageInput) removeImageInput.value = 'false';
        }
    });
}

if (evRemoveImage) {
    evRemoveImage.addEventListener("click", function(e) {
        e.preventDefault();
        hidePreview();
    });
}
