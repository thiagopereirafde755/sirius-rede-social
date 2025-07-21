document.addEventListener('DOMContentLoaded', function () {
    const tabelaDiv = document.querySelector('.table-responsive');

    function handleFormRemocao(form, textoConfirmacao, textoLoading) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            Swal.fire({
                title: 'Tem certeza?',
                text: textoConfirmacao,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, remover',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: 'Processando...',
                        text: textoLoading,
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            Swal.showLoading();

                            if (tabelaDiv) {
                                sessionStorage.setItem('scrollPosTabela', tabelaDiv.scrollTop);
                            }

                            form.submit();
                        }
                    });
                }
            });
        });
    }

    document.querySelectorAll('.form-remover').forEach(form => {
        const isComentario = form.action.includes('/deletar_comentario/');
        const confirmText = isComentario
            ? 'O comentário será removido e o usuário notificado.'
            : 'O post será removido e o usuário notificado.';
        const loadingText = isComentario
            ? 'Removendo comentário e notificando o usuário...'
            : 'Removendo post e notificando o usuário...';

        handleFormRemocao(form, confirmText, loadingText);
    });

    if (tabelaDiv) {
        const scrollPos = sessionStorage.getItem('scrollPosTabela');
        if (scrollPos) {
            tabelaDiv.scrollTop = parseInt(scrollPos, 10);
            sessionStorage.removeItem('scrollPosTabela');
        }
    }
});