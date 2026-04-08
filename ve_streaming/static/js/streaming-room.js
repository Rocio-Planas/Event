// streaming-room.js (versión solo para grabación y satisfacción)
class StreamingRoomExtras {
    constructor(eventSlug) {
        this.eventSlug = eventSlug;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.init();
    }

    init() {
        this.bindRecording();
        this.bindSatisfaction();
    }

    bindRecording() {
        const recordBtn = document.getElementById('sr-record-btn');
        if (recordBtn) {
            recordBtn.addEventListener('click', () => this.toggleRecording());
        }
    }

    async toggleRecording() {
        const btn = document.getElementById('sr-record-btn');
        const icon = btn.querySelector('i');
        const textSpan = btn.querySelector('span');

        if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
                this.mediaRecorder = new MediaRecorder(stream);
                this.recordedChunks = [];

                this.mediaRecorder.ondataavailable = (e) => {
                    if (e.data.size > 0) this.recordedChunks.push(e.data);
                };

                this.mediaRecorder.onstop = () => {
                    const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `grabacion-${this.eventSlug}.webm`;
                    a.click();

                    icon.className = 'bi bi-camera-video';
                    textSpan.textContent = 'Grabar pantalla';
                    btn.classList.remove('btn-danger');
                    btn.classList.add('btn-outline-secondary');
                };

                this.mediaRecorder.start();
                icon.className = 'bi bi-stop-circle sr-recording-active';
                textSpan.textContent = 'Detener grabación';
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-danger');

            } catch (err) {
                console.error("Error al grabar:", err);
                alert("No se pudo iniciar la grabación. Asegúrate de dar permisos.");
            }
        } else {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }

    bindSatisfaction() {
        // Satisfacción (emoji)
        const satisfactionBtn = document.getElementById('sr-satisfaction-btn');
        if (satisfactionBtn) {
            satisfactionBtn.addEventListener('click', () => {
                if (window.room && window.room.sendSatisfaction) {
                    window.room.sendSatisfaction(5);
                } else {
                    console.warn("Polling room no disponible para satisfacción");
                }
            });
        }

        // Satisfacción (estrellas)
        const stars = document.querySelectorAll('.sr-star-rating input');
        stars.forEach(star => {
            star.addEventListener('change', (e) => {
                if (window.room && window.room.sendSatisfaction) {
                    window.room.sendSatisfaction(parseInt(e.target.value));
                }
            });
        });
    }
}

// Esperar a que el otro script (streaming-polling) haya definido window.room
// y luego agregar las funcionalidades extra
document.addEventListener('DOMContentLoaded', () => {
    // Esperar un poco para asegurar que StreamingPolling se haya inicializado
    setTimeout(() => {
        if (window.room) {
            // Añadir métodos de grabación y satisfacción al objeto existente
            const extras = new StreamingRoomExtras(window.room.eventSlug);
            window.room.toggleRecording = extras.toggleRecording.bind(extras);
            // Si quieres mantener la referencia al botón de grabación, ya se bindeó internamente
        } else {
            console.warn("StreamingPolling no se ha inicializado aún, reintentando...");
        }
    }, 100);
});