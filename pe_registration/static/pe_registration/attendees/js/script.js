// Datos iniciales
let attendeesData = window.attendeesData || [];
let eventId = window.eventId || null;

// Filtros
let filters = {
    search: '',
    ticket: 'all',
    status: 'all'
};

// Renderizar tabla
function renderTable() {
    const tableBody = document.getElementById('attendeesTableBody');
    if (!tableBody) return;

    const filtered = attendeesData.filter(attendee => {
        const matchesSearch = !filters.search || 
            attendee.name.toLowerCase().includes(filters.search.toLowerCase()) ||
            attendee.email.toLowerCase().includes(filters.search.toLowerCase());
        const matchesTicket = filters.ticket === 'all' || attendee.ticket_type === filters.ticket;
        const matchesStatus = filters.status === 'all' || attendee.status === filters.status;
        
        return matchesSearch && matchesTicket && matchesStatus;
    });

    if (filtered.length === 0) {
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
        return;
    }

    tableBody.innerHTML = filtered.map(attendee => `
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
                ${attendee.status === 'completado' 
                    ? '<span class="badge bg-success">Confirmado</span>' 
                    : '<span class="badge bg-warning">Pendiente</span>'}
            </td>
            <td>${new Date(attendee.registration_date).toLocaleDateString('es-ES')}</td>
            <td class="px-4 text-center">
                <div class="btn-group">
                    <button class="btn btn-sm btn-outline-primary" title="Ver detalles">
                        <span class="material-symbols-outlined" style="font-size: 16px;">visibility</span>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" title="Eliminar">
                        <span class="material-symbols-outlined" style="font-size: 16px;">delete</span>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    // Actualizar contador
    document.getElementById('paginationInfo').textContent = `Mostrando ${filtered.length} asistentes`;
}

// Cargar datos desde API
async function loadAttendees() {
    try {
        const params = new URLSearchParams({
            search: filters.search,
            status: filters.status,
            ticket: filters.ticket
        });
        
        const response = await fetch(`/tickets/api/attendees/${eventId}/?${params}`);
        const data = await response.json();
        
        if (data.success) {
            attendeesData = data.attendees;
            renderTable();
        }
    } catch (error) {
        console.error('Error loading attendees:', error);
    }
}

// Event listeners
document.getElementById('searchAttendee')?.addEventListener('input', (e) => {
    filters.search = e.target.value;
    renderTable();
});

document.getElementById('filterTicket')?.addEventListener('change', (e) => {
    filters.ticket = e.target.value;
    renderTable();
});

document.getElementById('filterStatus')?.addEventListener('change', (e) => {
    filters.status = e.target.value;
    renderTable();
});

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    renderTable();
});