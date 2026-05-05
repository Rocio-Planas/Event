// Datos iniciales
let attendeesData = window.attendeesData || [];

// Obtener eventId del atributo data-event-id o de window
let eventId = window.eventId || null;
if (!eventId) {
    const container = document.querySelector("[data-event-id]");
    if (container) {
        eventId = container.getAttribute("data-event-id");
        console.log("EventId obtenido del data-attribute:", eventId);
    }
}
console.log("EventId inicial:", eventId);

// Paginación
let currentPage = 1;
const itemsPerPage = 15;

// Filtros
let filters = {
    search: "",
    status: "all",
};

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}

function updatePaginationButtons(totalPages) {
    const prevBtn = document.getElementById("prevPageBtn");
    const nextBtn = document.getElementById("nextPageBtn");

    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
}

// Renderizar tabla
function renderTable() {
    const tableBody = document.getElementById("attendeesTableBody");
    const paginationInfo = document.getElementById("paginationInfo");
    if (!tableBody || !paginationInfo) return;

    const filtered = attendeesData.filter((attendee) => {
        const matchesSearch =
            !filters.search ||
            attendee.name
                .toLowerCase()
                .includes(filters.search.toLowerCase()) ||
            attendee.email.toLowerCase().includes(filters.search.toLowerCase());
        const matchesStatus =
            filters.status === "all" || attendee.status === filters.status;
        return matchesSearch && matchesStatus;
    });

    const totalItems = filtered.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
    if (currentPage > totalPages) currentPage = totalPages;

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginated = filtered.slice(startIndex, endIndex);

    if (totalItems === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4">
                    <div class="text-muted">
                        <span class="material-symbols-outlined" style="width: 48px; height: 48px;">group_remove</span>
                        <p>No hay asistentes con los filtros aplicados</p>
                    </div>
                </td>
            </tr>
        `;
        paginationInfo.textContent = `Mostrando ${paginated.length} asistentes`;
        updatePaginationButtons(1);
        return;
    }

    tableBody.innerHTML = paginated
        .map(
            (attendee) => `
        <tr data-registration-id="${attendee.id}">
            <td class="px-4 py-3">
                <div class="d-flex align-items-center">
                    <div class="bg-light rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                        <span class="material-symbols-outlined">person</span>
                    </div>
                    <div>
                        <div class="fw-bold">${attendee.name}</div>
                        <small class="text-muted">${attendee.email}</small>
                    </div>
                </div>
            </td>
            <td>${attendee.ticket_type}</td>
            <td>
                ${
                    attendee.status === "confirmada"
                        ? '<span class="badge bg-success">Confirmado</span>'
                        : attendee.status === "cancelada"
                          ? '<span class="badge bg-danger">Cancelado</span>'
                          : '<span class="badge bg-warning">Pendiente</span>'
                }
            </td>
            <td>${new Date(attendee.registration_date).toLocaleDateString("es-ES")}</td>
            <td class="px-4 text-center">
                <div class="btn-group">
                    <button class="btn btn-sm btn-outline-primary btn-view-attendee" data-id="${attendee.id}" title="Ver detalles">
                        <span class="material-symbols-outlined" style="font-size: 16px;">visibility</span>
                    </button>
                    <button class="btn btn-sm btn-outline-danger btn-delete-attendee" data-id="${attendee.id}" data-name="${attendee.name}" title="Eliminar">
                        <span class="material-symbols-outlined" style="font-size: 16px;">delete</span>
                    </button>
                </div>
            </td>
        </tr>
    `,
        )
        .join("");

    const shownCount = paginated.length;
    paginationInfo.textContent = `Mostrando ${paginated.length} asistentes`;
    updatePaginationButtons(totalPages);
}

function resetPagination() {
    currentPage = 1;
}

function formatDate(value) {
    if (!value) return "No disponible";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "No disponible";
    return date.toLocaleDateString("es-ES", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

function formatText(value) {
    return value ? value : "No especificado";
}

function formatLink(value) {
    if (!value) return "No especificado";
    return `<a href="${value}" target="_blank" rel="noopener noreferrer">${value}</a>`;
}

function showAttendeeModal(attendee) {
    if (!attendee) return;

    const modalAvatar = document.getElementById("modalAvatar");
    const modalName = document.getElementById("modalName");
    const modalEmail = document.getElementById("modalEmail");
    const modalRole = document.getElementById("modalRole");
    const modalPhone = document.getElementById("modalPhone");
    const modalBirthDate = document.getElementById("modalBirthDate");
    const modalSex = document.getElementById("modalSex");
    const modalLastActivity = document.getElementById("modalLastActivity");
    const modalTicketType = document.getElementById("modalTicketType");
    const modalStatus = document.getElementById("modalStatus");
    const modalAddress = document.getElementById("modalAddress");
    const modalBio = document.getElementById("modalBio");
    const modalWebsite = document.getElementById("modalWebsite");
    const modalTwitter = document.getElementById("modalTwitter");
    const modalInstagram = document.getElementById("modalInstagram");
    const modalLinkedin = document.getElementById("modalLinkedin");

    if (modalAvatar) {
        modalAvatar.src =
            attendee.avatar_url ||
            "https://via.placeholder.com/120?text=Avatar";
        modalAvatar.alt = attendee.name;
    }
    if (modalName) modalName.textContent = attendee.name;
    if (modalEmail) modalEmail.textContent = attendee.email;
    if (modalRole)
        modalRole.textContent = attendee.role
            ? attendee.role.charAt(0).toUpperCase() + attendee.role.slice(1)
            : "No especificado";
    if (modalPhone) modalPhone.textContent = formatText(attendee.phone);
    if (modalBirthDate)
        modalBirthDate.textContent = formatDate(attendee.birth_date);
    if (modalSex)
        modalSex.textContent = attendee.sex_display || formatText(attendee.sex);
    if (modalLastActivity)
        modalLastActivity.textContent = formatDate(attendee.last_activity);
    if (modalTicketType)
        modalTicketType.textContent = formatText(attendee.ticket_type);
    if (modalStatus)
        modalStatus.textContent =
            attendee.status === "confirmada"
                ? "Confirmado"
                : attendee.status === "cancelada"
                  ? "Cancelado"
                  : "Pendiente";
    if (modalAddress) modalAddress.textContent = formatText(attendee.address);
    if (modalBio) modalBio.textContent = formatText(attendee.bio);
    if (modalWebsite) modalWebsite.innerHTML = formatLink(attendee.website);
    if (modalTwitter)
        modalTwitter.innerHTML = attendee.twitter
            ? `<a href="https://twitter.com/${attendee.twitter}" target="_blank" rel="noopener noreferrer">@${attendee.twitter}</a>`
            : "No especificado";
    if (modalInstagram)
        modalInstagram.innerHTML = attendee.instagram
            ? `<a href="https://instagram.com/${attendee.instagram}" target="_blank" rel="noopener noreferrer">@${attendee.instagram}</a>`
            : "No especificado";
    if (modalLinkedin)
        modalLinkedin.innerHTML = attendee.linkedin
            ? `<a href="${attendee.linkedin}" target="_blank" rel="noopener noreferrer">LinkedIn</a>`
            : "No especificado";

    const modalElement = document.getElementById("attendeeInfoModal");
    if (modalElement && typeof bootstrap !== "undefined") {
        const attendeeModal = new bootstrap.Modal(modalElement);
        attendeeModal.show();
    }
}

let deleteRegistrationId = null;
function openDeleteModal(registrationId, attendeeName) {
    deleteRegistrationId = registrationId;
    const nameField = document.getElementById("deleteAttendeeName");
    if (nameField) nameField.textContent = attendeeName;
    const modalElement = document.getElementById("deleteAttendeeModal");
    if (modalElement && typeof bootstrap !== "undefined") {
        const deleteModal = new bootstrap.Modal(modalElement);
        deleteModal.show();
    }
}

async function deleteAttendee() {
    if (!deleteRegistrationId || !eventId) return;

    try {
        const response = await fetch(
            `/tickets/api/attendees/${eventId}/delete/${deleteRegistrationId}/`,
            {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                credentials: "same-origin",
            },
        );
        const data = await response.json();
        if (response.ok && data.success) {
            const modalElement = document.getElementById("deleteAttendeeModal");
            if (modalElement && typeof bootstrap !== "undefined") {
                bootstrap.Modal.getInstance(modalElement)?.hide();
            }
            deleteRegistrationId = null;
            loadAttendees();
        } else {
            console.error("Error eliminando asistente:", data);
            alert(data.error || "No se pudo eliminar el asistente.");
        }
    } catch (error) {
        console.error("Error eliminando asistente:", error);
        alert("Ocurrió un error al eliminar el asistente.");
    }
}

// Mostrar modal de información o de eliminación al hacer clic en el botón correspondiente
document.addEventListener("click", (event) => {
    const viewButton = event.target.closest(".btn-view-attendee");
    if (viewButton) {
        const registrationId = viewButton.dataset.id;
        if (!registrationId) return;
        const attendee = attendeesData.find(
            (item) => String(item.id) === String(registrationId),
        );
        if (attendee) {
            showAttendeeModal(attendee);
        }
        return;
    }

    const deleteButton = event.target.closest(".btn-delete-attendee");
    if (deleteButton) {
        const registrationId = deleteButton.dataset.id;
        const attendeeName = deleteButton.dataset.name || "este asistente";
        if (!registrationId) return;
        openDeleteModal(registrationId, attendeeName);
    }
});

const confirmDeleteBtn = document.getElementById("confirmDeleteAttendeeBtn");
if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", deleteAttendee);
}

// Cargar datos desde API
async function loadAttendees() {
    console.log(
        "Iniciando loadAttendees(), eventId:",
        eventId,
        "filters:",
        filters,
    );

    try {
        const params = new URLSearchParams({
            search: filters.search,
            status: filters.status,
        });
        if (filters.ticket && filters.ticket !== "all") {
            params.set("ticket", filters.ticket);
        }

        const url = `/tickets/api/attendees/${eventId}/?${params}`;
        console.log("URL del fetch:", url);

        const response = await fetch(url);
        console.log("Response status:", response.status, response.statusText);

        const data = await response.json();
        console.log("Datos recibidos:", data);

        if (data.success) {
            attendeesData = data.attendees;
            console.log("Asistentes cargados:", attendeesData.length);
            renderTable();
        } else {
            console.warn("La respuesta no fue exitosa:", data);
        }
    } catch (error) {
        console.error("Error loading attendees:", error);
    }
}

// Event listeners
const searchInput = document.getElementById("searchAttendee");
const ticketSelect = document.getElementById("filterTicket");
const statusSelect = document.getElementById("filterStatus");
const prevPageBtn = document.getElementById("prevPageBtn");
const nextPageBtn = document.getElementById("nextPageBtn");

searchInput?.addEventListener("input", (e) => {
    filters.search = e.target.value;
    resetPagination();
    if (currentView === "attendees") {
        renderTable();
    } else {
        renderWaitlistTable();
    }
});

statusSelect?.addEventListener("change", (e) => {
    filters.status = e.target.value;
    resetPagination();
    renderTable();
});

prevPageBtn?.addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage -= 1;
        renderTable();
    }
});

nextPageBtn?.addEventListener("click", () => {
    currentPage += 1;
    renderTable();
});

// Variables waitlist
let waitlistData = [];
let currentView = "attendees";

function switchView(view) {
    currentView = view;
    const attendeesTable = document.getElementById("attendeesTable");
    const waitlistTable = document.getElementById("waitlistTable");
    const statusFilterCol = document.getElementById("statusFilterCol");
    const waitlistSwitch = document.getElementById("waitlistSwitch");
    const paginationInfo = document.getElementById("paginationInfo");

    if (view === "waitlist") {
        if (waitlistSwitch) waitlistSwitch.checked = true;
        if (attendeesTable) attendeesTable.style.display = "none";
        if (waitlistTable) waitlistTable.style.display = "table";
        if (statusFilterCol) statusFilterCol.style.display = "none";
        loadWaitlist();
    } else {
        if (waitlistSwitch) waitlistSwitch.checked = false;
        if (attendeesTable) attendeesTable.style.display = "table";
        if (waitlistTable) waitlistTable.style.display = "none";
        if (statusFilterCol) statusFilterCol.style.display = "block";
        if (paginationInfo) paginationInfo.textContent = "";
    }
    currentPage = 1;
}

function toggleWaitlistView(isWaitlist) {
    switchView(isWaitlist ? "waitlist" : "attendees");
}

function loadWaitlist() {
    console.log("Cargando waitlist para eventId:", eventId);
    const url = `/tickets/api/waitlist/${eventId}/`;
    fetch(url)
        .then((res) => {
            console.log("Response status:", res.status);
            return res.json();
        })
        .then((data) => {
            console.log("Waitlist data:", data);
            console.log("waitlistData:", data.waitlist);
            waitlistData = data.waitlist || [];
            console.log("waitlistData длиnа:", waitlistData.length);
            renderWaitlistTable();
            document.getElementById("totalWaitlist").textContent =
                waitlistData.length;
        })
        .catch((err) => console.error("Error cargando waitlist:", err));
}

function renderWaitlistTable() {
    const tableBody = document.getElementById("waitlistTableBody");
    if (!tableBody) return;
    const paginationInfo = document.getElementById("paginationInfo");

    const filtered = waitlistData.filter((item) => {
        const matchesSearch =
            !filters.search ||
            item.name.toLowerCase().includes(filters.search.toLowerCase()) ||
            item.email.toLowerCase().includes(filters.search.toLowerCase());
        return matchesSearch;
    });

    if (filtered.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center py-4">
                    <div class="text-muted">
                        <span class="material-symbols-outlined" style="width: 48px; height: 48px;">hourglass_empty</span>
                        <p>No hay usuarios en lista de espera</p>
                    </div>
                </td>
            </tr>
        `;
        if (paginationInfo) paginationInfo.textContent = "";
        return;
    }

    if (paginationInfo)
        paginationInfo.textContent = `Mostrando ${filtered.length} en lista de espera`;

    tableBody.innerHTML = filtered
        .map(
            (item, index) => `
        <tr>
            <td class="px-4 py-3">${index + 1}</td>
            <td class="py-3">
                <div class="fw-bold">${item.name}</div>
                <small class="text-muted">${item.email}</small>
            </td>
            <td class="py-3">${item.created_at}</td>
            <td class="px-4 py-3 text-center">
                <button class="btn btn-sm btn-outline-danger" onclick="removeFromWaitlist(${item.id})" title="Eliminar">
                    <span class="material-symbols-outlined" style="font-size: 18px;">delete</span>
                </button>
            </td>
        </tr>
    `,
        )
        .join("");
}

