// survey_form.js
document.addEventListener("DOMContentLoaded", function () {
    const surveyTypeSelect = document.querySelector(".survey-type-select");
    const multipleChoiceField = document.querySelector(
        "#multiple_choice_field",
    );
    const optionsContainer = document.querySelector("#options_container");
    const optionsTitle = document.querySelector("#options_title");
    const deliveryTypeSelect = document.querySelector("#id_delivery_type");
    const scheduledDateField = document.querySelector("#scheduled_date_field");

    // Usar event delegation para los botones de agregar y eliminar opción
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "add_option_btn") {
            e.preventDefault();
            addOption();
        }
        
        // Manejar eliminación de opciones
        if (e.target && (e.target.classList.contains("remove-option-btn") || e.target.closest(".remove-option-btn"))) {
            e.preventDefault();
            const button = e.target.classList.contains("remove-option-btn") ? e.target : e.target.closest(".remove-option-btn");
            removeOption(button);
        }
    });

    function toggleFields() {
        const selectedType = surveyTypeSelect.value;
        if (selectedType === "texto") {
            multipleChoiceField.style.display = "block";
            optionsContainer.style.display = "block";
            optionsTitle.style.display = "block";
            const addBtn = document.querySelector("#add_option_btn");
            if (addBtn) addBtn.style.display = "block";
        } else {
            multipleChoiceField.style.display = "none";
            optionsContainer.style.display = "none";
            optionsTitle.style.display = "none";
            const addBtn = document.querySelector("#add_option_btn");
            if (addBtn) addBtn.style.display = "none";
        }
    }

    function toggleScheduledDate() {
        const selectedDelivery = deliveryTypeSelect.value;
        if (selectedDelivery === "programado") {
            scheduledDateField.style.display = "block";
        } else {
            scheduledDateField.style.display = "none";
        }
    }

    if (surveyTypeSelect) {
        surveyTypeSelect.addEventListener("change", toggleFields);
        toggleFields(); // Inicial
    }

    if (deliveryTypeSelect) {
        deliveryTypeSelect.addEventListener("change", toggleScheduledDate);
        toggleScheduledDate(); // Inicial
    }
});

// Función para agregar opción dinámicamente
function addOption() {
    console.log("Iniciando addOption()");

    const optionsContainer = document.querySelector("#options_container");

    // Buscar el input de TOTAL_FORMS - puede tener diferentes variaciones de nombres
    let managementForm = document.querySelector("#id_form-TOTAL_FORMS");
    if (!managementForm) {
        managementForm = document.querySelector('input[name*="TOTAL_FORMS"]');
    }

    console.log("optionsContainer:", optionsContainer);
    console.log("managementForm:", managementForm);
    console.log("managementForm queryselector value:", managementForm?.value);

    if (!optionsContainer) {
        console.error("No se encontró #options_container");
        return;
    }

    if (!managementForm) {
        console.error("No se encontró el input TOTAL_FORMS");
        console.log(
            "Inputs disponibles en la página:",
            document.querySelectorAll('input[name*="TOTAL"]'),
        );
        return;
    }

    const currentTotal = parseInt(managementForm.value);
    console.log("currentTotal:", currentTotal);

    // Clonar la última fila de opción
    const optionBlocks = optionsContainer.querySelectorAll(".option-block");
    console.log("optionBlocks encontrados:", optionBlocks.length);

    if (optionBlocks.length === 0) {
        console.error("No hay option-blocks para clonar");
        return;
    }

    const lastBlock = optionBlocks[optionBlocks.length - 1];
    const newBlock = lastBlock.cloneNode(true);

    console.log("Bloqueado clonado, actualizando índices...");

    // Actualizar índices en los inputs del nuevo bloque
    const inputs = newBlock.querySelectorAll("[name], [id]");
    console.log("Inputs a actualizar:", inputs.length);

    inputs.forEach((input) => {
        // Actualizar atributo name
        if (input.name) {
            const oldName = input.name;
            const newName = input.name.replace(
                /options-\d+-/,
                `options-${currentTotal}-`,
            );
            input.name = newName;
            console.log(`Nombre actualizado: ${oldName} -> ${newName}`);
        }

        // Actualizar atributo id
        if (input.id) {
            const oldId = input.id;
            const newId = input.id.replace(
                /id_options-\d+-/,
                `id_options-${currentTotal}-`,
            );
            input.id = newId;
            console.log(`ID actualizado: ${oldId} -> ${newId}`);
        }

        // Limpiar valores
        if (input.type === "checkbox" || input.type === "radio") {
            input.checked = false;
        } else if (input.tagName !== "LABEL") {
            input.value = "";
        }
    });

    // Actualizar labels asociados
    const labels = newBlock.querySelectorAll("label");
    labels.forEach((label) => {
        const forAttr = label.getAttribute("for");
        if (forAttr) {
            const newFor = forAttr.replace(
                /id_form-\d+-/,
                `id_form-${currentTotal}-`,
            );
            label.setAttribute("for", newFor);
        }
    });

    // Agregar el nuevo bloque
    optionsContainer.appendChild(newBlock);
    console.log("Nuevo bloque agregado al contenedor");

    // Incrementar TOTAL_FORMS
    managementForm.value = currentTotal + 1;

    console.log(`✓ Opción agregada. Total formas: ${managementForm.value}`);
    
    // Ocultar mensaje de error si estaba visible
    hideOptionsError();
}

