document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Impede envio imediato

        Swal.fire({
            title: 'Entrando...',
            html: 'Aguarde.',
            allowOutsideClick: false,
            allowEscapeKey: false,
            background: '#2d2a32',
            color: '#e0e0e0',
            didOpen: () => {
                Swal.showLoading();
            }
        });

        setTimeout(() => {
            form.submit();
        }, 300); // Leve atraso para mostrar o alert antes do envio
    });
});
