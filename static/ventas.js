(function () {
    const productsList = document.getElementById('vpProductsList');
    const addProductButton = document.getElementById('vpAddProduct');
    const totalPreview = document.getElementById('vpTotalPreview');
    const stockPreview = document.getElementById('vpStockPreview');

    if (!productsList || !addProductButton || !totalPreview || !stockPreview) {
        return;
    }

    const moneyFormatter = new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        maximumFractionDigits: 0
    });

    const numberFormatter = new Intl.NumberFormat('es-CO', {
        maximumFractionDigits: 0
    });

    function limpiarPrecio(valor) {
        if (!valor) {
            return 0;
        }

        valor = String(valor).trim();

        if (valor.includes(',') && valor.includes('.')) {
            valor = valor.replace(/\./g, '').replace(',', '.');
        } else if (valor.includes(',')) {
            valor = valor.replace(',', '.');
        }

        const precio = parseFloat(valor);

        return isNaN(precio) ? 0 : precio;
    }

    function getRows() {
        return Array.from(productsList.querySelectorAll('.vp-product-row'));
    }

    function updateRemoveButtons() {
        const rows = getRows();

        rows.forEach(function (row) {
            const removeButton = row.querySelector('.vp-remove-btn');

            if (removeButton) {
                removeButton.disabled = rows.length === 1;
            }
        });
    }

    function updatePreview() {
        const rows = getRows();

        let total = 0;
        let selectedProducts = 0;
        let stockMessage = 'Selecciona productos';
        let stockError = false;

        rows.forEach(function (row) {
            const select = row.querySelector('.vp-product-select');
            const input = row.querySelector('.vp-quantity-input');

            if (!select || !input) {
                return;
            }

            const option = select.options[select.selectedIndex];

            if (!option || !option.value) {
                return;
            }

            const price = limpiarPrecio(option.dataset.precio);
            const stock = Number(option.dataset.stock || 0);
            const quantity = Number(input.value || 0);

            input.setAttribute('max', String(stock));

            total += price * quantity;
            selectedProducts += 1;

            if (quantity > stock) {
                stockError = true;
                stockMessage = `Hay un producto que supera el stock. Máximo: ${numberFormatter.format(stock)}`;
            }
        });

        if (!stockError) {
            if (selectedProducts === 1) {
                stockMessage = '1 producto seleccionado';
            } else if (selectedProducts > 1) {
                stockMessage = `${selectedProducts} productos seleccionados`;
            }
        }

        totalPreview.textContent = moneyFormatter.format(total);
        stockPreview.textContent = stockMessage;
    }

    function resetRow(row) {
        const select = row.querySelector('.vp-product-select');
        const input = row.querySelector('.vp-quantity-input');

        if (select) {
            select.selectedIndex = 0;
        }

        if (input) {
            input.value = 1;
            input.removeAttribute('max');
        }
    }

    function addRow() {
        const firstRow = productsList.querySelector('.vp-product-row');

        if (!firstRow) {
            return;
        }

        const newRow = firstRow.cloneNode(true);

        resetRow(newRow);
        productsList.appendChild(newRow);

        updateRemoveButtons();
        updatePreview();
    }

    productsList.addEventListener('change', function (event) {
        if (event.target.classList.contains('vp-product-select')) {
            updatePreview();
        }
    });

    productsList.addEventListener('input', function (event) {
        if (event.target.classList.contains('vp-quantity-input')) {
            updatePreview();
        }
    });

    productsList.addEventListener('click', function (event) {
        const removeButton = event.target.closest('.vp-remove-btn');

        if (!removeButton) {
            return;
        }

        const rows = getRows();

        if (rows.length <= 1) {
            return;
        }

        const row = removeButton.closest('.vp-product-row');

        if (row) {
            row.remove();
        }

        updateRemoveButtons();
        updatePreview();
    });

    addProductButton.addEventListener('click', addRow);

    updateRemoveButtons();
    updatePreview();
})();