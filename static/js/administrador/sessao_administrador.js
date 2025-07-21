document.addEventListener('DOMContentLoaded', function() {
    const swalConfig = {
        customClass: {
            popup: 'custom-swal-popup',
            title: 'custom-swal-title',
            content: 'custom-swal-content',
            confirmButton: 'custom-swal-confirm'
        },
        buttonsStyling: false,
        confirmButtonColor: '',
        background: '#2d2a32',
        color: '#e0e0e0'
    };

    function showAlert(success, message) {
        const config = {
            ...swalConfig,
            icon: success ? 'success' : 'error',
            title: success ? 'Sucesso' : 'Erro',
            text: message
        };
        
        Swal.fire(config);
    }

    // =====================
    // RESTAURA SCROLL DA TABELA AO CARREGAR
    // =====================
    const tabelaDiv = document.querySelector('.table-responsive');
    if (tabelaDiv) {
        const scrollPos = sessionStorage.getItem('scrollPosTabela');
        if (scrollPos) {
            tabelaDiv.scrollTop = parseInt(scrollPos, 10);
            sessionStorage.removeItem('scrollPosTabela');
        }
    }

    // =============================================================
    //  INSERIR ADMINISTRADOR via fetch (AJAX)
    // =============================================================
    const addAdminForm = document.querySelector('#modalAdicionarAdm form');
    if (addAdminForm) {
        addAdminForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
            
            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert(true, data.message);
                    setTimeout(() => {
                        bootstrap.Modal.getInstance(document.getElementById('modalAdicionarAdm')).hide();

                        // Salva scroll da tabela ANTES do reload
                        if (tabelaDiv) {
                            sessionStorage.setItem('scrollPosTabela', tabelaDiv.scrollTop);
                        }

                        window.location.reload();
                    }, 1500);
                } else {
                    showAlert(false, data.message);
                }
            } catch (error) {
                showAlert(false, 'Erro na comunicação com o servidor');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // =============================================================
    //  ALERT PARA SABER QUE ESTA É SUA CONTA
    // =============================================================
    const btnLogado = document.querySelector('.btn-logado');
    if (btnLogado) {
        btnLogado.addEventListener('click', function () {
            Swal.fire({
                icon: 'info',
                title: 'Este usuário é você!',
                text: 'Você está logado com essa conta.',
                confirmButtonText: 'OK'
            });
        });
    }

    // =============================================================
    //  EXCLUIR ADMINISTRADOR COM CONFIRMAÇÃO SWEETALERT
    // =============================================================
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const adminId = this.getAttribute('data-id');

            Swal.fire({
                title: 'Tem certeza?',
                text: 'Essa ação vai excluir o administrador!',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sim, excluir',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Salva scroll da tabela ANTES do redirecionamento
                    if (tabelaDiv) {
                        sessionStorage.setItem('scrollPosTabela', tabelaDiv.scrollTop);
                    }
                    window.location.href = `/deletar_administrador/${adminId}`;
                }
            });
        });
    });

    // =============================================================
    //  MODAL DE EDIÇÃO: preencher campos ao abrir o modal
    // =============================================================
    const modalEditar = document.getElementById('modalEditarAdm');
    const formEditar = modalEditar.querySelector('form');

    modalEditar.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const id = button.getAttribute('data-id');
        const user = button.getAttribute('data-user');
        const senha = button.getAttribute('data-senha');

        document.getElementById('edit-id').value = id;
        document.getElementById('edit-user').value = user;
        document.getElementById('edit-senha').value = senha;
    });

    // =============================================================
    //  CONFIRMAÇÃO SALVAR ALTERAÇÕES ADMIN
    // =============================================================
    formEditar.addEventListener('submit', function (e) {
        e.preventDefault(); 

        Swal.fire({
            title: 'Deseja salvar as alterações?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#aaa',
            confirmButtonText: 'Sim, salvar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Salva scroll da tabela ANTES do submit (que vai recarregar a página)
                if (tabelaDiv) {
                    sessionStorage.setItem('scrollPosTabela', tabelaDiv.scrollTop);
                }
                formEditar.submit(); 
            }
        });
    });
});
