$(document).ready(function() {
    $('#detalhesUsuario').on('input', function() {
        const length = $(this).val().length;
        $('#contadorDetalhesUsuario').text(length + '/80');
    });

    $(document).on('click', '.btn-denunciar-usuario', function(e) {
        e.preventDefault();
        const usuarioId = $(this).data('id');
        $('#denunciaUsuarioId').val(usuarioId);
        $('#modalDenunciarUsuario').modal('show');
    });

    $('#formDenunciaUsuario').on('submit', function(e) {
        e.preventDefault();
        const formData = $(this).serialize();

        $.ajax({
            url: '/denunciar_usuario',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Denúncia enviada',
                        text: 'Obrigado por ajudar a manter nossa comunidade segura!',
                        timer: 1500,
                        showConfirmButton: false,
                        didClose: () => {
                            $('#modalDenunciarUsuario').modal('hide');
                            $('#formDenunciaUsuario')[0].reset();
                            $('#contadorDetalhesUsuario').text('0/80');
                        }
                    });
                } else {
                    Swal.fire({ icon: 'error', title: 'Erro', text: response.message });
                }
            },
            error: function() {
                Swal.fire({ icon: 'error', title: 'Erro', text: 'Erro ao enviar denúncia. Tente novamente.' });
            }
        });
    });
});
