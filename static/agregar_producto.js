document.addEventListener('DOMContentLoaded', () => {
    const btnCrearCategoria = document.getElementById('btnCrearCategoria');
    const nuevaCategoriaBox = document.getElementById('nuevaCategoriaBox');
    const nuevaCategoriaInput = document.getElementById('nueva_categoria');
    const categoriaMensaje = document.getElementById('categoriaMensaje');
    const categoriaSelect = document.querySelector('select[name="categoria"]');

    if (btnCrearCategoria && nuevaCategoriaBox && nuevaCategoriaInput && categoriaSelect) {
        btnCrearCategoria.addEventListener('click', async () => {
            const estaOculto = nuevaCategoriaBox.classList.contains('d-none');

            if (estaOculto) {
                nuevaCategoriaBox.classList.remove('d-none');
                nuevaCategoriaInput.focus();
                btnCrearCategoria.innerHTML = "<i class='bx bx-check'></i> Guardar categoría";
                return;
            }

            const nombreCategoria = nuevaCategoriaInput.value.trim();

            if (!nombreCategoria) {
                categoriaMensaje.textContent = 'Escribe el nombre de la categoría.';
                categoriaMensaje.className = 'category-message error';
                return;
            }

            try {
                const response = await fetch(crearCategoriaUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        nombre: nombreCategoria
                    })
                });

                const data = await response.json();

                if (data.success) {
                    const option = document.createElement('option');
                    option.value = data.id;
                    option.textContent = data.nombre;
                    option.selected = true;

                    categoriaSelect.appendChild(option);

                    nuevaCategoriaInput.value = '';
                    nuevaCategoriaBox.classList.add('d-none');
                    categoriaMensaje.textContent = '';
                    btnCrearCategoria.innerHTML = "<i class='bx bx-plus'></i> Crear categoría";
                } else {
                    categoriaMensaje.textContent = data.error || 'No se pudo crear la categoría.';
                    categoriaMensaje.className = 'category-message error';
                }
            } catch (error) {
                categoriaMensaje.textContent = 'Error al conectar con el servidor.';
                categoriaMensaje.className = 'category-message error';
            }
        });
    }

    const imagenInput = document.querySelector('input[name="imagen"]');
    const imagePreview = document.getElementById('imagePreview');
    const imagePreviewBox = document.getElementById('imagePreviewBox');
    const imagePreviewText = document.getElementById('imagePreviewText');

    function mostrarVistaPrevia() {
        if (!imagenInput || !imagePreview || !imagePreviewBox || !imagePreviewText) {
            return;
        }

        const imageUrl = imagenInput.value.trim();

        if (imageUrl) {
            imagePreview.src = imageUrl;
            imagePreview.style.display = 'block';
            imagePreviewText.style.display = 'none';
            imagePreviewBox.classList.add('has-image');
        } else {
            imagePreview.src = '';
            imagePreview.style.display = 'none';
            imagePreviewText.style.display = 'block';
            imagePreviewBox.classList.remove('has-image');
        }
    }

    if (imagenInput) {
        imagenInput.addEventListener('input', mostrarVistaPrevia);
        imagenInput.addEventListener('change', mostrarVistaPrevia);
        mostrarVistaPrevia();
    }
});

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}