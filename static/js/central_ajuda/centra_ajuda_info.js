document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.faq-item').forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();

            const mensagem = this.getAttribute('data-mensagem');

            Swal.fire({
                icon: 'info',
                title: 'Resposta',
                text: mensagem,
                confirmButtonText: 'Entendi!',
                confirmButtonColor: '#3085d6'
            });
        });
    });
});
