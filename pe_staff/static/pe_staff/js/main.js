// Datos del contexto de Django
let membersData = window.membersData || [];
let invitationsData = window.invitationsData || [];
let eventId = window.eventId || null;

// Mostrar/ocultar selector de rol según tipo de usuario
document.getElementById("userType")?.addEventListener("change", function () {
    const roleDiv = document.getElementById("roleSelectDiv");
    const roleSelect = document.getElementById("inviteRole");

    if (this.value === "staff") {
        roleDiv.style.display = "block";
        roleSelect.required = true;
    } else {
        roleDiv.style.display = "none";
        roleSelect.required = false;
        roleSelect.value = "";
    }
});

// Formulario de invitación
document
    .getElementById("inviteForm")
    ?.addEventListener("submit", async function (e) {
        e.preventDefault();

        const email = document.getElementById("inviteEmail").value.trim();
        const userType = document.getElementById("userType").value;
        const role = document.getElementById("inviteRole").value;

        if (!email) {
            alert("Por favor ingresa un correo electrónico");
            return;
        }

        if (userType === "staff" && !role) {
            alert("Por favor selecciona un rol para el staff");
            return;
        }

        try {
            const response = await fetch(`/equipo/staff/${eventId}/invite/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({
                    email: email,
                    user_type: userType,
                    role: role,
                }),
            });

            const data = await response.json();

            if (data.success) {
                alert("¡Invitación enviada con éxito!");
                // Cerrar modal y recargar
                const modal = bootstrap.Modal.getInstance(
                    document.getElementById("inviteStaffModal"),
                );
                modal.hide();
                window.location.reload();
            } else {
                alert(data.error || "Error al enviar invitación");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error al enviar invitación");
        }
    });

// Formulario de asignar zona
document
    .getElementById("assignZoneForm")
    ?.addEventListener("submit", async function (e) {
        e.preventDefault();

        const memberId = document.getElementById("memberId").value;
        const zone = document.getElementById("zoneName").value.trim();

        if (!memberId || !zone) {
            alert("Datos incompletos");
            return;
        }

        try {
            const response = await fetch(
                `/equipo/staff/${eventId}/assign-zone/${memberId}/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ zone: zone }),
                },
            );

            const data = await response.json();

            if (data.success) {
                alert("¡Zona asignada correctamente!");
                window.location.reload();
            } else {
                alert(data.error || "Error al asignar zona");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error al asignar zona");
        }
    });

// Configurar modal de asignar zona
document
    .getElementById("assignZoneModal")
    ?.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const memberId = button?.getAttribute("data-member-id");
        document.getElementById("memberId").value = memberId || "";
    });

// Obtener CSRF Token
function getCSRFToken() {
    const name = "csrftoken";
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1),
                );
                break;
            }
        }
    }
    return cookieValue;
}

