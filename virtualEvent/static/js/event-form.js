// static/js/event-form.js
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const imageInput = document.getElementById('evImageInput');
    const imagePreview = document.getElementById('evImagePreview');
    const previewContainer = document.getElementById('evPreviewContainer');
    const removeImageBtn = document.getElementById('evRemoveImage');
    const accessRadios = document.getElementsByName('access_type');
    const invitationsGroup = document.getElementById('evInvitationsGroup');
    const categorySelect = document.getElementById('id_category');
    const customCategoryGroup = document.getElementById('evCustomCategoryGroup');

    /**
     * Previsualización de imagen
     */
    function handleImagePreview(event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                previewContainer.classList.remove('d-none');
                const dropZoneContent = document.getElementById('evDropZoneContent');
                if (dropZoneContent) dropZoneContent.classList.add('d-none');
            };
            reader.readAsDataURL(file);
        }
    }

    function removeImage() {
        imageInput.value = '';
        imagePreview.src = '';
        previewContainer.classList.add('d-none');
        const dropZoneContent = document.getElementById('evDropZoneContent');
        if (dropZoneContent) dropZoneContent.classList.remove('d-none');
    }

    /**
     * Mostrar/ocultar campo de invitaciones según tipo de acceso
     */
    function toggleInvitations() {
        const selectedAccess = Array.from(accessRadios).find(r => r.checked).value;
        if (selectedAccess === 'private') {
            invitationsGroup.classList.remove('d-none');
        } else {
            invitationsGroup.classList.add('d-none');
        }
    }

    /**
     * Mostrar/ocultar campo de categoría personalizada
     */
    function toggleCustomCategory() {
        if (categorySelect && customCategoryGroup) {
            if (categorySelect.value === 'custom') {
                customCategoryGroup.classList.remove('d-none');
                const customInput = document.getElementById('id_custom_category');
                if (customInput) customInput.setAttribute('required', 'required');
            } else {
                customCategoryGroup.classList.add('d-none');
                const customInput = document.getElementById('id_custom_category');
                if (customInput) customInput.removeAttribute('required');
            }
        }
    }

    // Asignar eventos
    if (imageInput) imageInput.addEventListener('change', handleImagePreview);
    if (removeImageBtn) removeImageBtn.addEventListener('click', removeImage);
    accessRadios.forEach(radio => radio.addEventListener('change', toggleInvitations));
    if (categorySelect) categorySelect.addEventListener('change', toggleCustomCategory);

    // Estado inicial
    toggleInvitations();
    toggleCustomCategory();
});