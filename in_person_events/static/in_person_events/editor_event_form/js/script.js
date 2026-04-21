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
    if (!ticketContainer || !ticketsDataInput) return;

    const tickets = [];
    const ticketItems = ticketContainer.querySelectorAll(".ticket-item");

    ticketItems.forEach((item) => {
        const nameInput = item.querySelector('input[type="text"]');
        const priceInput = item.querySelector('input[type="number"]');

        if (nameInput && priceInput) {
            const name = nameInput.value.trim();
            const price = parseFloat(priceInput.value) || 0;

            if (name) {
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
                    <span class="fw-bold me-1">$</span>
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

// Handle Form Submission
const eventForm = document.getElementById("eventForm");
if (eventForm) {
    eventForm.addEventListener("submit", (e) => {
        updateTicketsData();
    });
}
