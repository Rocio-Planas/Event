
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
        chatHeight = Math.max(chatHeight, 300); 
        
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
    
    var resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(syncChatHeight, 200);
    });
    
    var leftCol = document.querySelector('.row.g-4 > .col-lg-8');
    if (leftCol && window.ResizeObserver) {
        new ResizeObserver(syncChatHeight).observe(leftCol);
    }
    
    window.syncChatHeight = syncChatHeight;
})();