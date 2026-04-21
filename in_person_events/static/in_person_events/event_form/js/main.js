console.log("[event_form] main.js loaded");
document.addEventListener("DOMContentLoaded", () => {
    // Date Validation - Prevent past dates and ensure end_date > start_date
    const startDateField = document.querySelector('input[name="start_date"]');
    const endDateField = document.querySelector('input[name="end_date"]');

    if (startDateField && endDateField) {
        // Update end_date minimum when start_date changes
        startDateField.addEventListener("change", () => {
            if (startDateField.value) {
                endDateField.setAttribute("min", startDateField.value);
                // If current end_date is before start_date, clear it
                if (
                    endDateField.value &&
                    endDateField.value <= startDateField.value
                ) {
                    endDateField.value = "";
                }
            }
        });
    }

    // Capacity Slider
    const capacitySlider = document.getElementById("capacitySlider");
    const capacityValue = document.getElementById("capacityValue");

    if (capacitySlider && capacityValue) {
        capacitySlider.addEventListener("input", (e) => {
            capacityValue.textContent = e.target.value;
        });
    }

    // Visibility Toggles
    const publicCard = document.getElementById("publicVisibility");
    const privateCard = document.getElementById("privateVisibility");
    const publicRadio = publicCard
        ? publicCard.querySelector('input[type="radio"]')
        : null;
    const privateRadio = privateCard
        ? privateCard.querySelector('input[type="radio"]')
        : null;

    if (publicCard) {
        publicCard.addEventListener("click", () => {
            publicCard.classList.add("active");
            privateCard.classList.remove("active");
            if (publicRadio) publicRadio.checked = true;
        });
    }

    if (privateCard) {
        privateCard.addEventListener("click", () => {
            privateCard.classList.add("active");
            publicCard.classList.remove("active");
            if (privateRadio) privateRadio.checked = true;
        });
    }

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

    if (addTicketBtn && ticketContainer) {
        console.log("[event_form] addTicketBtn found, attaching listener");
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

    const eventForm = document.getElementById("eventForm");
    if (eventForm) {
        eventForm.addEventListener("submit", (e) => {
            console.log("SUBMIT INTERCEPTADO");
            updateTicketsData();
            const ticketsData = document.getElementById("ticketsData");
            console.log("Tickets data antes de enviar:", ticketsData.value);
            console.log("Datos del formulario:");
            console.log(
                "- Title:",
                document.querySelector('input[name="title"]')?.value,
            );
            console.log(
                "- Start Date:",
                document.querySelector('input[name="start_date"]')?.value,
            );
            console.log(
                "- End Date:",
                document.querySelector('input[name="end_date"]')?.value,
            );
            console.log(
                "- Capacity:",
                document.querySelector('input[name="capacity"]')?.value,
            );
            console.log(
                "- Visibility:",
                document.querySelector('input[name="visibility"]')?.checked,
            );
            // NO prevenimos el envío, dejamos que continúe normalmente
        });
    }

    updateTicketsData();

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
});
