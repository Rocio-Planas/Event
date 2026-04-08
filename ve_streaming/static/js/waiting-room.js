/**
 * waiting-room.js
 * Controla la cuenta regresiva exacta y habilita el botón solo cuando el evento comienza.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Elementos DOM
    const daysEl = document.getElementById('days');
    const hoursEl = document.getElementById('hours');
    const minutesEl = document.getElementById('minutes');
    const secondsEl = document.getElementById('seconds');
    const enterBtn = document.getElementById('enter-room-btn');
    const copyBtn = document.getElementById('copy-btn');
    const statusMsg = document.getElementById('status-message');
    const eventLinkEl = document.getElementById('event-link');

    // Variables globales definidas en el template
    if (typeof startTimestamp === 'undefined') {
        console.error('startTimestamp no está definida');
        return;
    }
    if (typeof liveUrl === 'undefined') {
        console.error('liveUrl no está definida');
        return;
    }

    let countdownInterval = null;

    function updateCountdown() {
        const now = Date.now();
        const diff = startTimestamp - now;

        if (diff <= 0) {
            // Evento ya comenzó
            daysEl.innerText = '00';
            hoursEl.innerText = '00';
            minutesEl.innerText = '00';
            secondsEl.innerText = '00';
            if (enterBtn.disabled) {
                enterBtn.disabled = false;
                statusMsg.innerHTML = '¡El evento ya comenzó! Haz clic para ingresar.';
                statusMsg.classList.remove('text-muted');
                statusMsg.classList.add('text-success', 'fw-bold');
            }
            if (countdownInterval) {
                clearInterval(countdownInterval);
                countdownInterval = null;
            }
            return;
        }

        // Cálculos correctos (diff está en milisegundos)
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        daysEl.innerText = String(days).padStart(2, '0');
        hoursEl.innerText = String(hours).padStart(2, '0');
        minutesEl.innerText = String(minutes).padStart(2, '0');
        secondsEl.innerText = String(seconds).padStart(2, '0');

        // Botón deshabilitado mientras no sea la hora
        if (!enterBtn.disabled) {
            enterBtn.disabled = true;
            statusMsg.innerHTML = 'La sala se abrirá cuando llegue la hora del evento.';
            statusMsg.classList.add('text-muted');
            statusMsg.classList.remove('text-success', 'fw-bold');
        }
    }

    // Copiar enlace con feedback visual
    if (copyBtn && eventLinkEl) {
        copyBtn.addEventListener('click', function () {
            const textToCopy = eventLinkEl.innerText;
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalIcon = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="bi bi-check2"></i>';
                copyBtn.classList.add('copy-success');
                setTimeout(() => {
                    copyBtn.innerHTML = originalIcon;
                    copyBtn.classList.remove('copy-success');
                }, 2000);
            }).catch(err => {
                console.error('Error al copiar:', err);
                alert('No se pudo copiar el enlace');
            });
        });
    }

    // Redirección a la sala
    if (enterBtn) {
        enterBtn.addEventListener('click', function () {
            if (!enterBtn.disabled) {
                window.location.href = liveUrl;
            }
        });
    }

    // Iniciar la cuenta regresiva
    updateCountdown();
    countdownInterval = setInterval(updateCountdown, 1000);
});