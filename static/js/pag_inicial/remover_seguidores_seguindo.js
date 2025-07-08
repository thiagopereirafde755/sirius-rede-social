    function ajustarCampoBuscaSeguidores() {
    const $lista = $('#seguidores-list');
    const $search = $('#search-seguidor');
    const totalVisiveis = $lista.find('li.seguidor-li:visible').length;
    if (totalVisiveis > 1) {
        if ($search.length === 0) {
            // Adiciona o campo de busca se não existe e há mais de 1 seguidor
            $('#body-do-seguidores').prepend(`
                <input type="text" id="search-seguidor" class="form-control mb-2" placeholder="Buscar seguidor...">
            `);
        } else {
            $search.show();
        }
    } else {
        $search.hide();
    }
}

function ajustarCampoBuscaSeguindo() {
    const $lista = $('#seguindo-list');
    const $search = $('#search-seguindo');
    const totalVisiveis = $lista.find('li.seguindo-li:visible').length;
    if (totalVisiveis > 1) {
        if ($search.length === 0) {
            $('#body-do-seguindo').prepend(`
                <input type="text" id="search-seguindo" class="form-control mb-2" placeholder="Buscar seguindo...">
            `);
        } else {
            $search.show();
        }
    } else {
        $search.hide();
    }
}

// Chame essas funções SEMPRE após remover alguém
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
                            ajustarCampoBuscaSeguidores();

                            const $lista = $('#seguidores-list');
                            if ($lista.find('li.seguidor-li:visible').length === 0) {
                                $lista.hide();
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
                                $('#search-seguidor').hide();
                            } else {
                                $('#no-followers-message').hide();
                            }
                        });
                        // Atualiza contador etc...
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
                            ajustarCampoBuscaSeguindo();

                            const $lista = $('#seguindo-list');
                            if ($lista.find('li.seguindo-li:visible').length === 0) {
                                $lista.hide();
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
                                $('#search-seguindo').hide();
                            } else {
                                $('#no-following-message').hide();
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

// Opcional: garanta o comportamento correto ao abrir o modal (ex: ao recarregar ou reabrir)
$('#seguidoresModal').on('shown.bs.modal', ajustarCampoBuscaSeguidores);
$('#seguindoModal').on('shown.bs.modal', ajustarCampoBuscaSeguindo);