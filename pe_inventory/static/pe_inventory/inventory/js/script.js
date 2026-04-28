document.addEventListener("DOMContentLoaded", () => {
    console.log("Stratos Inventory Manager Initialized");

    // Helper function to get CSRF token
    const getCsrfToken = () => {
        const token = document.querySelector("[name=csrfmiddlewaretoken]");
        if (!token) {
            console.error("CSRF token not found in DOM");
            return null;
        }
        return token.value;
    };

    // Validate event ID exists
    const inventoryModalEl = document.getElementById("inventoryModal");
    const eventId = inventoryModalEl?.dataset?.eventId;
    if (!eventId) {
        console.error("Event ID not found in modal data attribute");
    } else {
        console.log("Event ID detected:", eventId);
    }

    // Simple search functionality
    const searchInput = document.getElementById("activitySearch");
    const inventoryTableBody = document.getElementById("inventoryTableBody");

    if (searchInput && inventoryTableBody) {
        searchInput.addEventListener("input", () => {
            const filter = searchInput.value.toLowerCase();
            const rows = inventoryTableBody.getElementsByTagName("tr");

            for (let i = 0; i < rows.length; i++) {
                const text = rows[i].textContent.toLowerCase();
                if (text.includes(filter)) {
                    rows[i].style.display = "";
                } else {
                    rows[i].style.display = "none";
                }
            }
        });
    }

    // Filter Logic for Select Inputs
    const filterCategory = document.getElementById("filterCategory");
    const filterStatus = document.getElementById("filterStatus");

    const applyFilters = () => {
        const catValue = filterCategory.value.toLowerCase();
        const statValue = filterStatus.value.toLowerCase();
        const rows = inventoryTableBody.getElementsByTagName("tr");

        for (let i = 0; i < rows.length; i++) {
            const rowText = rows[i].textContent.toLowerCase();
            const categoryMatch =
                catValue === "all" || rowText.includes(catValue);

            let statusMatch = statValue === "all";
            if (statValue === "stock")
                statusMatch = rowText.includes("en stock");
            if (statValue === "bajo")
                statusMatch = rowText.includes("stock bajo");
            if (statValue === "sin")
                statusMatch = rowText.includes("sin stock");

            if (categoryMatch && statusMatch) {
                rows[i].style.display = "";
            } else {
                rows[i].style.display = "none";
            }
        }
        updatePaginationInfo();
    };

    if (filterCategory) filterCategory.addEventListener("change", applyFilters);
    if (filterStatus) filterStatus.addEventListener("change", applyFilters);

    const updateGlobalStats = () => {
        const rows = Array.from(inventoryTableBody.getElementsByTagName("tr"));
        let inStock = 0;
        let lowStock = 0;
        let noStock = 0;

        rows.forEach((row) => {
            const statusEl = row.querySelector(".item-status");
            if (statusEl) {
                const status = statusEl.textContent.trim();
                if (status === "En Stock") inStock++;
                if (status === "Stock Bajo") lowStock++;
                if (status === "Sin Stock") noStock++;
            }
        });

        const countInStock = document.getElementById("countInStock");
        const countLowStock = document.getElementById("countLowStock");
        const countNoStock = document.getElementById("countNoStock");

        if (countInStock) countInStock.textContent = inStock;
        if (countLowStock) countLowStock.textContent = lowStock;
        if (countNoStock) countNoStock.textContent = noStock;
    };

    const updatePaginationInfo = () => {
        const visibleRows = Array.from(
            inventoryTableBody.getElementsByTagName("tr"),
        ).filter((r) => r.style.display !== "none").length;
        const info = document.getElementById("paginationInfo");
        if (info) {
            info.textContent = `Mostrando ${visibleRows} artículo${visibleRows !== 1 ? "s" : ""} registrado${visibleRows !== 1 ? "s" : ""}`;
        }
    };

    // Action button handlers
    let editingRow = null;
    const inventoryModal = new bootstrap.Modal(inventoryModalEl);
    const inventoryForm = document.getElementById("inventoryForm");
    const modalTitle = document.getElementById("inventoryModalLabel");
    const addItemBtn = document.getElementById("addItemBtn");

    if (addItemBtn) {
        addItemBtn.addEventListener("click", () => {
            editingRow = null;
            modalTitle.textContent = "Añadir Nuevo Artículo";
            inventoryForm.reset();
            document.getElementById("itemId").value = "";
            document.getElementById("itemImage").value = "";
            document.getElementById("itemImageData").value = "";
        });
    }

    const itemImageInput = document.getElementById("itemImage");
    const itemImageData = document.getElementById("itemImageData");

    // No need for FileReader since we send the file directly

    document.addEventListener("click", (e) => {
        const editBtn = e.target.closest(".edit-btn");
        const deleteBtn = e.target.closest(".delete-btn");

        if (editBtn) {
            editingRow = editBtn.closest("tr");
            modalTitle.textContent = "Editar Artículo";

            document.getElementById("itemName").value = editingRow
                .querySelector(".item-name")
                .textContent.trim();
            document.getElementById("itemSku").value = editingRow
                .querySelector(".item-sku")
                .textContent.trim();
            document.getElementById("itemCategory").value = editingRow
                .querySelector(".item-category")
                .textContent.trim();
            document.getElementById("itemTotal").value = editingRow
                .querySelector(".item-total")
                .textContent.trim();
            document.getElementById("itemNotes").value = editingRow
                .querySelector(".item-notes")
                .textContent.trim();
            document.getElementById("itemId").value = editBtn.dataset.itemId;

            const currentImg = editingRow.querySelector(".item-img");
            document.getElementById("itemImageData").value = currentImg
                ? currentImg.src
                : "";
            document.getElementById("itemImage").value = "";
        }

        if (deleteBtn) {
            const itemId = deleteBtn.dataset.itemId;
            const currentEventId =
                document.getElementById("inventoryModal").dataset.eventId;
            if (
                confirm(
                    "¿Estás seguro de eliminar este recurso del inventario?",
                )
            ) {
                // Send delete request
                const csrfToken = getCsrfToken();
                if (!csrfToken) {
                    alert("Error de seguridad: Token CSRF no encontrado");
                    return;
                }

                const formData = new FormData();
                formData.append("csrfmiddlewaretoken", csrfToken);

                fetch(`/inventario/${currentEventId}/delete/${itemId}/`, {
                    method: "POST",
                    body: formData,
                })
                    .then((response) => response.json())
                    .then((result) => {
                        if (result.success) {
                            loadItems();
                            alert(result.message);
                        } else {
                            alert("Error: " + result.error);
                        }
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                        alert("Error al eliminar el artículo");
                    });
            }
        }
    });

    if (inventoryForm) {
        inventoryForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const itemId = document.getElementById("itemId").value;
            const currentEventId =
                document.getElementById("inventoryModal").dataset.eventId;
            const name = document.getElementById("itemName").value.trim();
            const sku = document.getElementById("itemSku").value.trim();
            const category = document.getElementById("itemCategory").value;
            const total = parseInt(document.getElementById("itemTotal").value);
            const notes = document.getElementById("itemNotes").value.trim();
            const imageFile = document.getElementById("itemImage").files[0];

            // Validaciones básicas
            if (!name) {
                alert("El nombre del artículo es requerido");
                return;
            }
            if (!sku) {
                alert("El SKU es requerido");
                return;
            }
            if (!total || total < 1) {
                alert("El stock total debe ser mayor a 0");
                return;
            }

            const formData = new FormData();
            formData.append("name", name);
            formData.append("sku", sku);
            formData.append("category", category);
            formData.append("total_stock", total);
            formData.append("notes", notes);
            if (imageFile) {
                formData.append("image", imageFile);
            }

            // Agregar CSRF token al FormData
            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                alert("Error de seguridad: Token CSRF no encontrado");
                return;
            }
            formData.append("csrfmiddlewaretoken", csrfToken);

            try {
                let url, method;

                if (itemId) {
                    // Actualizar
                    url = `/inventario/${currentEventId}/update/${itemId}/`;
                    method = "POST";
                    console.log("Actualizando item:", itemId);
                } else {
                    // Crear
                    url = `/inventario/${currentEventId}/create/`;
                    method = "POST";
                    console.log("Creando nuevo item");
                }

                console.log("Enviando formulario a:", url);
                console.log("Event ID:", currentEventId);

                const response = await fetch(url, {
                    method: method,
                    body: formData,
                });

                console.log("Response status:", response.status);
                const result = await response.json();
                console.log("Response data:", result);

                if (response.ok) {
                    alert(result.message || "Operación exitosa");
                    inventoryModal.hide();
                    inventoryForm.reset();
                    document.getElementById("itemId").value = "";
                    loadItems();
                } else {
                    alert(
                        "Error: " + (result.error || "Error en la operación"),
                    );
                    console.error("Error details:", result);
                }
            } catch (error) {
                console.error("Error completo:", error);
                alert("Error al guardar el artículo: " + error.message);
            }
        });
    }

    const loadItems = async () => {
        const currentEventId =
            document.getElementById("inventoryModal").dataset.eventId;

        if (!currentEventId) {
            console.error("Event ID no disponible para cargar items");
            document.getElementById("inventoryTableBody").innerHTML =
                '<tr><td colspan="6" class="text-center py-4 text-danger">Error: ID de evento no disponible</td></tr>';
            return;
        }

        try {
            console.log("Cargando items para evento:", currentEventId);
            const response = await fetch(
                `/inventario/${currentEventId}/items/`,
            );
            console.log("Response status:", response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Items data received:", data);

            if (data.success) {
                const items = data.items;
                const tbody = document.getElementById("inventoryTableBody");
                tbody.innerHTML = "";
                if (items.length === 0) {
                    tbody.innerHTML =
                        '<tr><td colspan="6" class="text-center py-4 text-muted">No hay artículos registrados</td></tr>';
                } else {
                    items.forEach((item) => {
                        const statusBadgeClass =
                            item.status === "En Stock"
                                ? "bg-success"
                                : item.status === "Stock Bajo"
                                  ? "bg-warning text-dark"
                                  : "bg-danger";
                        const usagePercent =
                            item.total_stock > 0
                                ? Math.round(
                                      (item.used_stock / item.total_stock) *
                                          100,
                                  )
                                : 0;
                        const finalImageUrl =
                            item.image ||
                            `https://ui-avatars.com/api/?name=${encodeURIComponent(item.name)}&background=f8f9ff&color=0058be`;
                        const rowHtml = `
                            <tr data-item-id="${item.id}">
                                <td class="px-4 py-3">
                                    <div class="d-flex align-items-center">
                                        <div class="bg-light rounded p-1 me-3 border" style="width: 40px; height: 40px;">
                                            <img src="${finalImageUrl}" class="w-100 h-100 object-fit-cover rounded item-img" alt="${item.name}" referrerpolicy="no-referrer">
                                        </div>
                                        <div>
                                            <div class="fw-bold item-name">${item.name}</div>
                                            <small class="text-muted item-sku">${item.sku}</small>
                                        </div>
                                    </div>
                                </td>
                                <td><span class="badge bg-primary text-white item-category">${item.category}</span></td>
                                <td>
                                    <div class="d-flex justify-content-between small fw-bold mb-1">
                                        <span class="text-muted">Total: <span class="item-total">${item.total_stock}</span></span>
                                        <span class="text-primary">Usados: <span class="item-used">${item.used_stock}</span></span>
                                    </div>
                                    <div class="progress" style="height: 6px;">
                                        <div class="progress-bar ${usagePercent > 80 ? "bg-warning" : "bg-primary"}" style="width: ${usagePercent}%;"></div>
                                    </div>
                                </td>
                                <td><span class="badge ${statusBadgeClass} item-status">${item.status}</span></td>
                                <td>
                                    <small class="text-muted item-notes">${item.notes}</small>
                                </td>
                                <td class="px-4 text-center">
                                    <div class="btn-group">
                                        <button class="btn btn-sm btn-outline-primary edit-btn" title="Editar" data-bs-toggle="modal" data-bs-target="#inventoryModal" data-item-id="${item.id}">
                                            <span class="material-symbols-outlined" style="font-size: 16px;">edit</span>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger delete-btn" title="Eliminar" data-item-id="${item.id}">
                                            <span class="material-symbols-outlined" style="font-size: 16px;">delete</span>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `;
                        tbody.insertAdjacentHTML("beforeend", rowHtml);
                    });
                }
                updateGlobalStats();
            } else {
                console.error("No success flag in response");
                document.getElementById("inventoryTableBody").innerHTML =
                    '<tr><td colspan="6" class="text-center py-4 text-danger">Error al cargar los items</td></tr>';
            }
        } catch (error) {
            console.error("Error loading items:", error);
            document.getElementById("inventoryTableBody").innerHTML =
                '<tr><td colspan="6" class="text-center py-4 text-danger">Error: ' +
                error.message +
                "</td></tr>";
        }
    };

    // Initial load
    loadItems();
    updatePaginationInfo();
});
