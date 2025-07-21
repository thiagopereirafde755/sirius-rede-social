document.addEventListener('DOMContentLoaded', function () {
    // CONFIRMAR REMOÇÃO DE POST
    function handleFormDeletarPost(form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            Swal.fire({
                title: 'Deseja remover este post?',
                text: 'Essa ação é irreversível.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, remover',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: 'Processando...',
                        text: 'Removendo o post e notificando o usuário...',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();

                            // Salva scroll antes de enviar o form
                            const tabelaDiv = document.querySelector('.table-responsive');
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

    document.querySelectorAll('.form-remover').forEach(handleFormDeletarPost);

    // RESTAURA SCROLL DA TABELA APÓS RELOAD
    const tabelaDiv = document.querySelector('.table-responsive');
    if (tabelaDiv) {
        const scrollPos = sessionStorage.getItem('scrollPosTabela');
        if (scrollPos) {
            tabelaDiv.scrollTop = parseInt(scrollPos, 10);
            sessionStorage.removeItem('scrollPosTabela');
        }
    }
});
