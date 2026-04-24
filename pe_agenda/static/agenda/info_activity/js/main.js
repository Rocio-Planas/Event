/**
 * Stratos Event Suite - Main Logic
 * Este archivo contiene la lógica básica para la interfaz de usuario.
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Stratos Dashboard Initialized');

    // Ejemplo: Manejo de clics en el FAB para expansión futura
    const fabButton = document.querySelector('.fab');
    if (fabButton) {
        fabButton.addEventListener('click', () => {
            console.log('Abrir modal de nueva actividad');
        });
    }

    // Manejo de navegación (Simulación de estado activo)
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});
