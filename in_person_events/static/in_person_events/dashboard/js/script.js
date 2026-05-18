// EventHorizon Dashboard Logic
document.addEventListener('DOMContentLoaded', () => {
    // Add active state to nav links on click
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Simple animation for stat cards on load
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `all 0.5s ease ${index * 0.1}s`;
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    });

    // Announcement modal - Async send
    const sendBtn = document.getElementById('sendAnnouncementBtn');
    const announcementForm = document.getElementById('announcementForm');
    
    if (sendBtn && announcementForm) {
        sendBtn.addEventListener('click', function() {
            const titleInput = announcementForm.querySelector('input[name="title"]');
            const messageInput = announcementForm.querySelector('textarea[name="message"]');
            
            if (!titleInput.value.trim() || !messageInput.value.trim()) {
                showToast('El título y el mensaje son obligatorios.', 'error');
                return;
            }
            
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Enviando...';
            
            const formData = new FormData(announcementForm);
            const csrftoken = getCookie('csrftoken');
            
            fetch(`/eventos-presenciales/send-announcement/${dashboardEventId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message, 'success');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('announcementModal'));
                    modal.hide();
                    announcementForm.reset();
                } else {
                    showToast(data.error || 'Error al enviar el anuncio.', 'error');
                }
            })
            .catch(error => {
                showToast('Error de conexión.', 'error');
            })
            .finally(() => {
                sendBtn.disabled = false;
                sendBtn.innerHTML = 'Enviar';
            });
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
