$(document).ready(function() {
    $('#form-modo-status').on('submit', function(e) {
        e.preventDefault();
        const url = $(this).data('url');
        const valor = $('#modo_status').val();
        const formData = { modo_status: valor };
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
                let errorMsg = 'Erro ao atualizar modo de status';
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