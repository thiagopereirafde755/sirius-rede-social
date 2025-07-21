document.addEventListener('DOMContentLoaded', function () {

    // =============================================================
    // BOTÃO DE EXIBIR MODAL DO USUÁRIO
    // =============================================================
    const modalElement = document.getElementById('userDetailModal');
    const modal = new bootstrap.Modal(modalElement);

    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', () => {
            const nome = button.getAttribute('data-nome');
            const username = button.getAttribute('data-username');
            const bio = button.getAttribute('data-bio');
            const nascimento = button.getAttribute('data-nascimento');
            const cadastro = button.getAttribute('data-cadastro');
            const foto = button.getAttribute('data-foto');
            const fotoCapa = button.getAttribute('data-foto-capa');

            document.getElementById('modalUserNome').textContent = nome;
            document.getElementById('modalUserUsername').textContent = username;
            document.getElementById('modalUserBio').textContent = bio;
            document.getElementById('modalUserNascimento').textContent = nascimento;
            document.getElementById('modalUserCadastro').textContent = cadastro;
            document.getElementById('modalUserPhoto').setAttribute('src', foto);
            document.getElementById('modalUserCoverPhoto').setAttribute('src', fotoCapa);

            modal.show();
        });
    });

    // =============================================================
    // PARA SUSPENDER O USUÁRIO
    // =============================================================
    function handleFormSuspender(form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = form.querySelector('button').getAttribute('data-user');

            Swal.fire({
                title: `Suspender ${username}?`,
                text: "O usuário será impedido de acessar a rede social.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, suspender',
                cancelButtonText: 'Cancelar',
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: 'Processando...',
                        text: 'Suspendendo o usuário e enviando email de aviso...',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();

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

    // =============================================================
    // PARA REMOVER A SUSPENSÃO
    // =============================================================
    function handleFormRemover(form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = form.querySelector('button').getAttribute('data-user');

            Swal.fire({
                title: `Remover suspensão de ${username}?`,
                text: "O usuário poderá acessar normalmente.",
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sim, remover',
                cancelButtonText: 'Cancelar',
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        title: 'Processando...',
                        text: 'Removendo suspensão e enviando email de aviso...',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();

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

    document.querySelectorAll('.form-suspender').forEach(handleFormSuspender);
    document.querySelectorAll('.form-remover').forEach(handleFormRemover);

    // =============================================================
    // RESTAURA SCROLL AO CARREGAR A PÁGINA
    // =============================================================
    const tabelaDiv = document.querySelector('.table-responsive');
    if (tabelaDiv) {
        const scrollPos = sessionStorage.getItem('scrollPosTabela');
        if (scrollPos) {
            tabelaDiv.scrollTop = parseInt(scrollPos, 10);
            sessionStorage.removeItem('scrollPosTabela');
        }
    }

});