document.addEventListener('DOMContentLoaded', function () {
    // === BOTÃO DE EDITAR ===
    const editButtons = document.querySelectorAll('.btn-edit');

    editButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const remetente = this.getAttribute('data-remetente');
            const destinatario = this.getAttribute('data-destinatario');
            const mensagem = this.getAttribute('data-mensagem');
            const dataEnvio = this.getAttribute('data-data');
            const caminho = this.getAttribute('data-caminho');
            const postId = this.getAttribute('data-post_id') || '-';


            // Preencher o modal
            document.getElementById('modalMessageId').textContent = id;
            document.getElementById('modalMessageSender').textContent = remetente;
            document.getElementById('modalMessageReceiver').textContent = destinatario;
            document.getElementById('modalMessageContent').textContent = mensagem;
            document.getElementById('modalMessageDate').textContent = dataEnvio;
            document.getElementById('modalMessagePostId').textContent = postId;

            const mediaContainer = document.getElementById('modalMediaContainer');
            mediaContainer.innerHTML = ''; // limpa o conteúdo anterior

            if (caminho) {
                if (caminho.match(/\.(mp4|webm|ogg)$/i)) {
                    const video = document.createElement('video');
                    video.src = caminho;
                    video.controls = true;
                    video.classList.add('w-100');
                    mediaContainer.appendChild(video);
                } else {
                    const img = document.createElement('img');
                    img.src = caminho;
                    img.classList.add('img-fluid');
                    mediaContainer.appendChild(img);
                }
            }

            // Mostrar o modal
            const modal = new bootstrap.Modal(document.getElementById('messageDetailModal'));
            modal.show();
        });
    });

    // === BOTÃO DE DELETAR ===
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', () => {
            const id = button.dataset.id;

            Swal.fire({
                title: 'Tem certeza?',
                text: "Esta ação não poderá ser desfeita!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sim, excluir!',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Mostrar modal de loading
                    Swal.fire({
                        title: 'Processando...',
                        text: 'Por favor, aguarde.',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });

                    fetch(`/excluir_mensagem/${id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        Swal.close(); // fecha o loading

                        if (data.success) {
                            Swal.fire(
                                'Excluído!',
                                data.msg,
                                'success'
                            ).then(() => {
                                button.closest('tr').remove();
                            });
                        } else {
                            Swal.fire('Erro', data.msg || 'Falha ao excluir.', 'error');
                        }
                    })
                    .catch(() => {
                        Swal.close(); // fecha o loading
                        Swal.fire('Erro', 'Falha na conexão com o servidor.', 'error');
                    });
                }
            });
        });
    });
});
