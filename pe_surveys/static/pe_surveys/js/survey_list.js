function toggleSurvey(pk, event_id) {
    fetch(`/encuestas/${event_id}/toggle/${pk}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                location.reload();
            }
        });
}

function sendSurvey(pk, event_id) {
    if (!confirm("¿Enviar esta encuesta a todos los participantes?")) return;

    fetch(`/encuestas/${event_id}/api/send-survey/${pk}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                alert("Encuesta enviada");
            } else {
                alert("Error: " + data.error);
            }
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1),
                );
                break;
            }
        }
    }
    return cookieValue;
}

document
    .getElementById("id_delivery_type")
    .addEventListener("change", function () {
        const scheduledField = document.getElementById("scheduled_date_field");
        scheduledField.style.display =
            this.value === "fecha_especifica" ? "block" : "none";
    });

document.querySelectorAll(".question-type-select").forEach((select) => {
    select.addEventListener("change", function () {
        const block = this.closest(".question-block");
        const optionsField = block.querySelector(".options-field");
        const optionsInput = optionsField.querySelector("input, textarea");
        if (this.value === "opcion_multiple") {
            optionsField.style.display = "block";
            if (optionsInput) optionsInput.required = true;
        } else {
            optionsField.style.display = "none";
            if (optionsInput) optionsInput.required = false;
        }
    });
});

function addQuestion() {
    const container = document.getElementById("questions_container");
    const count = container.querySelectorAll(".question-block").length;
    const totalForms = document.getElementById("id_form-TOTAL_FORMS");

    const newBlock = container.querySelector(".question-block").cloneNode(true);
    newBlock.querySelectorAll("input, select, textarea").forEach((input) => {
        input.name = input.name.replace(/form-\d+-/, `form-${count}-`);
        input.id = input.id.replace(/form-\d+-/, `form-${count}-`);
        input.value = "";
    });

    container.appendChild(newBlock);
    totalForms.value = count + 1;
}

// Initialize existing question types
document.querySelectorAll(".question-type-select").forEach((select) => {
    select.dispatchEvent(new Event("change"));
});
// Show modal if there are errors or editing
if (window.hasFormErrors || window.isEditing) {
    var myModal = new bootstrap.Modal(
        document.getElementById("createSurveyModal"),
    );
    myModal.show();
}
