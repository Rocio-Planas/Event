(function() {
    const eventId = window.EVENT_ID;
    if (!eventId) {
        console.warn("No EVENT_ID disponible");
        return;
    }

    function getCsrfToken() {
        let cookieValue = null;
        const name = 'csrftoken';
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
        return cookieValue || '';
    }

    // Heartbeat cada 30 segundos
    setInterval(() => {
        fetch(`/eventos/evento/${eventId}/heartbeat/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        }).catch(err => console.warn("Heartbeat error:", err));
    }, 30000);

    // Actualizar métricas cada 5 segundos
    function updateMetrics() {
        fetch(`/eventos/evento/${eventId}/metrics/`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                document.getElementById('metric-online').innerText = data.active_viewers || 0;
                document.getElementById('metric-online-badge').innerText = data.active_viewers || 0;
                document.getElementById('metric-messages').innerText = data.total_messages || 0;
                document.getElementById('metric-hands').innerText = data.total_hands || 0;
                document.getElementById('metric-participation').innerText = (data.participation_percent || 0) + '%';
                document.getElementById('metric-time').innerText = data.elapsed_time || '00:00:00';
                document.getElementById('metric-satisfaction').innerText = data.average_satisfaction || 0;
            })
            .catch(err => console.error("Error actualizando métricas:", err));
    }
    updateMetrics();
    setInterval(updateMetrics, 5000);
})();