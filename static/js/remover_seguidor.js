$(document).on('submit', '.remover-seguidor-form', function(e) {
    e.preventDefault();
    var $form = $(this);

    Swal.fire({
        title: 'Tem certeza?',
        text: "Você quer remover esse seguidor?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, remover',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: $form.attr('action'),
                method: 'POST',
                data: $form.serialize(),
                success: function(response) {
                    if (response.success) {
                        $form.closest('li.seguidor-li').fadeOut(300, function() {
                            $(this).remove();

                            // Checa se ainda há seguidores na lista
                            const $seguidorList = $('#seguidores-list');
                            const $searchInput = $('#search-seguidor');

                            if ($seguidorList.find('li.seguidor-li:visible').length === 0) {
                                // Mostra mensagem de "nenhum seguidor"
                                if ($('#no-followers-message').length === 0) {
                                    $('#body-do-seguidores').append(`
                                        <div id="no-followers-message" class="text-center" style="color: #fff; margin-top: 30px;">
                                            <i class='bx bx-user-x' style="font-size:2.5rem;"></i>
                                            <p>Você não tem nenhum seguidor</p>
                                        </div>
                                    `);
                                } else {
                                    $('#no-followers-message').show();
                                }
                                // Opcional: desabilita o campo de busca se a lista estiver vazia
                                $searchInput.prop('disabled', true);
                            } else {
                                // Garante que a mensagem não aparece e reabilita o campo de busca
                                $('#no-followers-message').hide();
                                $searchInput.prop('disabled', false);
                            }
                        });

                        // Atualiza o contador de seguidores
                        if (response.seguidores_count !== undefined) {
                            $('.stat-item .total').first().text(response.seguidores_count);
                        }

                        Swal.fire({
                            icon: 'success',
                            title: 'Removido!',
                            text: 'O seguidor foi removido com sucesso.',
                            timer: 1500,
                            showConfirmButton: false
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro',
                            text: response.error || 'Erro ao remover seguidor!'
                        });
                    }
                },
                error: function() {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro',
                        text: 'Erro ao remover seguidor!'
                    });
                }
            });
        }
    });
});