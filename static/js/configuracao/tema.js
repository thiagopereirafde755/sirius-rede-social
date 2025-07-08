$(document).ready(function() {
    $('#form-alterar-tema').on('submit', function(e) {
        e.preventDefault();

        const url = $(this).data('url');
        const tema = $('#tema').val();
        const formData = { tema };

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
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    // Redireciona para a tela de configuração
                    if(response.redirect_url){
                        window.location.href = response.redirect_url;
                    }
                });
            },
            error: function(xhr) {
                let errorMsg = 'Erro ao atualizar o tema';
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