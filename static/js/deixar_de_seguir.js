$(document).on('submit', '.deixar-seguir-form', function(e) {
    e.preventDefault();
    var $form = $(this);

    Swal.fire({
        title: 'Tem certeza?',
        text: "Deseja deixar de seguir este usuário?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, deixar de seguir',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: $form.attr('action'),
                method: 'POST',
                data: $form.serialize(),
                success: function(response) {
                    if (response.success) {
                        $form.closest('li.seguindo-li').fadeOut(300, function() {
                            $(this).remove();

                            // Checa se ainda há alguém seguido visível
                            const $seguindoList = $('#seguindo-list');
                            const $searchInput = $('#search-seguindo');

                            if ($seguindoList.find('li.seguindo-li:visible').length === 0) {
                                // Mostra mensagem de "não segue ninguém"
                                if ($('#no-following-message').length === 0) {
                                    $('#body-do-seguindo').append(`
                                        <div id="no-following-message" class="text-center" style="color: #fff; margin-top: 30px;">
                                            <i class='bx bx-user-x' style="font-size:2.5rem;"></i>
                                            <p>Você não segue ninguém</p>
                                        </div>
                                    `);
                                } else {
                                    $('#no-following-message').show();
                                }
                                // Opcional: desabilita o campo de busca se lista vazia
                                $searchInput.prop('disabled', true);
                            } else {
                                // Remove mensagem e garante que search fica habilitado
                                $('#no-following-message').hide();
                                $searchInput.prop('disabled', false);
                            }
                        });

                        // Atualizar o contador de seguindo
                        if (response.seguindo_count !== undefined) {
                            $('.stat-item .total').eq(1).text(response.seguindo_count);
                        }

                        Swal.fire({
                            icon: 'success',
                            title: 'Removido!',
                            text: 'Você deixou de seguir este usuário.',
                            timer: 1500,
                            showConfirmButton: false
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Erro',
                            text: response.error || 'Erro ao deixar de seguir!'
                        });
                    }
                },
                error: function() {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro',
                        text: 'Erro ao deixar de seguir!'
                    });
                }
            });
        }
    });
});