// Función para eliminar opción dinámicamente
function removeOption(button) {
    console.log("Iniciando removeOption()");
    
    const optionsContainer = document.querySelector("#options_container");
    const optionBlocks = optionsContainer.querySelectorAll(".option-block");
    
    // Verificar que no queden menos de 2 opciones
    if (optionBlocks.length <= 2) {
        showOptionsError("Debes mantener al menos 2 opciones para las encuestas de texto.");
        return;
    }
    
    // Buscar el input de TOTAL_FORMS
    let managementForm = document.querySelector("#id_form-TOTAL_FORMS");
    if (!managementForm) {
        managementForm = document.querySelector('input[name*="TOTAL_FORMS"]');
    }
    
    if (!managementForm) {
        console.error("No se encontró el input TOTAL_FORMS");
        return;
    }
    
    // Encontrar el bloque de opción que contiene el botón
    const optionBlock = button.closest(".option-block");
    if (!optionBlock) {
        console.error("No se encontró el bloque de opción");
        return;
    }
    
    // Remover el bloque
    optionBlock.remove();
    console.log("Bloque de opción removido");
    
    // Re-indexar los bloques restantes
    reindexOptions();
    
    // Decrementar TOTAL_FORMS
    const currentTotal = parseInt(managementForm.value);
    managementForm.value = currentTotal - 1;
    
    console.log(`✓ Opción eliminada. Total formas: ${managementForm.value}`);
    
    // Ocultar mensaje de error si estaba visible
    hideOptionsError();
}

// Función para re-indexar las opciones después de eliminar una
function reindexOptions() {
    const optionsContainer = document.querySelector("#options_container");
    const optionBlocks = optionsContainer.querySelectorAll(".option-block");
    
    optionBlocks.forEach((block, index) => {
        const inputs = block.querySelectorAll("[name], [id]");
        inputs.forEach((input) => {
            // Actualizar atributo name
            if (input.name) {
                const newName = input.name.replace(/options-\d+-/, `options-${index}-`);
                input.name = newName;
            }
            
            // Actualizar atributo id
            if (input.id) {
                const newId = input.id.replace(/id_options-\d+-/, `id_options-${index}-`);
                input.id = newId;
            }
        });
        
        // Actualizar labels asociados
        const labels = block.querySelectorAll("label");
        labels.forEach((label) => {
            const forAttr = label.getAttribute("for");
            if (forAttr) {
                const newFor = forAttr.replace(/id_options-\d+-/, `id_options-${index}-`);
                label.setAttribute("for", newFor);
            }
        });
    });
    
    console.log("Opciones re-indexadas");
}

// Función para mostrar mensaje de error
function showOptionsError(message) {
    const errorDiv = document.querySelector("#options_error");
    const errorText = document.querySelector("#options_error_text");
    
    if (errorDiv && errorText) {
        errorText.textContent = message;
        errorDiv.style.display = "block";
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            hideOptionsError();
        }, 5000);
    }
}

// Función para ocultar mensaje de error
function hideOptionsError() {
    const errorDiv = document.querySelector("#options_error");
    if (errorDiv) {
        errorDiv.style.display = "none";
    }
}
