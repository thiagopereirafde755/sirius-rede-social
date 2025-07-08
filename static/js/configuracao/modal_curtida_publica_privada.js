$(document).ready(function() {
    $('#form-curtidas-publicas').on('submit', function(e) {
        e.preventDefault();

        const url = $(this).data('url');
        const valor = $('#curtidas_publicas').val(); // 'publico' ou 'privado'
        const formData = {
            curtidas_publicas: valor
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
                let errorMsg = 'Erro ao atualizar curtidas';
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