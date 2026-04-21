document.addEventListener('DOMContentLoaded', () => {
    // Switch Toggling Logic
    const switches = document.querySelectorAll('.custom-switch');
    switches.forEach(sw => {
        sw.addEventListener('click', () => {
            sw.classList.toggle('active');
        });
    });

    // Form submission simulation
    const saveBtn = document.querySelector('.btn-primary-custom');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            alert('Configuración guardada correctamente.');
        });
    }

    const discardBtn = document.querySelector('.btn-discard');
    if (discardBtn) {
        discardBtn.addEventListener('click', () => {
            if (confirm('¿Estás seguro de descartar los cambios?')) {
                location.reload();
            }
        });
    }
});
