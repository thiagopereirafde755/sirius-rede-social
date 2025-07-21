$(document).ready(function() {
    var isProcessing = false;

    $('.curtir-icon').click(function(e) {
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
                    return;
                }

                // Atualiza o contador de curtidas
                $('#curtidas-count-' + postId).text(response.curtidas);

                // Alterna o ícone de curtir/descurtir
                if (response.curtido) {
                    icon.attr('src', '../static/img/icone/silhueta-de-formato-simples-de-coracao.png').addClass('curtido');
                } else {
                    icon.attr('src', '../static/img/icone/coracao-descurtido.png').removeClass('curtido');
                }

                isProcessing = false;
            },
            error: function(xhr, status, error) {
                isProcessing = false;
                alert('Erro ao curtir o post.');
            }
        });
    });
});