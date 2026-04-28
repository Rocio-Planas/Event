document.addEventListener('DOMContentLoaded', () => {
    console.log('Stratos Event Suite initialized');

    // Initialize Lucide icons if using the library
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Toggle Sidebar Mobile (Basic implementation)
    const setupMobileToggle = () => {
        // This is a placeholder for when we add a hamburger menu in HTML
    };

    // Tooltip initialization for Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Mock action for the optimization button
    const optimizeBtn = document.querySelector('.optimization-banner button');
    if (optimizeBtn) {
        optimizeBtn.addEventListener('click', () => {
            optimizeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Ejecutando...';
            setTimeout(() => {
                optimizeBtn.innerHTML = 'Reajuste Completado';
                optimizeBtn.classList.remove('btn-secondary-fixed');
                optimizeBtn.classList.add('btn-success');
                alert('El reajuste de recursos se ha completado con éxito.');
            }, 2000);
        });
    }
});
