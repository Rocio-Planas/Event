// streaming-room.js - Versión definitiva que NO rompe nada
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
            // Eliminar listeners existentes para evitar duplicados
            const newBtn = recordBtn.cloneNode(true);
            recordBtn.parentNode.replaceChild(newBtn, recordBtn);
            newBtn.addEventListener('click', () => this.toggleRecording());
        }
    }

    async toggleRecording() {
        const btn = document.getElementById('sr-record-btn');
        if (!btn) return;
        
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
                    URL.revokeObjectURL(url);

                    if (icon) icon.className = 'bi bi-camera-video';
                    if (textSpan) textSpan.textContent = 'Grabar pantalla';
                    btn.classList.remove('btn-danger');
                    btn.classList.add('btn-outline-secondary');
                };

                this.mediaRecorder.start();
                if (icon) icon.className = 'bi bi-stop-circle sr-recording-active';
                if (textSpan) textSpan.textContent = 'Detener grabación';
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
        // SATISFACCIÓN EMOJI
        const satisfactionBtn = document.getElementById('sr-satisfaction-btn');
        if (satisfactionBtn) {
            // Eliminar listeners existentes
            const newBtn = satisfactionBtn.cloneNode(true);
            satisfactionBtn.parentNode.replaceChild(newBtn, satisfactionBtn);
            newBtn.addEventListener('click', () => {
                console.log("Emoji satisfaction clicked");
                if (window.room && typeof window.room.sendSatisfaction === 'function') {
                    window.room.sendSatisfaction(5);
                } else {
                    console.warn("sendSatisfaction no disponible");
                }
            });
        }

        // SATISFACCIÓN ESTRELLAS - CRÍTICO
        const starsContainer = document.querySelector('.sr-star-rating');
        if (starsContainer) {
            // Eliminar todos los inputs existentes y recrearlos para asegurar listeners frescos
            const inputs = starsContainer.querySelectorAll('input');
            inputs.forEach(input => {
                const newInput = input.cloneNode(true);
                input.parentNode.replaceChild(newInput, input);
                
                newInput.addEventListener('change', (e) => {
                    const rating = parseInt(e.target.value);
                    console.log(`Estrella seleccionada: ${rating}`);
                    if (window.room && typeof window.room.sendSatisfaction === 'function') {
                        window.room.sendSatisfaction(rating);
                        // Feedback visual opcional
                        const labels = starsContainer.querySelectorAll('label');
                        labels.forEach((label, idx) => {
                            if (idx < rating) {
                                label.style.color = '#fbbf24';
                            }
                        });
                    } else {
                        console.error("sendSatisfaction NO está disponible en window.room");
                    }
                });
            });
        }
    }
}

// Inicialización - NO interferir con window.room existente
document.addEventListener('DOMContentLoaded', () => {
    console.log("Inicializando StreamingRoomExtras...");
    
    // Verificar que window.room ya existe
    if (window.room && typeof window.room.sendSatisfaction === 'function') {
        console.log("window.room detectado correctamente, sendSatisfaction disponible");
        new StreamingRoomExtras(window.room.eventSlug || window.eventSlug);
    } else {
        // Esperar a que window.room esté disponible
        const checkInterval = setInterval(() => {
            if (window.room && typeof window.room.sendSatisfaction === 'function') {
                console.log("window.room ahora disponible");
                clearInterval(checkInterval);
                new StreamingRoomExtras(window.room.eventSlug || window.eventSlug);
            } else {
                console.log("Esperando window.room...");
            }
        }, 100);
        
        // Timeout por si acaso
        setTimeout(() => {
            clearInterval(checkInterval);
            if (!window.room || typeof window.room.sendSatisfaction !== 'function') {
                console.error("No se pudo detectar window.room con sendSatisfaction");
            }
        }, 5000);
    }
});