// Cancelar invitación pendiente (pasar a rechazada)
document.addEventListener("click", async function (event) {
    const button = event.target.closest(".cancel-invitation-btn");
    if (!button) return;

    const invitationId = button.getAttribute("data-invitation-id");
    if (!invitationId) return;

    const invitationRow = button.closest('tr');
    const invitationNameEl = invitationRow?.querySelector('.fw-bold');
    const invitationName = invitationNameEl ? invitationNameEl.textContent : 'esta invitación';

    const cancelModalEl = document.getElementById('cancelInvitationModal');
    const cancelModal = new bootstrap.Modal(cancelModalEl);
    document.getElementById('cancelInvitationName').textContent = invitationName;
    document.getElementById('confirmCancelInvitationBtn').dataset.invitationId = invitationId;
    cancelModal.show();

    document.getElementById('confirmCancelInvitationBtn').onclick = async function() {
        try {
            const response = await fetch(
                `/equipo/staff/${eventId}/cancel-invitation/${invitationId}/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                },
            );

            const data = await response.json();
            if (data.success) {
                cancelModal.hide();
                window.location.reload();
            } else {
                alert(data.error || "Error al cancelar la invitación");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error al cancelar la invitación");
        }
    };
});

// Eliminar invitación (aceptada o rechazada)
document.addEventListener("click", async function (event) {
    const button = event.target.closest(".delete-invitation-btn");
    if (!button) return;

    const invitationId = button.getAttribute("data-invitation-id");
    if (!invitationId) return;

    const invitationRow = button.closest('tr');
    const invitationNameEl = invitationRow?.querySelector('.fw-bold');
    const invitationName = invitationNameEl ? invitationNameEl.textContent : 'esta invitación';

    const deleteModalEl = document.getElementById('deleteInvitationModal');
    const deleteModal = new bootstrap.Modal(deleteModalEl);
    document.getElementById('deleteInvitationName').textContent = invitationName;
    document.getElementById('confirmDeleteInvitationBtn').dataset.invitationId = invitationId;
    deleteModal.show();

    document.getElementById('confirmDeleteInvitationBtn').onclick = async function() {
        try {
            const response = await fetch(
                `/equipo/staff/${eventId}/delete-invitation/${invitationId}/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                },
            );

            const data = await response.json();
            if (data.success) {
                deleteModal.hide();
                window.location.reload();
            } else {
                alert(data.error || "Error al eliminar la invitación");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Error al eliminar la invitación");
        }
    };
});

// Ver miembros
document.addEventListener("click", function (event) {
    const viewBtn = event.target.closest("[data-bs-target='#viewMemberModal']");
    if (!viewBtn) return;

    document.getElementById('viewMemberName').textContent = viewBtn.dataset.memberName || '';
    document.getElementById('viewMemberEmail').textContent = viewBtn.dataset.memberEmail || '';
    document.getElementById('viewMemberType').textContent = viewBtn.dataset.memberType || '';
    document.getElementById('viewMemberRole').textContent = viewBtn.dataset.memberRole || '';
    document.getElementById('viewMemberZone').textContent = viewBtn.dataset.memberZone || '';
});

// Ver invitaciones aceptadas
document.addEventListener("click", function (event) {
    const viewBtn = event.target.closest("[data-bs-target='#attendeeInfoModal']");
    if (!viewBtn) return;

    document.getElementById('modalName').textContent = viewBtn.dataset.attendeeName || '';
    document.getElementById('modalEmail').textContent = viewBtn.dataset.attendeeEmail || '';
    document.getElementById('modalType').textContent = viewBtn.dataset.attendeeType || '';
    document.getElementById('modalPhone').textContent = viewBtn.dataset.attendeePhone || 'No disponible';
    document.getElementById('modalStatus').textContent = 'Aceptada';
    document.getElementById('modalAcceptedAt').textContent = new Date().toLocaleDateString();
});

