// Dynamic field handling for StaffMember admin
(function() {
    'use strict';
    
    const userTypeSelect = document.getElementById('id_user_type');
    const eventSelect = document.getElementById('id_event');
    const zoneField = document.querySelector('[id*="zone"]');
    const activityField = document.querySelector('[id*="activity"]');
    const roleField = document.querySelector('[id*="role"]');
    
    function updateFields() {
        const userType = userTypeSelect ? userTypeSelect.value : '';
        const eventId = eventSelect ? eventSelect.value : '';
        
        if (userType === 'ponente') {
            // Show activity field, hide zone and role
            if (zoneField) {
                zoneField.parentElement.style.display = 'none';
            }
            if (roleField) {
                roleField.parentElement.parentElement.style.display = 'none';
            }
            if (activityField) {
                activityField.parentElement.style.display = 'block';
            }
        } else if (userType === 'staff') {
            // Show zone field, hide activity
            if (zoneField) {
                zoneField.parentElement.style.display = 'block';
            }
            if (roleField) {
                roleField.parentElement.parentElement.style.display = 'block';
            }
            if (activityField) {
                activityField.parentElement.style.display = 'none';
            }
        } else {
            // Default: show both
            if (zoneField) {
                zoneField.parentElement.style.display = 'block';
            }
            if (roleField) {
                roleField.parentElement.parentElement.style.display = 'block';
            }
            if (activityField) {
                activityField.parentElement.style.display = 'none';
            }
        }
    }
    
    if (userTypeSelect) {
        userTypeSelect.addEventListener('change', updateFields);
    }
    
    // Initial run
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateFields);
    } else {
        updateFields();
    }
})();