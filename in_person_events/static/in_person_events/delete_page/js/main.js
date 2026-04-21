document.addEventListener('DOMContentLoaded', () => {
    console.log('Stratos Event Suite ready');
    
    // Aquí puedes añadir interactividad JS funcional
    const backBtn = document.querySelector('.btn-primary-custom');
    if (backBtn) {
        backBtn.addEventListener('click', (e) => {
            console.log('Navegando a la lista de eventos...');
            // En Django esto sería un enlace real: a href="{% url 'event_list' %}"
        });
    }
});
