$(document).ready(function () {
    var isProcessing = false;

    $('.republicar-icon').click(function (e) {
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
            success: function (response) {
                if (response.error) {
                    alert(response.error);
                    isProcessing = false;
                    return;
                }

                // Atualiza o contador de republicações
                $('#republicados-count-' + postId).text(response.republicados);

                // Atualiza o ícone de republicar/desfazer
                if (response.republicado) {
                    icon.attr('src', '../static/img/icone/para_desfazer_republicacao.png')
                        .addClass('republicado');
                } else {
                    icon.attr('src', '../static/img/icone/para_republicar.png')
                        .removeClass('republicado');
                }

                // Atualiza o container HTML1 que mostra "por você"
                var textoRepuContainer = $('#texto-repu-container-' + postId);
                if (response.republicado) {
                    textoRepuContainer.html(
                        `<p class="text_repu" id="texto-repu-${postId}">
                            <i class='bx bx-repost'></i> Republicado por: <a class="dono_repu" href="/inicio">você</a>
                        </p>`
                    );
                } else {
                    textoRepuContainer.empty();
                }

                // Atualiza SÓ a parte "e por você" dentro da <span>, sem mexer no resto
                var repuPorVoce = $('#texto-repu-info-user-' + postId + ' .repu-por-voce');
                if (response.republicado) {
                    repuPorVoce.html(`e por <a class="dono_repu" href="/inicio">você</a>`);
                } else {
                    repuPorVoce.empty();
                }

                isProcessing = false;
            },
            error: function () {
                alert('Erro ao processar a republicação.');
                isProcessing = false;
            }
        });
    });

});
