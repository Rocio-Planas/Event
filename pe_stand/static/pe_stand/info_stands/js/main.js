// currentStandId is set in the template via <script>var currentStandId = {{ stand.id }};</script>

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function addSelectedStaff() {
    var selectedCheckboxes = document.querySelectorAll('.staff-checkbox:checked');
    var selectedUsers = Array.from(selectedCheckboxes).map(function(cb) {
        return { user_id: cb.value, role: cb.dataset.role };
    });
    
    if (selectedUsers.length === 0) return;
    
    var btn = document.getElementById('confirmAddStaffBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Añadiendo...';
    
    fetch('/stands/api/' + currentStandId + '/add-staff/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ users: selectedUsers })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            location.reload();
        } else {
            showToast(data.error || 'Error desconocido', 'error');
            btn.disabled = false;
            btn.textContent = 'Aceptar';
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
        btn.disabled = false;
        btn.textContent = 'Aceptar';
    });
}

function openNotificationModal(userId, userName) {
    document.getElementById('notificationUserId').value = userId;
    document.getElementById('notificationUserName').textContent = userName;
    var modal = new bootstrap.Modal(document.getElementById('notificationModal'));
    modal.show();
}

function sendNotification() {
    var userId = document.getElementById('notificationUserId').value;
    var title = document.getElementById('notificationTitle').value;
    var message = document.getElementById('notificationMessage').value;
    
    if (!title || !message) {
        showToast('Completa todos los campos', 'error');
        return;
    }
    
    var btn = document.getElementById('sendNotificationBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Enviando...';
    
    fetch('/comunicacion/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            user_id: userId,
            title: title,
            message: message
        })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            showToast('Notificación enviada', 'success');
            bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide();
            document.getElementById('notificationTitle').value = '';
            document.getElementById('notificationMessage').value = '';
        } else {
            showToast(data.error || 'Error al enviar', 'error');
        }
        btn.disabled = false;
        btn.textContent = 'Enviar';
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
        btn.disabled = false;
        btn.textContent = 'Enviar';
    });
}

document.addEventListener('change', function(e) {
    if (e.target.classList.contains('staff-checkbox')) {
        var anyChecked = document.querySelectorAll('.staff-checkbox:checked').length > 0;
        document.getElementById('confirmAddStaffBtn').disabled = !anyChecked;
    }
    if (e.target.classList.contains('activity-checkbox')) {
        var anyChecked = document.querySelectorAll('.activity-checkbox:checked').length > 0;
        document.getElementById('confirmAssignActivityBtn').disabled = !anyChecked;
    }
    if (e.target.classList.contains('resource-checkbox')) {
        var anyChecked = document.querySelectorAll('.resource-checkbox:checked').length > 0;
        document.getElementById('confirmAddBtn').disabled = !anyChecked;
    }
});

function removeStaffFromStand(userId, userName) {
    var userIdInput = document.querySelector('#removeStaffUserId');
    var userNameSpan = document.querySelector('#removeStaffModal #removeStaffUserName');
    
    if (userIdInput) {
        userIdInput.value = userId;
    }
    
    if (userNameSpan) {
        userNameSpan.textContent = userName;
    }
    
    var modalEl = document.getElementById('removeStaffModal');
    if (modalEl) {
        var modal = new bootstrap.Modal(modalEl);
        modal.show();
    } else {
        showToast('Error: Modal no encontrado', 'error');
    }
}

function confirmRemoveStaff() {
    var userId = document.getElementById('removeStaffUserId').value;

    fetch('/stands/api/' + currentStandId + '/remove-staff/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('removeStaffModal')).hide();
            var row = document.querySelector('[data-staff-id="' + userId + '"]');
            if (row) row.remove();
            var container = document.getElementById('teamContainer');
            var remainingStaff = container ? container.querySelectorAll('[data-staff-id]').length : 0;
            var emptyState = document.getElementById('teamEmptyState');
            if (remainingStaff === 0 && emptyState) {
                emptyState.style.display = 'block';
            }
            showToast('Personal removido correctamente', 'success');
        } else {
            showToast(data.error || 'Error al remover', 'error');
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
    });
}

function addSelectedActivities() {
    var selectedCheckboxes = document.querySelectorAll('.activity-checkbox:checked');
    var selectedActivities = Array.from(selectedCheckboxes).map(function(cb) {
        return { activity_id: cb.value };
    });
    
    if (selectedActivities.length === 0) return;
    
    var btn = document.getElementById('confirmAssignActivityBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Asignando...';
    
    fetch('/stands/api/' + currentStandId + '/add-activities/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ activities: selectedActivities })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            location.reload();
        } else {
            showToast(data.error || 'Error desconocido', 'error');
            btn.disabled = false;
            btn.textContent = 'Asignar';
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
        btn.disabled = false;
        btn.textContent = 'Asignar';
    });
}

