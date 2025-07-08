$(document).ready(function() {
    let usuariosCurtiram = []; // Guarda a lista completa para filtrar

    // Ao clicar no link de curtidas, abre o modal e carrega usuários
    $('#posts').on('click', '.curtidas-lista-link', function() {
        var postId = $(this).data('post-id');
        $('#curtidas-usuarios-lista').html('<div class="text-center">Carregando...</div>');
        $('#curtidasUsuariosModal').modal('show');
        $("#search-curtidas-user").hide().val(""); // Reseta busca

        $.ajax({
            url: `/curtidas/${postId}/usuarios`,
            method: 'GET',
            success: function(response) {
                usuariosCurtiram = response.usuarios || [];
                renderizaUsuariosCurtiram(usuariosCurtiram);

                if (usuariosCurtiram.length > 1) {
                    $("#search-curtidas-user").show();
                } else {
                    $("#search-curtidas-user").hide();
                }
            },
            error: function() {
                $('#curtidas-usuarios-lista').html('<p>Erro ao carregar usuários.</p>');
            }
        });
    });

    // Filtro de busca
    $("#search-curtidas-user").on("input", function() {
        const termo = $(this).val().toLowerCase();
        const filtrados = usuariosCurtiram.filter(user => user.username.toLowerCase().includes(termo));
        renderizaUsuariosCurtiram(filtrados);
    });

    function renderizaUsuariosCurtiram(lista) {
        let html = '';
        // Ninguém nunca curtiu o post
        if (usuariosCurtiram.length === 0) {
            html = `
                <div class="text-center">
                    <i class='bx bxs-user-x' style="font-size:2rem;"></i>
                    <br>
                    Ainda ninguém curtiu este post.
                </div>
            `;
        }
        // Já teve curtidas, mas filtro não encontrou ninguém
        else if (lista.length === 0) {
            html = `
                <div class="text-center">
                    <i class='bx bxs-user-x' style="font-size:2rem;"></i>
                    <br>
                    Nenhum usuário encontrado.
                </div>
            `;
        }
        // Mostra usuários encontrados
        else {
            html += '<ul class="list-group">';
            lista.forEach(function(user) {
                var foto = user.fotos_perfil ? `/static/${user.fotos_perfil}` : '/static/img/icone/user.png';
                html += `
                    <li class="list-group-item d-flex align-items-center">
                        <a href="/info-user/${user.id}" class="font-weight-bold">
                            <img src="${foto}" width="32" height="32" class="rounded-circle mr-2" alt="Foto de perfil">
                            ${user.username}
                        </a>
                    </li>
                `;
            });
            html += '</ul>';
        }
        $('#curtidas-usuarios-lista').html(html);
    }
});