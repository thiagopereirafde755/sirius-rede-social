$(document).ready(function () {
    console.log("Documento pronto.");

    const urlParams = new URLSearchParams(window.location.search);
    const comentarioId = urlParams.get('comentario_id');
    const openCommentModal = urlParams.get('open_comment_modal');
    console.log("Parametro comentario_id:", comentarioId);
    console.log("Parametro open_comment_modal:", openCommentModal);

    const postId = $('body').data('post-id');
    console.log("Post ID:", postId);

    const modal = $('#commentModal-' + postId);
    console.log("Modal encontrado:", modal.length > 0);

    if (comentarioId) {
        console.log("Abrindo modal para comentário específico.");

        if (modal.length) {
            modal.modal('show');

            modal.on('shown.bs.modal', function () {
                console.log("Modal exibido.");

                const resposta = document.getElementById('comentario-' + comentarioId);
                console.log("Elemento resposta:", resposta);

                if (resposta) {
                    if ($(resposta).hasClass('resposta-comentario')) {
                        console.log("Comentário é uma resposta.");

                        const parentId = $(resposta).data('parent-comment-id');
                        console.log("ID do comentário pai:", parentId);

                        if (parentId) {
                            // Mostra todas as respostas
                            $('.comentario.resposta-comentario[data-parent-comment-id="' + parentId + '"]').removeClass('respostas-ocultas');
                            console.log("Respostas do pai exibidas.");
                            // $('#comentario-' + parentId).find('.btn-toggle-respostas').hide();
                        }
                    }

                    resposta.scrollIntoView({ behavior: "smooth", block: "center" });
                    $(resposta).addClass('comentario-destaque');
                    console.log("Comentário destacado e focado.");
                } else {
                    console.warn("Comentário com ID", comentarioId, "não encontrado.");

                    Swal.fire({
                        icon: 'warning',
                        title: 'Comentário não encontrado',
                        text: 'O comentário que você tentou acessar não está mais disponível.',
                        confirmButtonText: 'Fechar'
                    });
                }
            });
        } else {
            console.warn("Modal com ID 'commentModal-" + postId + "' não encontrado.");
        }
    } else if (openCommentModal) {
        console.log("Abrindo modal sem comentário específico.");

        if (modal.length) {
            modal.modal('show');
        } else {
            console.warn("Modal com ID 'commentModal-" + postId + "' não encontrado.");
        }
    } else {
        console.log("Nenhum parâmetro de comentário encontrado na URL.");
    }
});
