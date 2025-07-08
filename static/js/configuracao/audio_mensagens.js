$(document).ready(function() {
    $('#form-audio-notificacoes-mensagem').on('submit', function(e) {
        e.preventDefault();
        const url = $(this).data('url');
        const valor = $('#audio_notificacoes_mensagem').val(); // 'ativado' ou 'desativado'
        const formData = {
            audio_notificacoes_mensagem: valor
        };
        $.ajax({
            url: url,
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(formData),
            success: function(response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso!',
                    text: response.message,
                    timer: 2000,
                    showConfirmButton: false
                });
            },
            error: function(xhr) {
                let errorMsg = 'Erro ao atualizar notificações de áudio para mensagens';
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.error) errorMsg = response.error;
                } catch (e) {}
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: errorMsg
                });
            }
        });
    });
});