function addSelectedResources() {
    var selectedCheckboxes = document.querySelectorAll('.resource-checkbox:checked');
    var selectedItems = Array.from(selectedCheckboxes).map(function(cb) {
        return cb.value;
    });

    if (selectedItems.length === 0) return;

    var btn = document.getElementById('confirmAddBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Añadiendo...';

    fetch('/stands/api/' + currentStandId + '/add-resources/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ item_ids: selectedItems })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            location.reload();
        } else {
            showToast('No se pudieron agregar los recursos', 'error');
            btn.disabled = false;
            btn.textContent = 'Añadir Seleccionados';
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
        btn.disabled = false;
        btn.textContent = 'Añadir Seleccionados';
    });
}

function updateQuantity(assignmentId, delta, maxStock) {
    var currentQtySpan = document.querySelector('[data-assignment-id="' + assignmentId + '"] .assigned-val');
    var currentQty = parseInt(currentQtySpan.textContent);
    var newQty = currentQty + delta;
    
    if (newQty < 0 || newQty > maxStock) {
        return;
    }

    fetch('/stands/' + currentStandId + '/update-resource/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ assignment_id: assignmentId, quantity: newQty })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            location.reload();
        }
    })
    .catch(function(error) {
        showToast('Error al actualizar cantidad', 'error');
    });
}

function openActivityDetails(activityId, title, description, startDate, endDate, duration, location, speakerName, speakerEmail, status) {
    document.getElementById('detailActivityId').value = activityId;
    document.getElementById('detailActivityTitle').textContent = title;
    document.getElementById('detailActivityDescription').textContent = description || 'Descripción no disponible';
    document.getElementById('detailActivityTime').textContent = 'Inicio: ' + startDate;
    document.getElementById('detailActivityDate').textContent = 'Fin: ' + endDate;
    document.getElementById('detailActivityDuration').textContent = duration + ' min';
    document.getElementById('detailActivityLocation').textContent = location || 'Sin ubicación';

    var statusLabel = 'Programada';
    var statusStyle = 'background-color: rgba(0, 87, 205, 0.1); color: var(--primary);';
    if (status === 'en_curso') {
        statusLabel = 'En curso';
        statusStyle = 'background-color: rgba(248, 169, 0, 0.1); color: var(--warning);';
    } else if (status === 'completada') {
        statusLabel = 'Completada';
        statusStyle = 'background-color: rgba(6, 167, 125, 0.1); color: var(--success);';
    } else if (status === 'cancelada') {
        statusLabel = 'Cancelada';
        statusStyle = 'background-color: rgba(220, 38, 38, 0.1); color: var(--error);';
    }
    var statusElement = document.getElementById('detailActivityStatus');
    statusElement.textContent = statusLabel;
    statusElement.className = 'badge fw-bold';
    statusElement.style.cssText = statusStyle;

    if (speakerName) {
        document.getElementById('detailActivitySpeaker').textContent = speakerName;
        document.getElementById('detailActivitySpeakerEmail').textContent = speakerEmail || '';
    } else {
        document.getElementById('detailActivitySpeaker').textContent = 'Sin asignar';
        document.getElementById('detailActivitySpeakerEmail').textContent = '';
    }

    if (!location) {
        document.getElementById('detailActivityLocation').textContent = 'No asignada';
    }

    var modal = new bootstrap.Modal(document.getElementById('activityDetailsModal'));
    modal.show();
}

function openEditResourceModal(assignmentId, itemName, itemCategory, currentDetails, currentRequired) {
    document.getElementById('editAssignmentId').value = assignmentId;
    document.getElementById('editResourceName').textContent = itemName + ' (' + itemCategory + ')';
    document.getElementById('editReqInput').value = currentDetails || '';
    document.getElementById('editRequiredInput').value = currentRequired || 0;
    var modal = new bootstrap.Modal(document.getElementById('editResourceModal'));
    modal.show();
}

function saveResourceEdit() {
    var assignmentId = document.getElementById('editAssignmentId').value;
    var details = document.getElementById('editReqInput').value;
    var requiredQty = document.getElementById('editRequiredInput').value;
    
    if (details.length > 100) {
        showToast('El texto no puede exceder 100 caracteres', 'error');
        return;
    }
    
    var btn = document.getElementById('saveResourceEditBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Guardando...';
    
    fetch('/stands/' + currentStandId + '/update-resource/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ assignment_id: assignmentId, details: details, required_quantity: parseInt(requiredQty) || 0 })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            location.reload();
        } else {
            showToast(data.error || 'Error al guardar', 'error');
        }
    })
    .catch(function(error) {
        showToast('Error al guardar', 'error');
    })
    .finally(function() {
        btn.disabled = false;
        btn.textContent = 'Guardar Cambios';
    });
}

