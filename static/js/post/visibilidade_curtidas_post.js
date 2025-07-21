 document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.curtidas-privadas').forEach(function (element) {
        element.addEventListener('click', function () {
            Swal.fire({
                icon: 'info',
                title: 'Curtidas privadas',
                html: 'A visibilidade das curtidas deste post é privada. Para mais informações, visite a <a target="_blank" href="/central_ajuda/curtidas_de_post" style="color: #3b7ddd; text-decoration: underline;">central de ajuda</a>.',
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'Entendi'
            });
        });
    });
});