function promoteFromWaitlist() {
    const modal = new bootstrap.Modal(
        document.getElementById("deleteWaitlistModal"),
    );
    document.getElementById("deleteWaitlistModalLabel").textContent =
        "Promover usuario";
    document.querySelector("#deleteWaitlistModal .modal-body p").textContent =
        "¿Estás seguro de que deseas promover al primer usuario de la lista de espera?";

    const btn = document.getElementById("confirmDeleteWaitlistBtn");
    btn.onclick = function () {
        modal.hide();
        doPromoteFromWaitlist();
    };
    modal.show();
}

function doPromoteFromWaitlist() {
    const url = `/tickets/api/waitlist/${eventId}/promote/`;
    fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                loadWaitlist();
                loadAttendees();
            } else {
                alert(data.error || "Error al promover");
            }
        })
        .catch((err) => console.error("Error:", err));
}

function removeFromWaitlist(waitlistId) {
    const item = waitlistData.find((w) => w.id === waitlistId);
    if (!item) return;

    const modal = new bootstrap.Modal(
        document.getElementById("deleteWaitlistModal"),
    );
    document.getElementById("deleteWaitlistModalLabel").textContent =
        "Eliminar de lista de espera";
    document.getElementById("deleteWaitlistName").textContent = item.name;

    const btn = document.getElementById("confirmDeleteWaitlistBtn");
    btn.onclick = function () {
        modal.hide();
        doRemoveFromWaitlist(waitlistId);
    };
    modal.show();
}

function doRemoveFromWaitlist(waitlistId) {
    const url = `/tickets/api/waitlist/${eventId}/remove/${waitlistId}/`;
    fetch(url, {
        method: "DELETE",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                loadWaitlist();
            } else {
                alert(data.error || "Error al eliminar");
            }
        })
        .catch((err) => console.error("Error:", err));
}

// Inicializar
document.addEventListener("DOMContentLoaded", () => {
    switchView("attendees");
    loadAttendees();
    loadWaitlist();
});
