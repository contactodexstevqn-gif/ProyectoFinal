const menuToggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (menuToggle && sidebar && overlay) {
    menuToggle.addEventListener('click', () => {
        sidebar.classList.add('active');
        overlay.classList.add('active');
    });

    overlay.addEventListener('click', () => {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
    });
}

const themeToggle = document.getElementById('themeToggle');
const themeIcon = themeToggle ? themeToggle.querySelector('i') : null;

const savedTheme = localStorage.getItem('theme');

if (savedTheme === 'dark') {
    document.body.classList.add('dark-mode');

    if (themeIcon) {
        themeIcon.classList.remove('bx-moon');
        themeIcon.classList.add('bx-sun');
    }
}

if (themeToggle && themeIcon) {
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');

        const isDark = document.body.classList.contains('dark-mode');

        themeIcon.classList.toggle('bx-moon', !isDark);
        themeIcon.classList.toggle('bx-sun', isDark);

        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

const btnExportar = document.getElementById('btnExportar');

if (btnExportar) {
    btnExportar.addEventListener('click', () => {
        const tabla = document.getElementById('tablaUsuarios');

        if (!tabla) return;

        let csv = [];
        const filas = tabla.querySelectorAll('tr');

        filas.forEach(fila => {
            const columnas = fila.querySelectorAll('th, td');
            let datos = [];

            columnas.forEach((columna, index) => {
                if (index !== columnas.length - 1) {
                    datos.push(`"${columna.innerText.trim().replace(/"/g, '""')}"`);
                }
            });

            csv.push(datos.join(','));
        });

        const archivo = new Blob([csv.join('\n')], {
            type: 'text/csv;charset=utf-8;'
        });

        const url = URL.createObjectURL(archivo);
        const enlace = document.createElement('a');

        enlace.href = url;
        enlace.download = 'usuarios_fucsia_boutique.csv';
        enlace.click();

        URL.revokeObjectURL(url);
    });
}