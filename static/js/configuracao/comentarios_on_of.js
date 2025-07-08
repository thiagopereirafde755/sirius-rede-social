$(document).ready(function() {
    $('#form-visibilidade-comentarios').on('submit', function(e) {
        e.preventDefault();

        const url = $(this).data('url');
        const visibilidade = $('#comentarios_publicos').val(); // 'publico' ou 'privado'
        const formData = {
            comentarios_publicos: visibilidade === 'publico' ? 1 : 0
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
                let errorMsg = 'Erro ao atualizar configurações';
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.error) {
                        errorMsg = response.error;
                    }
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