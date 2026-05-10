(function () {
    const productSelect = document.getElementById('producto');
    const quantityInput = document.getElementById('cantidad');
    const totalPreview = document.getElementById('saleTotalPreview');
    const stockPreview = document.getElementById('saleStockPreview');

    if (!productSelect || !quantityInput || !totalPreview || !stockPreview) {
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
        if (!valor) return 0;

        valor = String(valor).trim();

        if (valor.includes(',') && valor.includes('.')) {
            valor = valor.replace(/\./g, '').replace(',', '.');
        } else if (valor.includes(',')) {
            valor = valor.replace(',', '.');
        }

        const precio = parseFloat(valor);

        return isNaN(precio) ? 0 : precio;
    }

    function updatePreview() {
        const selectedOption = productSelect.options[productSelect.selectedIndex];

        if (!selectedOption || !selectedOption.value) {
            totalPreview.textContent = moneyFormatter.format(0);
            stockPreview.textContent = 'Selecciona producto';
            quantityInput.removeAttribute('max');
            return;
        }

        const price = limpiarPrecio(selectedOption.dataset.precio);
        const stock = Number(selectedOption.dataset.stock || 0);
        const quantity = Number(quantityInput.value || 0);
        const total = price * quantity;

        totalPreview.textContent = moneyFormatter.format(total);
        stockPreview.textContent = `Stock disponible: ${numberFormatter.format(stock)}`;

        quantityInput.setAttribute('max', String(stock));

        if (quantity > stock) {
            stockPreview.textContent = `Máximo permitido: ${numberFormatter.format(stock)}`;
        }
    }

    productSelect.addEventListener('change', updatePreview);
    quantityInput.addEventListener('input', updatePreview);

    updatePreview();
})();