function openRemoveResourceModal(assignmentId) {
    document.getElementById('removeResourceAssignmentId').value = assignmentId;
    var modal = new bootstrap.Modal(document.getElementById('removeResourceModal'));
    modal.show();
}

function confirmRemoveResource() {
    var assignmentId = document.getElementById('removeResourceAssignmentId').value;
    
    fetch('/stands/' + currentStandId + '/delete-resource/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ assignment_id: assignmentId })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('removeResourceModal')).hide();
            location.reload();
        } else {
            showToast(data.error || 'Error al eliminar', 'error');
        }
    })
    .catch(function(error) {
        showToast('Error al eliminar recurso', 'error');
    });
}

function adjustQuantity(assignmentId, delta, button) {
    var td = button.closest('td');
    var span = td.querySelector('span');
    var currentText = span.textContent.trim();
    var parts = currentText.split(' / ');
    var currentQty = parseInt(parts[0]) || 0;
    var requiredQty = parseInt(parts[1]) || 0;
    
    var newQty = Math.max(0, currentQty + delta);
    
    fetch('/stands/' + currentStandId + '/update-resource/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ assignment_id: assignmentId, quantity: newQty })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            location.reload();
        } else {
            showToast(data.error || 'Error al actualizar cantidad', 'error');
        }
    })
    .catch(function(error) {
        showToast('Error al actualizar cantidad', 'error');
    });
}

function openMoveModal() {
    var activityId = document.getElementById('detailActivityId').value;
    if (!activityId) {
        showToast('Selecciona una actividad primero', 'error');
        return;
    }
    var detailsModal = bootstrap.Modal.getInstance(document.getElementById('activityDetailsModal'));
    if (detailsModal) {
        detailsModal.hide();
    }
    var moveModal = new bootstrap.Modal(document.getElementById('moveActivityModal'));
    moveModal.show();
}

function moveActivityToStand() {
    var activityId = document.getElementById('detailActivityId').value;
    var targetStandId = document.getElementById('moveStandSelect').value;

    if (!targetStandId) {
        showToast('Selecciona un stand destino', 'error');
        return;
    }

    var btn = document.querySelector('#moveActivityModal .btn-signature');
    btn.disabled = true;
    btn.textContent = 'Moviendo...';

    fetch('/stands/api/' + currentStandId + '/move-activity/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ activity_id: activityId, target_stand_id: targetStandId })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            var moveModal = bootstrap.Modal.getInstance(document.getElementById('moveActivityModal'));
            if (moveModal) moveModal.hide();
            var detailsModal = bootstrap.Modal.getInstance(document.getElementById('activityDetailsModal'));
            if (detailsModal) detailsModal.hide();
            removeActivityCard(activityId);
            showToast('Actividad movida correctamente', 'success');
        } else {
            showToast(data.error || 'Error al mover la actividad', 'error');
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
    })
    .finally(function() {
        btn.disabled = false;
        btn.textContent = 'Mover';
    });
}

function openRemoveActivityModal() {
    var activityId = document.getElementById('detailActivityId').value;
    if (!activityId) {
        showToast('Selecciona una actividad primero', 'error');
        return;
    }
    document.getElementById('removeActivityId').value = activityId;
    var detailsModal = bootstrap.Modal.getInstance(document.getElementById('activityDetailsModal'));
    if (detailsModal) detailsModal.hide();
    var modal = new bootstrap.Modal(document.getElementById('removeActivityModal'));
    modal.show();
}

function confirmDeleteActivityFromStand() {
    var activityId = document.getElementById('removeActivityId').value;

    var btn = document.querySelector('#removeActivityModal .btn-danger');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Quitando...';

    fetch('/stands/api/' + currentStandId + '/remove-activity/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ activity_id: activityId })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('removeActivityModal')).hide();
            removeActivityCard(activityId);
            showToast('Actividad removida correctamente', 'success');
        } else {
            showToast(data.error || 'Error al quitar la actividad del stand', 'error');
            btn.disabled = false;
            btn.textContent = 'Quitar';
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
        btn.disabled = false;
        btn.textContent = 'Quitar';
    });
}

function removeActivityCard(activityId) {
    var card = document.querySelector('[data-activity-id="' + activityId + '"]');
    if (card) {
        card.remove();
    }
    var container = document.getElementById('activitiesContainer');
    if (container && container.querySelectorAll('.activity-card').length === 0) {
        container.style.display = 'none';
        var emptyDiv = document.getElementById('activitiesEmptyState');
        if (emptyDiv) {
            emptyDiv.style.display = 'block';
        }
    }
}

