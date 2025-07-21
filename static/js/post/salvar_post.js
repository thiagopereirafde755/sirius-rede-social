$(document).ready(function() {
    var isProcessing = false;

    // Clique no ícone de salvar/desfazer salvamento
    $('.salvar-icon').click(function(e) {
        e.preventDefault();

        if (isProcessing) return;

        var icon = $(this);
        var postId = icon.data('post-id');
        var form = icon.closest('form');
        var url = form.attr('action');

        isProcessing = true;

        $.ajax({
            url: url,
            method: 'POST',
            success: function(response) {
                if (response.error) {
                    alert(response.error);
                    isProcessing = false;
                    return;
                }

                // Atualiza o contador de salvos
                $('#salvo-count-' + postId).text(response.salvados);

                // Atualiza o ícone dependendo do novo estado
                if (response.salvado) {
                    icon.attr('src', '../static/img/icone/salvo.png')
                        .addClass('salvo');
                } else {
                    icon.attr('src', '../static/img/icone/nao_salvo.png')
                        .removeClass('salvo');
                }

                isProcessing = false;
            },
            error: function() {
                isProcessing = false;
                alert('Erro ao salvar o post.');
            }
        });
    });

    // Clique no contador para abrir alerta explicativo
    $(document).on('click', '.salvo-count', function() {
        Swal.fire({
            title: 'Quantidade de Salvos',
            html: 'Esse número mostra quantas vezes esse post foi salvo por outros usuários. Para mais informações, visite a <a target="_blank" href="/central_ajuda/salvo_post" style="color: #3b7ddd; text-decoration: underline;">central de ajuda</a>.',
            icon: 'info',
            confirmButtonText: 'Entendi!',
            customClass: {
                popup: 'meu-sweetalert'
            }
        });
    });
});
