document.addEventListener("DOMContentLoaded", () => {
    const getCsrfToken = () => {
        const token = document.querySelector("[name=csrfmiddlewaretoken]");
        if (!token) {
            return null;
        }
        return token.value;
    };

    const inventoryModalEl = document.getElementById("inventoryModal");
    const eventId = inventoryModalEl?.dataset?.eventId;

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
            const t = window.translations && window.translations[window.currentLang] ? window.translations[window.currentLang] : window.translations.es;
            const showingItems = t.showing_items || "Mostrando";
            const itemsRegistered = t.items_registered || "artículos registrados";
            info.textContent = `${showingItems} ${visibleRows} ${visibleRows !== 1 ? itemsRegistered.replace("artículos", "artículo").replace("registrados", "registrado") : itemsRegistered}`;
        }
    };

    let editingRow = null;
    let inventoryModal = null;
    if (typeof bootstrap !== "undefined" && inventoryModalEl) {
        inventoryModal = new bootstrap.Modal(inventoryModalEl);
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
            if (inventoryModal) {
                inventoryModal.show();
            }
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
                if (!eventId) {
                    showToast("Error: ID de evento no disponible", "error");
                    return;
                }

                exportExcelBtn.disabled = true;
                exportExcelBtn.innerHTML =
                    '<span class="material-symbols-outlined" style="font-size: 18px;">downloading</span> Descargando...';

                const url = `/inventario/${eventId}/export-excel/`;

                const response = await fetch(url, {
                    credentials: "same-origin",
                });

                if (!response.ok) {
                    let message = "Error desconocido";
                    const contentType =
                        response.headers.get("content-type") || "";
                    if (contentType.includes("application/json")) {
                        const error = await response.json();
                        message = error.error || message;
                    } else {
                        const text = await response.text();
                        message = text ? text.substring(0, 400) : message;
                    }
                    showToast("Error: " + message, "error");
                    return;
                }

                const blob = await response.blob();

                const downloadUrl = window.URL.createObjectURL(blob);

                const a = document.createElement("a");
                a.href = downloadUrl;
                a.download = `inventario_${new Date().toISOString().split("T")[0]}.xlsx`;

                document.body.appendChild(a);
                a.click();

                setTimeout(() => {
                    window.URL.revokeObjectURL(downloadUrl);
                    document.body.removeChild(a);
                }, 500);

                showToast("Archivo exportado correctamente", "success");
            } catch (error) {
                showToast("Error al exportar: " + error.message, "error");
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
                }
                if (response.ok) {
                    await loadItems();
                    updateGlobalStats();
                    showToast("Inventario importado correctamente", "success");
                } else {
                    showToast(data?.error || "Error al importar", "error");
                }
            } catch (error) {
                showToast("Error al importar inventario", "error");
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

    document.addEventListener("click", (e) => {
        const editBtn = e.target.closest(".edit-btn");
        const deleteBtn = e.target.closest(".delete-btn");

        if (editBtn) {
            const itemId = editBtn.dataset.itemId;
            editingRow = editBtn.closest("tr");
            modalTitle.textContent = "Editar Artículo";

            fetch(`/inventario/${eventId}/item/${itemId}/`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        const item = data.item;
                        document.getElementById("itemName").value = item.name;
                        document.getElementById("itemCategory").value =
                            item.category;
                        document.getElementById("itemTotal").value =
                            item.total_stock;
                        document.getElementById("itemNotes").value = item.notes;
                        document.getElementById("itemId").value = item.id;

                        const finalImageUrl =
                            item.image ||
                            `https://ui-avatars.com/api/?name=${encodeURIComponent(item.name)}&background=f8f9ff&color=0058be`;
                        document.getElementById("itemImageData").value =
                            finalImageUrl;
                        document.getElementById("itemImage").value = "";

                        if (inventoryModal) {
                            inventoryModal.show();
                        }
                    } else {
                        showToast("Error al cargar los datos del artículo", "error");
                    }
                })
                .catch((error) => {
                    showToast("Error al cargar los datos del artículo", "error");
                });
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
                    showToast("Token CSRF no encontrado", "error");
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
                            showToast("Artículo eliminado correctamente", "success");
                        } else {
                            showToast(result.error || "Error al eliminar", "error");
                        }
                    })
                    .catch((error) => {
                        showToast("Error al eliminar artículo", "error");
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

            if (!name) {
                showToast("El nombre del artículo es requerido", "error");
                return;
            }
            if (!total || total < 1) {
                showToast("El stock total debe ser mayor a 0", "error");
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

            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                showToast("Token CSRF no encontrado", "error");
                return;
            }
            formData.append("csrfmiddlewaretoken", csrfToken);

            try {
                let url;

                if (itemId) {
                    url = `/inventario/${currentEventId}/update/${itemId}/`;
                } else {
                    url = `/inventario/${currentEventId}/create/`;
                }

                const response = await fetch(url, {
                    method: "POST",
                    body: formData,
                });

                const result = await response.json();

                if (response.ok) {
                    if (inventoryModal) {
                        inventoryModal.hide();
                    }
                    if (inventoryForm) {
                        inventoryForm.reset();
                    }
                    document.getElementById("itemId").value = "";
                    loadItems();
                    showToast(itemId ? "Artículo actualizado correctamente" : "Artículo creado correctamente", "success");
                } else {
                    showToast(result.error || "Error en la operación", "error");
                }
            } catch (error) {
                showToast("Error al guardar artículo", "error");
            }
        });
    }

    const loadItems = async () => {
        const currentEventId =
            document.getElementById("inventoryModal").dataset.eventId;

        if (!currentEventId) {
            document.getElementById("inventoryTableBody").innerHTML =
                '<tr><td colspan="6" class="text-center py-4 text-danger">Error: ID de evento no disponible</td></tr>';
            return;
        }

        try {
            const response = await fetch(
                `/inventario/${currentEventId}/items/`,
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                const items = data.items;
                const tbody = document.getElementById("inventoryTableBody");
                tbody.innerHTML = "";
                if (items.length === 0) {
                    const t = window.translations && window.translations[window.currentLang] ? window.translations[window.currentLang] : window.translations.es;
                    const noItems = t.no_inventory_items || "No hay artículos registrados";
                    tbody.innerHTML =
                        `<tr style="background-color: var(--surface-container-lowest);"><td colspan="6" class="text-center py-4 text-muted" style="background-color: var(--surface-container-lowest);">${noItems}</td></tr>`;
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
                            <tr style="background-color: var(--surface-container-lowest);" data-item-id="${item.id}">
                                <td class="px-4 py-3" style="background-color: var(--surface-container-lowest);">
                                    <div class="d-flex align-items-center">
                                        <div class="bg-light rounded p-1 me-3 border" style="width: 40px; height: 40px;">
                                            <img src="${finalImageUrl}" class="w-100 h-100 object-fit-cover rounded item-img" alt="${item.name}" referrerpolicy="no-referrer">
                                        </div>
                                        <div>
                                            <div class="fw-bold item-name">${item.name}</div>
                                        </div>
                                    </div>
                                </td>
                                <td style="background-color: var(--surface-container-lowest);"><span class="badge bg-primary text-white item-category">${item.category}</span></td>
                                <td style="background-color: var(--surface-container-lowest);">
                                    <span class="fw-bold" style="color: var(--text-on-surface-variant);">${item.used_stock}/${item.total_stock}</span>
                                </td>
                                <td style="background-color: var(--surface-container-lowest);"><span class="badge ${statusBadgeClass} item-status">${item.status}</span></td>
                                <td style="background-color: var(--surface-container-lowest);">
                                    <small class="text-muted item-notes">${item.notes}</small>
                                </td>
                                <td class="px-4 text-center" style="background-color: var(--surface-container-lowest);">
                                    <div class="btn-group">
                                        <button class="btn btn-sm btn-outline-primary edit-btn" title="Editar" data-item-id="${item.id}">
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
                document.getElementById("inventoryTableBody").innerHTML =
                    '<tr><td colspan="6" class="text-center py-4 text-danger">Error al cargar los items</td></tr>';
            }
        } catch (error) {
            document.getElementById("inventoryTableBody").innerHTML =
                '<tr><td colspan="6" class="text-center py-4 text-danger">Error: ' +
                error.message +
                "</td></tr>";
        }
    };

    loadItems();
    updatePaginationInfo();
});