// Info Activity Assistant - JavaScript
// Handles interactions for the activity detail page

document.addEventListener('DOMContentLoaded', function() {
    // Add any interactive functionality here

    // Example: Copy activity link functionality
    const shareButton = document.querySelector('button:has(.material-symbols-outlined:contains("share"))');
    if (shareButton) {
        shareButton.addEventListener('click', function() {
            const url = window.location.href;
            navigator.clipboard.writeText(url).then(function() {
                // Simple feedback - you could show a toast notification here
                alert('Enlace copiado al portapapeles');
            }).catch(function(err) {
                console.error('Error al copiar: ', err);
            });
        });
    }

    // Add reminder functionality
    const reminderButton = document.querySelector('button:has(.material-symbols-outlined:contains("notifications_active"))');
    if (reminderButton) {
        reminderButton.addEventListener('click', function() {
            // This would typically integrate with a notification system
            alert('Recordatorio configurado para esta actividad');
        });
    }
});