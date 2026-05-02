// streaming-room-sync.js
// Sincroniza la altura del chat con la columna izquierda

(function() {
    'use strict';
    
    function syncChatHeight() {
        var leftCol = document.querySelector('.row.g-4 > .col-lg-8');
        var chatContainer = document.querySelector('.sr-chat-container');
        var metricsContainer = document.getElementById('sr-metrics-container');
        
        if (!leftCol || !chatContainer) return;
        
        // Medir altura real de la columna izquierda
        var leftHeight = leftCol.getBoundingClientRect().height;
        
        // Medir métricas
        var metricsHeight = metricsContainer ? metricsContainer.getBoundingClientRect().height : 0;
        var metricsMargin = metricsContainer ? 16 : 0;
        
        // Calcular altura del chat
        var chatHeight = leftHeight - metricsHeight - metricsMargin;
        chatHeight = Math.max(chatHeight, 300); // Mínimo 300px
        
        // Aplicar
        chatContainer.style.height = chatHeight + 'px';
        chatContainer.style.maxHeight = chatHeight + 'px';
    }
    
    // Ejecutar al cargar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncChatHeight);
    } else {
        syncChatHeight();
    }
    
    // Re-calcular al redimensionar (con delay)
    var resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(syncChatHeight, 200);
    });
    
    // Observar cambios en la columna izquierda
    var leftCol = document.querySelector('.row.g-4 > .col-lg-8');
    if (leftCol && window.ResizeObserver) {
        new ResizeObserver(syncChatHeight).observe(leftCol);
    }
    
    // Exponer globalmente por si se necesita llamar manualmente
    window.syncChatHeight = syncChatHeight;
})();