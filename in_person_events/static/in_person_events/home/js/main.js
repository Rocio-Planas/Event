document.addEventListener('DOMContentLoaded', () => {
    const createEventBtn = document.getElementById('createEventBtn');
    
    if (createEventBtn) {
        createEventBtn.addEventListener('click', () => {
            console.log('Crear Evento clicked');
            // Add your event creation logic here
            alert('Iniciando creación de evento...');
        });
    }
});
