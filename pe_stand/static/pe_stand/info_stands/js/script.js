// EventPro Stand Manager Interactions

document.addEventListener('DOMContentLoaded', () => {
    console.log('EventPro Stand Manager Initialized');

    // Handle "Nuevo Recurso" Catalog Injection
    const resourceCatalog = document.getElementById('resourceCatalog');
    const catalogItems = [
        { id: 'cam1', name: 'Cámara 4K', icon: 'videocam', dest: 'Entrada Stand' },
        { id: 'mic1', name: 'Micrófono Inalámbrico', icon: 'mic', dest: 'Sala Presentaciones' },
        { id: 'lpt1', name: 'Laptop Workstation', icon: 'laptop', dest: 'Control IT' },
        { id: 'tbl1', name: 'Mesa de Demo', icon: 'table_bar', dest: 'Zona Exhibición' }
    ];

    if (resourceCatalog) {
        resourceCatalog.innerHTML = catalogItems.map(item => `
            <label class="list-group-item d-flex align-items-center gap-3 p-3">
                <input class="form-check-input me-1" type="checkbox" value="${item.id}" data-name="${item.name}" data-icon="${item.icon}" data-dest="${item.dest}">
                <div class="bg-light rounded p-2 d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                    <span class="material-symbols-outlined text-muted fs-6">${item.icon}</span>
                </div>
                <span class="fw-medium">${item.name}</span>
            </label>
        `).join('');
    }

    // Handle Confirm Add
    const confirmAddBtn = document.getElementById('confirmAddBtn');
    const inventoryTableBody = document.querySelector('table tbody');

    // State for editing
    let currentRowBeingEdited = null;
    const editModalEl = document.getElementById('editResourceModal');
    const editModal = editModalEl ? new bootstrap.Modal(editModalEl) : null;
    const editDestInput = document.getElementById('editDestInput');
    const editReqInput = document.getElementById('editReqInput');
    const editResourceNameLabel = document.getElementById('editResourceName');
    const saveResourceEditBtn = document.getElementById('saveResourceEditBtn');

    if (confirmAddBtn && inventoryTableBody) {
        confirmAddBtn.addEventListener('click', () => {
            const selected = document.querySelectorAll('#resourceCatalog input:checked');
            selected.forEach(checkbox => {
                const name = checkbox.dataset.name;
                const icon = checkbox.dataset.icon;
                const dest = checkbox.dataset.dest;
                const newRow = createInventoryRow(name, icon, dest, 1);
                inventoryTableBody.appendChild(newRow);
                checkbox.checked = false; // Reset for next time
            });
            
            // Close modal
            const modalElement = document.getElementById('addResourceModal');
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) modalInstance.hide();
        });
    }

    if (saveResourceEditBtn) {
        saveResourceEditBtn.addEventListener('click', () => {
            if (currentRowBeingEdited) {
                const destLabel = currentRowBeingEdited.querySelector('.target-label');
                const reqLabel = currentRowBeingEdited.querySelector('.required-val');
                
                destLabel.innerText = editDestInput.value;
                reqLabel.innerText = editReqInput.value;
                
                // Re-evaluate status based on new requirement
                updateRowStatus(currentRowBeingEdited);
                
                editModal.hide();
                currentRowBeingEdited = null;
            }
        });
    }

    function createInventoryRow(name, icon, dest, required = 1) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="px-4">
                <div class="d-flex align-items-center gap-3">
                    <div class="bg-light rounded p-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                        <span class="material-symbols-outlined text-muted fs-5">${icon}</span>
                    </div>
                    <div class="fw-bold fs-7 text-nowrap resource-name">${name}</div>
                </div>
            </td>
            <td class="px-4">
                <div class="d-flex align-items-center justify-content-center gap-3">
                    <button class="btn btn-outline-secondary btn-sm rounded-circle p-1 d-flex align-items-center justify-content-center btn-remove" style="width: 28px; height: 28px;">
                        <span class="material-symbols-outlined fs-6">remove</span>
                    </button>
                    <div class="text-center fw-bold">
                        <span class="assigned-val">0</span><span class="text-muted">/</span><span class="required-val text-muted">${required}</span>
                    </div>
                    <button class="btn btn-outline-primary btn-sm rounded-circle p-1 d-flex align-items-center justify-content-center btn-add" style="width: 28px; height: 28px;">
                        <span class="material-symbols-outlined fs-6">add</span>
                    </button>
                </div>
            </td>
            <td class="px-4">
                <span class="badge badge-custom bg-warning-subtle text-warning status-badge">Pendiente</span>
            </td>
            <td class="px-4">
                <small class="text-muted fw-medium target-label">${dest}</small>
            </td>
            <td class="px-4 text-end">
                <button class="btn btn-link btn-sm p-0 text-muted opacity-50 hover-opacity-100" title="Editar recurso">
                    <span class="material-symbols-outlined fs-edit-icon">edit</span>
                </button>
            </td>
        `;
        
        // Add event listeners
        initRowControls(tr);

        return tr;
    }

    function initRowControls(row) {
        const editBtn = row.querySelector('[title="Editar recurso"]');
        if (editBtn) editBtn.addEventListener('click', handleEditResource);

        const addBtn = row.querySelector('.btn-add');
        if (addBtn) addBtn.addEventListener('click', () => {
            const assignedVal = row.querySelector('.assigned-val');
            let val = parseInt(assignedVal.innerText);
            assignedVal.innerText = ++val;
            updateRowStatus(row);
        });

        const removeBtn = row.querySelector('.btn-remove');
        if (removeBtn) removeBtn.addEventListener('click', () => {
            const assignedVal = row.querySelector('.assigned-val');
            let val = parseInt(assignedVal.innerText);
            if (val > 0) {
                assignedVal.innerText = --val;
                updateRowStatus(row);
            }
        });
    }

    function handleEditResource(e) {
        const row = e.currentTarget.closest('tr');
        currentRowBeingEdited = row;
        
        const name = row.querySelector('.resource-name')?.innerText || row.querySelector('.fw-bold.fs-7')?.innerText;
        const dest = row.querySelector('.target-label').innerText;
        const req = row.querySelector('.required-val').innerText;
        
        if (editResourceNameLabel) editResourceNameLabel.innerText = `Ajustando: ${name}`;
        if (editDestInput) editDestInput.value = dest;
        if (editReqInput) editReqInput.value = req;
        
        if (editModal) editModal.show();
    }

    function updateRowStatus(row) {
        const assigned = parseInt(row.querySelector('.assigned-val').innerText);
        const required = parseInt(row.querySelector('.required-val').innerText);
        const badge = row.querySelector('.status-badge') || row.querySelector('.badge');
        
        if (assigned >= required) {
            badge.className = 'badge badge-custom bg-success-subtle text-success status-badge';
            badge.innerText = 'Completado';
        } else if (assigned > 0) {
            badge.className = 'badge badge-custom bg-warning-subtle text-warning status-badge';
            badge.innerText = 'Pendiente';
        } else {
            badge.className = 'badge badge-custom bg-danger-subtle text-danger status-badge';
            badge.innerText = 'Crítico';
        }
    }

    // Initialize existing rows
    document.querySelectorAll('table tbody tr').forEach(row => {
        // Fix for existing rows that don't have all classes yet (but we added them in previous edit)
        // Ensure they have the "edit" icon title updated to "Editar recurso" for consistency
        const editBtn = row.querySelector('[title="Editar destino"]');
        if (editBtn) {
            editBtn.title = "Editar recurso";
        }
        initRowControls(row);
    });

    // --- Activities Details & Management Logic ---
    let currentActivityCard = null;
    const activityDetailsModalEl = document.getElementById('activityDetailsModal');
    const deleteActivityBtn = document.getElementById('deleteActivityBtn');
    const moveActivityBtn = document.getElementById('moveActivityBtn');

    // Add listener to track which card opened the modal
    document.addEventListener('click', (e) => {
        if (e.target.matches('[data-bs-target="#activityDetailsModal"]')) {
            currentActivityCard = e.target.closest('.activity-card');
        }
    });

    if (deleteActivityBtn) {
        deleteActivityBtn.addEventListener('click', () => {
            if (currentActivityCard && confirm('¿Estás seguro de que deseas eliminar esta actividad del stand?')) {
                currentActivityCard.remove();
                currentActivityCard = null;
                const modal = bootstrap.Modal.getInstance(activityDetailsModalEl);
                if (modal) modal.hide();
            }
        });
    }

    if (moveActivityBtn) {
        moveActivityBtn.addEventListener('click', () => {
            if (currentActivityCard) {
                const newLoc = prompt('Ingresa el nombre del nuevo stand o zona:', 'Stand B - Sector 12');
                if (newLoc) {
                    alert(`Actividad movida con éxito a: ${newLoc}`);
                    currentActivityCard.remove();
                    currentActivityCard = null;
                    const modal = bootstrap.Modal.getInstance(activityDetailsModalEl);
                    if (modal) modal.hide();
                }
            }
        });
    }

    // --- Activity Assignment Logic ---
    const activityCatalogList = document.getElementById('activityCatalogList');
    const organizerActivities = [
        { 
            id: 'act1', 
            title: 'Taller de VR Inmersivo', 
            time: '02:00 PM', 
            duration: '30 min', 
            speakers: 'Luis M., Ana P.', 
            desc: 'Experiencia práctica con las últimas gafas de realidad virtual para entornos comerciales.',
            imgs: ['https://images.unsplash.com/photo-1593508512255-86ab42a8e620?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80']
        },
        { 
            id: 'act2', 
            title: 'Keynote: Futuro del Ecommerce', 
            time: '04:30 PM', 
            duration: '90 min', 
            speakers: 'Robert C.', 
            desc: 'Análisis profundo sobre las tendencias globales que dominarán el comercio electrónico en 2027.',
            imgs: ['https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80']
        }
    ];

    if (activityCatalogList) {
        activityCatalogList.innerHTML = organizerActivities.map(act => `
            <label class="list-group-item d-flex align-items-center gap-3 p-3" style="cursor: pointer;">
                <input class="form-check-input me-1" type="radio" name="catalogActivity" value="${act.id}">
                <div class="flex-grow-1">
                    <p class="mb-0 fw-bold small">${act.title}</p>
                    <p class="mb-0 text-muted" style="font-size: 0.65rem">${act.time} — ${act.duration} | ${act.speakers}</p>
                </div>
            </label>
        `).join('');
    }

    const confirmAssignActivityBtn = document.getElementById('confirmAssignActivityBtn');
    const activityCardsContainer = document.querySelector('.activity-card').parentElement;

    if (confirmAssignActivityBtn && activityCardsContainer) {
        confirmAssignActivityBtn.addEventListener('click', () => {
            const selectedRadio = document.querySelector('input[name="catalogActivity"]:checked');
            if (!selectedRadio) {
                alert('Por favor selecciona una actividad.');
                return;
            }

            const actId = selectedRadio.value;
            const act = organizerActivities.find(a => a.id === actId);

            const newCard = document.createElement('div');
            newCard.className = 'activity-card mb-3';
            newCard.innerHTML = `
                <div class="d-flex justify-content-between mb-2">
                    <div class="d-flex flex-column">
                        <span class="text-muted fw-bold text-uppercase" style="font-size: 0.65rem">Programado — ${act.time}</span>
                        <small class="text-muted" style="font-size: 0.7rem">26 de Abril, 2026</small>
                    </div>
                    <div class="d-flex">
                        ${act.imgs.map(img => `<img src="${img}" style="width: 28px; height: 28px" class="rounded-circle border border-2 border-white ms-n2">`).join('')}
                    </div>
                </div>
                <h5 class="fw-bold h6">${act.title}</h5>
                <p class="text-muted small mb-3">${act.desc}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <div class="d-flex gap-3 text-muted" style="font-size: 0.7rem">
                        <span class="d-flex align-items-center gap-1"><span class="material-symbols-outlined fs-6">schedule</span> ${act.duration}</span>
                        <span class="d-flex align-items-center gap-1"><span class="material-symbols-outlined fs-6">person</span> Ponentes: ${act.speakers}</span>
                    </div>
                    <button class="btn btn-link btn-sm p-0 text-primary fw-bold text-decoration-none" style="font-size: 0.75rem" data-bs-toggle="modal" data-bs-target="#activityDetailsModal">Ver detalles</button>
                </div>
            `;

            activityCardsContainer.appendChild(newCard);

            // Close Modal
            const modalEl = document.getElementById('assignActivityModal');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) modalInstance.hide();
        });
    }

    // --- Activities Search Logic ---
    const searchActivitiesInput = document.getElementById('searchActivities');
    const activitiesList = document.querySelector('.col-12 .custom-card'); // Activities container (second col-12)

    if (searchActivitiesInput) {
        searchActivitiesInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const activityCards = document.querySelectorAll('.activity-card');
            
            activityCards.forEach(card => {
                const title = card.querySelector('h5').innerText.toLowerCase();
                const desc = card.querySelector('p').innerText.toLowerCase();
                
                if (title.includes(searchTerm) || desc.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Handle "Descargar PDF" button
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', () => {
            window.print(); // Basic print functionality as placeholder for PDF export
        });
    }

    // --- Team Switching Logic ---
    const staffCatalog = document.getElementById('staffCatalog');
    const catalogStaff = [
        { id: 'st1', name: 'Elena Rodríguez', role: 'Líder de Stand', img: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80' },
        { id: 'st2', name: 'Marcos Valenzuela', role: 'Especialista IT', img: 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80' },
        { id: 'st3', name: 'Lucía Méndez', role: 'Coordinadora Logística', img: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80' },
        { id: 'st4', name: 'Javier Soto', role: 'Analista de Datos', img: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80' },
        { id: 'st5', name: 'Sofía Castro', role: 'Diseñadora Experiencias', img: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80' }
    ];

    if (staffCatalog) {
        staffCatalog.innerHTML = catalogStaff.map(person => `
            <label class="list-group-item d-flex align-items-center gap-3 p-3" style="cursor: pointer;">
                <input class="form-check-input me-1" type="checkbox" value="${person.id}" data-name="${person.name}" data-role="${person.role}" data-img="${person.img}">
                <img src="${person.img}" class="rounded-circle" style="width: 32px; height: 32px; object-fit: cover;">
                <div class="flex-grow-1">
                    <p class="mb-0 fw-bold small">${person.name}</p>
                    <p class="mb-0 text-muted" style="font-size: 0.65rem">${person.role}</p>
                </div>
            </label>
        `).join('');
    }

    const confirmTeamChangeBtn = document.getElementById('confirmTeamChangeBtn');
    const assignedTeamList = document.getElementById('assignedTeamList');

    if (confirmTeamChangeBtn && assignedTeamList) {
        confirmTeamChangeBtn.addEventListener('click', () => {
            const selectedStaff = document.querySelectorAll('#staffCatalog input:checked');
            if (selectedStaff.length === 0) {
                alert('Por favor selecciona al menos un miembro del equipo.');
                return;
            }

            assignedTeamList.innerHTML = ''; // Clear current team
            
            const selectedArray = Array.from(selectedStaff);
            const leaders = selectedArray.filter(cb => cb.dataset.role.toLowerCase().includes('líder') || cb.dataset.role.toLowerCase().includes('leader'));
            const staff = selectedArray.filter(cb => !cb.dataset.role.toLowerCase().includes('líder') && !cb.dataset.role.toLowerCase().includes('leader'));

            // Render Leaders
            if (leaders.length > 0) {
                const header = document.createElement('div');
                header.className = 'col-12 mt-0';
                header.innerHTML = '<p class="text-uppercase fw-bold text-primary mb-1" style="font-size: 0.65rem; letter-spacing: 0.05em;">Liderazgo</p>';
                assignedTeamList.appendChild(header);

                leaders.forEach(checkbox => {
                    const name = checkbox.dataset.name;
                    const role = checkbox.dataset.role;
                    const img = checkbox.dataset.img;
                    
                    const colEl = document.createElement('div');
                    colEl.className = 'col-md-6 col-lg-4';
                    colEl.innerHTML = `
                        <div class="d-flex align-items-center gap-3 p-2 bg-light rounded-3 h-100 border-start border-3 border-primary">
                            <img src="${img}" alt="${name}" class="rounded-3" style="width: 48px; height: 48px; object-fit: cover;">
                            <div class="flex-grow-1">
                                <p class="mb-0 fw-bold small">${name}</p>
                                <p class="mb-0 text-muted" style="font-size: 0.7rem">${role}</p>
                            </div>
                            <button class="btn btn-link p-0 text-primary"><span class="material-symbols-outlined">chat</span></button>
                        </div>
                    `;
                    assignedTeamList.appendChild(colEl);
                });
            }

            // Render Staff
            if (staff.length > 0) {
                const separator = document.createElement('div');
                separator.className = 'col-12 mt-4';
                separator.innerHTML = `
                    <hr class="my-0 opacity-10">
                    <p class="text-uppercase fw-bold text-muted mt-2 mb-1" style="font-size: 0.65rem; letter-spacing: 0.05em;">Staff Operativo</p>
                `;
                assignedTeamList.appendChild(separator);

                staff.forEach(checkbox => {
                    const name = checkbox.dataset.name;
                    const role = checkbox.dataset.role;
                    const img = checkbox.dataset.img;
                    
                    const colEl = document.createElement('div');
                    colEl.className = 'col-md-6 col-lg-4';
                    colEl.innerHTML = `
                        <div class="d-flex align-items-center gap-3 p-2 bg-light rounded-3 h-100">
                            <img src="${img}" alt="${name}" class="rounded-3" style="width: 48px; height: 48px; object-fit: cover;">
                            <div class="flex-grow-1">
                                <p class="mb-0 fw-bold small">${name}</p>
                                <p class="mb-0 text-muted" style="font-size: 0.7rem">${role}</p>
                            </div>
                            <button class="btn btn-link p-0 text-primary"><span class="material-symbols-outlined">chat</span></button>
                        </div>
                    `;
                    assignedTeamList.appendChild(colEl);
                });
            }

            // Close Modal
            const modalEl = document.getElementById('changeTeamModal');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) modalInstance.hide();
        });
    }
});

// Utility function for updating budget (example of backend sync simulation)
function updateBudgetProgress(value) {
    const progressBar = document.getElementById('budgetProgressBar');
    const budgetValue = document.getElementById('budgetValue');
    if (progressBar && budgetValue) {
        progressBar.style.width = value + '%';
        budgetValue.innerText = value + '%';
    }
}