function filterActivities() {
    var searchInput = document.getElementById('searchActivities');
    var filter = searchInput.value.toLowerCase();
    var activityCards = document.querySelectorAll('.activity-card');
    
    activityCards.forEach(function(card) {
        var title = card.getAttribute('data-title') || '';
        var titleLower = title.toLowerCase();
        
        if (titleLower.indexOf(filter) !== -1) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal').forEach(function(modal) {
        if (!modal.hasAttribute('inert')) {
            modal.setAttribute('inert', '');
        }

        modal.addEventListener('shown.bs.modal', function() {
            modal.removeAttribute('inert');
        });

        modal.addEventListener('hidden.bs.modal', function() {
            if (modal.contains(document.activeElement)) {
                document.activeElement.blur();
            }
            modal.setAttribute('inert', '');
        });
    });
});

function openEditStandModal() {
    var standContainer = document.querySelector('.p-4[data-stand-id]');
    if (standContainer) {
        var name = standContainer.getAttribute('data-stand-name');
        var location = standContainer.getAttribute('data-stand-location');
        var capacity = standContainer.getAttribute('data-stand-capacity');
        
        if (name) document.getElementById('editStandName').value = name;
        if (location) document.getElementById('editStandLocation').value = location;
        if (capacity) document.getElementById('editStandCapacity').value = capacity;
        
        if (name && location && capacity) {
            return;
        }
    }
    
    var h2 = document.querySelector('h3.h2');
    if (h2) {
        document.getElementById('editStandName').value = h2.textContent.trim();
    }
    
    var infoContainer = document.querySelector('.d-flex.gap-3');
    if (infoContainer) {
        var spans = infoContainer.querySelectorAll(':scope > span');
        for (var i = 0; i < spans.length; i++) {
            var spanText = spans[i].textContent;
            if (spanText.includes('location_on')) {
                var locText = spanText.replace('location_on', '').trim();
                document.getElementById('editStandLocation').value = locText;
            }
            if (spanText.includes('groups') || spanText.includes('Capacidad')) {
                var match = spanText.match(/(\d+)/);
                if (match) {
                    document.getElementById('editStandCapacity').value = match[1];
                }
            }
        }
    }
}

function saveStandEdit() {
    var name = document.getElementById('editStandName').value.trim();
    var location = document.getElementById('editStandLocation').value.trim();
    var capacity = document.getElementById('editStandCapacity').value.trim();

    if (!name || !location || !capacity) {
        showToast('Completa todos los campos.', 'error');
        return;
    }

    var btn = document.getElementById('saveStandEditBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Guardando...';

    fetch('/stands/api/stands/' + currentStandId + '/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ name: name, location: location, capacity: parseInt(capacity) })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            document.querySelector('h3.h2').textContent = data.stand.name;
            var standDiv = document.querySelector('[data-stand-id]');
            if (standDiv) {
                var spans = standDiv.querySelectorAll('.d-flex.gap-3 span');
                if (spans[0]) spans[0].innerHTML = '<span class="material-symbols-outlined fs-6">location_on</span> ' + data.stand.location;
                if (spans[1]) spans[1].innerHTML = '<span class="material-symbols-outlined fs-6">groups</span> Capacidad: ' + data.stand.capacity;
            }
            bootstrap.Modal.getInstance(document.getElementById('editStandModal')).hide();
            showToast('Stand actualizado correctamente', 'success');
        } else {
            showToast(data.error || 'Error al guardar', 'error');
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
    })
    .finally(function() {
        btn.disabled = false;
        btn.textContent = 'Guardar Cambios';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    var editStandModalEl = document.getElementById('editStandModal');
    if (editStandModalEl) {
        editStandModalEl.addEventListener('shown.bs.modal', openEditStandModal);
    }
});

function openDeleteStandModal() {
    var modalEl = document.getElementById('deleteStandModal');
    if (modalEl) {
        var modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}

function confirmDeleteStand() {
    var btn = document.getElementById('confirmDeleteStandBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Eliminando...';

    fetch('/stands/api/stands/' + currentStandId + '/delete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            window.location.href = '/stands/' + data.event_id + '/';
        } else {
            showToast(data.error || 'Error al eliminar', 'error');
            btn.disabled = false;
            btn.innerHTML = 'Sí, eliminar';
        }
    })
    .catch(function(error) {
        showToast('Error de conexión', 'error');
        btn.disabled = false;
        btn.innerHTML = 'Sí, eliminar';
    });
}