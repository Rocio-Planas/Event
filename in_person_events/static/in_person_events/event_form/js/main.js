document.addEventListener("DOMContentLoaded", () => {
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
    const invitationsInput = document.getElementById("id_invitations");

    function toggleInvitationsRequired(show) {
        if (invitationsInput) {
            invitationsInput.required = show;
        }
    }

    if (publicCard) {
        publicCard.addEventListener("click", () => {
            publicCard.classList.add("active");
            privateCard.classList.remove("active");
            const invitationsGroup = document.getElementById("evInvitationsGroup");
            if (invitationsGroup) {
                invitationsGroup.classList.add("d-none");
            }
            toggleInvitationsRequired(false);
        });
    }

    if (privateCard) {
        privateCard.addEventListener("click", () => {
            privateCard.classList.add("active");
            publicCard.classList.remove("active");
            const invitationsGroup = document.getElementById("evInvitationsGroup");
            if (invitationsGroup) {
                invitationsGroup.classList.remove("d-none");
            }
            toggleInvitationsRequired(true);
        });
    }

    // Handle radio button changes for visibility
    const visibilityRadios = document.querySelectorAll('input[name="visibility"]');
    visibilityRadios.forEach((radio) => {
        radio.addEventListener("change", (e) => {
            const invitationsGroup = document.getElementById("evInvitationsGroup");
            if (invitationsGroup) {
                if (e.target.value === "privado") {
                    invitationsGroup.classList.remove("d-none");
                    toggleInvitationsRequired(true);
                } else {
                    invitationsGroup.classList.add("d-none");
                    toggleInvitationsRequired(false);
                }
            }
        });
    });

    const currentVisibility = document.querySelector('input[name="visibility"]:checked');
    if (currentVisibility && currentVisibility.value === 'privado') {
        toggleInvitationsRequired(true);
    } else {
        toggleInvitationsRequired(false);
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
                    tickets.push({ name: name, price: price });
                }
            }
        });

        ticketsDataInput.value = JSON.stringify(tickets);
    }

    function createTicketItem(ticketId, name = "", price = 0) {
        return `
            <div class="ticket-item d-flex flex-column flex-md-row align-items-center gap-3" id="ticket-${ticketId}">
                <div class="flex-grow-1 w-100">
                    <label class="ev-label mb-1">Nombre del Ticket</label>
                    <input type="text" class="form-control border-0 bg-transparent p-0 fw-medium shadow-none" placeholder="Nombre del ticket" value="${name}" />
                </div>
                <div class="w-100 w-md-25">
                    <label class="ev-label mb-1">Precio</label>
                    <div class="d-flex align-items-center">
                        <span class="fw-bold me-1">€</span>
                        <input type="number" class="form-control border-0 bg-transparent p-0 fw-bold shadow-none" value="${price}" min="0" />
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
            ticketContainer.insertAdjacentHTML("beforeend", createTicketItem(ticketId));
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
            updateTicketsData();
        });
    }

    // Image Upload Preview - Simple version like edit_event_form
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
                reader.onload = function(evt) {
                    showPreview(evt.target.result);
                };
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
});