// Eliminar miembro del equipo
document.addEventListener("click", async function (event) {
    const deleteBtn = event.target.closest(".remove-member-btn");
    if (!deleteBtn) return;

    const memberId = deleteBtn.getAttribute("data-member-id");
    if (!memberId) return;

    const memberRow = deleteBtn.closest('tr');
    const memberName = memberRow ? memberRow.querySelector('.fw-bold')?.textContent : 'este miembro';
    
    const deleteModalEl = document.getElementById('deleteMemberModal');
    const deleteModal = new bootstrap.Modal(deleteModalEl);
    document.getElementById('deleteMemberName').textContent = memberName;
    document.getElementById('confirmDeleteMemberBtn').dataset.memberId = memberId;
    deleteModal.show();

    document.getElementById('confirmDeleteMemberBtn').onclick = async function() {
        try {
            const response = await fetch(
                `/equipo/staff/${eventId}/remove-member/${memberId}/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                },
            );

            const data = await response.json();
            if (data.success) {
                deleteModal.hide();
                window.location.reload();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };
});

// Inicializar
document.addEventListener("DOMContentLoaded", function () {
    console.log("Staff management initialized");

    // Filtros
    const searchInput = document.getElementById('searchMember');
    const roleSelect = document.getElementById('filterRole');
    const statusSelect = document.getElementById('filterStatus');
    const tableBody = document.getElementById('membersTableBody');

    if (!searchInput || !roleSelect || !statusSelect || !tableBody) {
        console.error('Algunos elementos del filtro no fueron encontrados');
        return;
    }

    function filterTable() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedRole = roleSelect.value.toLowerCase().trim();
        const selectedStatus = statusSelect.value.toLowerCase().trim();

        const rows = tableBody.querySelectorAll('tr[data-member-id], tr[data-invitation-id]');
        
        console.log('Filtrando:', { searchTerm, selectedRole, selectedStatus, rowCount: rows.length });

        let totalMembers = 0;
        let activeMembers = 0;
        let pendingInvitations = 0;
        let rejectedInvitations = 0;
        let acceptedInvitations = 0;

        rows.forEach(row => {
            const nameEl = row.querySelector('.fw-bold');
            const emailEls = row.querySelectorAll('.text-muted');
            const emailEl = emailEls.length > 0 ? emailEls[0] : null;
            const roleBadgeEl = row.querySelector('td:nth-child(2) .badge');
            const statusBadgeEl = row.querySelector('td:nth-child(4) .badge');

            const name = nameEl?.textContent.toLowerCase().trim() || '';
            const email = emailEl?.textContent.toLowerCase().trim() || '';
            const roleBadge = row.dataset.role || roleBadgeEl?.textContent.toLowerCase().trim() || '';
            const statusBadge = row.dataset.status || statusBadgeEl?.textContent.toLowerCase().trim() || '';

            const normalizedRole = roleBadge.toLowerCase().trim();
            const normalizedStatus = statusBadge.toLowerCase().trim();

            // Búsqueda por nombre o email
            const matchesSearch = !searchTerm || name.includes(searchTerm) || email.includes(searchTerm);

            // Filtro por tipo (Ponente o Staff)
            let matchesRole = !selectedRole;
            if (selectedRole === 'ponente') {
                matchesRole = normalizedRole === 'ponente';
            } else if (selectedRole === 'staff') {
                matchesRole = normalizedRole === 'staff';
            }

            // Filtro por estado (Pendiente, Rechazado, Confirmado)
            let matchesStatus = !selectedStatus;
            if (selectedStatus === 'pendiente') {
                matchesStatus = normalizedStatus === 'pendiente';
            } else if (selectedStatus === 'rechazado') {
                matchesStatus = normalizedStatus === 'rechazado';
            } else if (selectedStatus === 'confirmado') {
                matchesStatus = normalizedStatus === 'confirmado';
            }

            // Mostrar u ocultar fila
            const shouldShow = matchesSearch && matchesRole && matchesStatus;
            row.style.display = shouldShow ? '' : 'none';

            if (shouldShow) {
                totalMembers++;
                if (normalizedStatus === 'confirmado') {
                    activeMembers++;
                    if (row.dataset.type === 'invitation') {
                        acceptedInvitations++;
                    }
                } else if (normalizedStatus === 'pendiente') {
                    pendingInvitations++;
                } else if (normalizedStatus === 'rechazado') {
                    rejectedInvitations++;
                }
            }
        });

        const paginationInfo = document.getElementById('paginationInfo');

        if (paginationInfo) {
            paginationInfo.textContent = `Mostrando ${totalMembers} de ${rows.length} miembros filtrados | ${pendingInvitations} pendientes | ${acceptedInvitations} aceptadas | ${rejectedInvitations} rechazadas`;
        }
    }

    searchInput.addEventListener('input', filterTable);
    roleSelect.addEventListener('change', filterTable);
    statusSelect.addEventListener('change', filterTable);

    filterTable();
    console.log('Filtros inicializados correctamente');
});
