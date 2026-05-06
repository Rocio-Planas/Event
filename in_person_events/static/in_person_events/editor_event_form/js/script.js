/* Stratos Event Suite - Interactive Logic */

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
}

if (evImageInput) {
    evImageInput.addEventListener("change", function(e) {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function(evt) { showPreview(evt.target.result); };
            reader.readAsDataURL(this.files[0]);
        }
    });
}

if (evRemoveImage) {
    evRemoveImage.addEventListener("click", function(e) {
        e.preventDefault();
        hidePreview();
    });
}
