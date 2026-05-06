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
    let inventoryModal = null;
    if (typeof bootstrap !== "undefined" && inventoryModalEl) {
        inventoryModal = new bootstrap.Modal(inventoryModalEl);
    } else {
        console.warn(
            "Bootstrap modal is not available. The inventory modal will still render but animation features may not work.",
        );
    }
    const inventoryForm = document.getElementById("inventoryForm");
    const modalTitle = document.getElementById("inventoryModalLabel");
    const saveItemButton = document.getElementById("saveItemButton");
    const addItemBtn = document.getElementById("addItemBtn");

    if (addItemBtn) {
        addItemBtn.addEventListener("click", () => {
            editingRow = null;
            modalTitle.textContent = "Añadir Nuevo Artículo";
            if (inventoryForm) {
                inventoryForm.reset();
            }
            document.getElementById("itemId").value = "";
            const imageInput = document.getElementById("itemImage");
            if (imageInput) imageInput.value = "";
            const imageDataInput = document.getElementById("itemImageData");
            if (imageDataInput) imageDataInput.value = "";
        });
    }
    if (saveItemButton && inventoryForm) {
        saveItemButton.addEventListener("click", (e) => {
            e.preventDefault();
            if (typeof inventoryForm.requestSubmit === "function") {
                inventoryForm.requestSubmit();
            } else {
                inventoryForm.submit();
            }
        });
    }

    const exportExcelBtn = document.getElementById("exportExcelBtn");
    const importExcelBtn = document.getElementById("importExcelBtn");
    const excelFileInput = document.getElementById("excelFileInput");

    if (exportExcelBtn) {
        exportExcelBtn.addEventListener("click", async () => {
            try {
                console.log("Iniciando exportación de Excel...");
                console.log("Event ID:", eventId);

                if (!eventId) {
                    alert("Error: ID de evento no disponible");
                    return;
                }

                exportExcelBtn.disabled = true;
                exportExcelBtn.innerHTML =
                    '<span class="material-symbols-outlined" style="font-size: 18px;">downloading</span> Descargando...';

                const url = `/inventario/${eventId}/export-excel/`;
                console.log("URL de descarga:", url);

                const response = await fetch(url, {
                    credentials: "same-origin",
                });

                console.log("Response status:", response.status);
                console.log("Response OK:", response.ok);
                console.log(
                    "Content-Type:",
                    response.headers.get("content-type"),
                );

                if (!response.ok) {
                    let message = "Error desconocido";
                    const contentType =
                        response.headers.get("content-type") || "";
                    if (contentType.includes("application/json")) {
                        const error = await response.json();
                        message = error.error || message;
                    } else {
                        const text = await response.text();
                        console.log("Response text:", text.substring(0, 200));
                        message = text ? text.substring(0, 400) : message;
                    }
                    alert("Error: " + message);
                    return;
                }

                console.log("Creando blob...");
                const blob = await response.blob();
                console.log("Blob size:", blob.size, "bytes");
                console.log("Blob type:", blob.type);

                const downloadUrl = window.URL.createObjectURL(blob);
                console.log("Download URL creada:", downloadUrl);

                const a = document.createElement("a");
                a.href = downloadUrl;
                a.download = `inventario_${new Date().toISOString().split("T")[0]}.xlsx`;
                console.log("Download name:", a.download);

                document.body.appendChild(a);
                a.click();
                console.log("Click realizado");

                setTimeout(() => {
                    window.URL.revokeObjectURL(downloadUrl);
                    document.body.removeChild(a);
                    console.log("Limpieza realizada");
                }, 500);

                alert("¡Archivo exportado correctamente!");
            } catch (error) {
                console.error("Error completo:", error);
                console.error("Stack:", error.stack);
                alert("Error al exportar: " + error.message);
            } finally {
                exportExcelBtn.disabled = false;
                exportExcelBtn.innerHTML =
                    '<span class="material-symbols-outlined" style="font-size: 18px;">download</span> Exportar';
            }
        });
    }

    if (importExcelBtn) {
        importExcelBtn.addEventListener("click", () => {
            if (excelFileInput) {
                excelFileInput.click();
            }
        });
    }

    if (excelFileInput) {
        excelFileInput.addEventListener("change", async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            try {
                if (importExcelBtn) {
                    importExcelBtn.disabled = true;
                    importExcelBtn.innerHTML =
                        '<span class="material-symbols-outlined" style="font-size: 18px;">uploading</span> Importando...';
                }

                const formData = new FormData();
                formData.append("file", file);
                const response = await fetch(
                    `/inventario/${eventId}/import-excel/`,
                    {
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                            "X-CSRFToken": getCsrfToken(),
                        },
                        body: formData,
                    },
                );

                let data = null;
                const contentType = response.headers.get("content-type") || "";
                if (contentType.includes("application/json")) {
                    data = await response.json();
                } else {
                    const text = await response.text();
                    data = {
                        error: text
                            ? text.substring(0, 400)
                            : "Error desconocido",
                    };
                }

                if (response.ok) {
                    let message = data.message || "Importación completada";
                    if (data.warnings && data.warnings.length > 0) {
                        message +=
                            "\n\nAdvertencias:\n" +
                            data.warnings.slice(0, 5).join("\n");
                        if (data.warnings.length > 5) {
                            message += `\n... y ${data.warnings.length - 5} advertencias más`;
                        }
                    }
                    if (data.errors && data.errors.length > 0) {
                        message +=
                            "\n\nErrores encontrados:\n" +
                            data.errors.slice(0, 5).join("\n");
                        if (data.errors.length > 5) {
                            message += `\n... y ${data.errors.length - 5} errores más`;
                        }
                    }
                    alert(message);
                    await loadItems();
                    updateGlobalStats();
                } else {
                    alert("Error: " + (data.error || "Error desconocido"));
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Error al importar: " + error.message);
            } finally {
                if (importExcelBtn) {
                    importExcelBtn.disabled = false;
                    importExcelBtn.innerHTML =
                        '<span class="material-symbols-outlined" style="font-size: 18px;">upload</span> Importar';
                }
                excelFileInput.value = "";
            }
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
            const deleteModalEl = document.getElementById("deleteItemModal");
            const deleteModal = new bootstrap.Modal(deleteModalEl);
            const itemName = deleteBtn
                .closest("tr")
                .querySelector(".item-name")
                .textContent.trim();
            document.getElementById("deleteItemName").textContent = itemName;
            document.getElementById("confirmDeleteBtn").dataset.itemId = itemId;
            deleteModal.show();

            document.getElementById("confirmDeleteBtn").onclick = function () {
                const currentEventId =
                    document.getElementById("inventoryModal").dataset.eventId;
                const csrfToken = getCsrfToken();
                if (!csrfToken) {
                    console.error("Token CSRF no encontrado");
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
                            deleteModal.hide();
                        } else {
                            console.error("Error:", result.error);
                        }
                    })
                    .catch((error) => {
                        console.error("Error:", error);
                    });
            };
        }
    });

    if (inventoryForm) {
        inventoryForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const itemId = document.getElementById("itemId").value;
            const currentEventId =
                document.getElementById("inventoryModal").dataset.eventId;
            const name = document.getElementById("itemName").value.trim();
            const category = document.getElementById("itemCategory").value;
            const total = parseInt(document.getElementById("itemTotal").value);
            const notes = document.getElementById("itemNotes").value.trim();
            const imageFile = document.getElementById("itemImage").files[0];

            // Validaciones básicas
            if (!name) {
                console.error("El nombre del artículo es requerido");
                return;
            }
            if (!total || total < 1) {
                console.error("El stock total debe ser mayor a 0");
                return;
            }

            const formData = new FormData();
            formData.append("name", name);
            formData.append("category", category);
            formData.append("total_stock", total);
            formData.append("notes", notes);
            if (imageFile) {
                formData.append("image", imageFile);
            }

            // Agregar CSRF token al FormData
            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                console.error("Token CSRF no encontrado");
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
                    if (inventoryModal) {
                        inventoryModal.hide();
                    }
                    if (inventoryForm) {
                        inventoryForm.reset();
                    }
                    document.getElementById("itemId").value = "";
                    loadItems();
                } else {
                    console.error("Error en la operación:", result);
                }
            } catch (error) {
                console.error("Error completo:", error);
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
                                        </div>
                                    </div>
                                </td>
                                <td><span class="badge bg-primary text-white item-category">${item.category}</span></td>
                                <td>
                                    <span class="fw-bold text-dark">${item.used_stock}/${item.total_stock}</span>
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
                updatePaginationInfo();
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
