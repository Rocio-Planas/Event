/* Stratos Event Suite - Interactive Logic */

console.log("Stratos Event Editor Ready");

// Capacity Slider
const capacitySlider = document.getElementById("capacitySlider");
const capacityValue = document.getElementById("capacityValue");

if (capacitySlider && capacityValue) {
    // Initialize with current value
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
        console.warn(
            "updateTicketsData: ticketContainer o ticketsDataInput no encontrados",
        );
        return;
    }

    const tickets = [];
    const ticketItems = ticketContainer.querySelectorAll(".ticket-item");

    ticketItems.forEach((item) => {
        const nameInput = item.querySelector('input[type="text"]');
        const priceInput = item.querySelector('input[type="number"]');

        if (nameInput && priceInput) {
            const name = nameInput.value.trim();
            const priceValue = priceInput.value;
            const price = parseFloat(priceValue) || 0;

            if (name && price >= 0) {
                tickets.push({
                    name: name,
                    price: price,
                });
            }
        }
    });

    const jsonValue = JSON.stringify(tickets);
    ticketsDataInput.value = jsonValue;
    console.log("Tickets actualizados:", jsonValue);
}

function createTicketItem(ticketId, name = "", price = 0) {
    return `
        <div class="ticket-item d-flex flex-column flex-md-row align-items-center gap-3" id="ticket-${ticketId}">
            <div class="flex-grow-1 w-100">
                <label class="form-label mb-1">Nombre del Ticket</label>
                <input
                    type="text"
                    class="form-control border-0 bg-transparent p-0 fw-medium shadow-none"
                    placeholder="Nombre del ticket"
                    value="${name}"
                />
            </div>
            <div class="w-100 w-md-25">
                <label class="form-label mb-1">Precio</label>
                <div class="d-flex align-items-center">
                    <span class="fw-bold me-1">€</span>
                    <input
                        type="number"
                        class="form-control border-0 bg-transparent p-0 fw-bold shadow-none"
                        value="${price}"
                        min="0"
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
        console.warn("ticketContainer o ticketsDataInput no encontrados");
        return;
    }

    try {
        const jsonValue = ticketsDataInput.value || "[]";
        console.log("JSON value:", jsonValue);
        const tickets = JSON.parse(jsonValue);
        console.log("Parsed tickets:", tickets);

        if (!Array.isArray(tickets)) {
            console.warn("tickets no es un array");
            return;
        }

        ticketContainer.innerHTML = "";

        if (tickets.length === 0) {
            console.log("No hay tickets");
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
        console.error("Error al inicializar tickets desde JSON:", error);
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
updateTicketsData();

// Handle Form Submission
const eventForm = document.getElementById("eventForm");
if (eventForm) {
    eventForm.addEventListener("submit", (e) => {
        updateTicketsData();
    });
}

// Image Upload Preview (Enhanced drag-and-drop)
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
        evImagePreview.src = "";
    }
    if (evImageInput) {
        evImageInput.value = "";
    }
}

if (evImageInput) {
    evImageInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (event) => {
                showPreview(event.target.result);
            };
            reader.readAsDataURL(file);
        }
    });
}

if (evRemoveImage) {
    evRemoveImage.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        hidePreview();
    });
}

// Drag and drop functionality
const evDropZone = document.querySelector(".ev-drop-zone");
if (evDropZone && evImageInput) {
    evDropZone.addEventListener("click", () => {
        evImageInput.click();
    });

    evDropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        evDropZone.classList.add("border-primary");
        evDropZone.classList.add("bg-light");
    });

    evDropZone.addEventListener("dragleave", () => {
        evDropZone.classList.remove("border-primary");
        evDropZone.classList.remove("bg-light");
    });

    evDropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        evDropZone.classList.remove("border-primary");
        evDropZone.classList.remove("bg-light");

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            evImageInput.files = files;
            const changeEvent = new Event("change");
            evImageInput.dispatchEvent(changeEvent);
        }
    });
}
