let usuariosRepublicaram = [];

$('#posts').on('click', '.republicados-lista-link', function () {
    const postId = $(this).data('post-id');
    $('#republicados-usuarios-lista').html('<div class="text-center">Carregando...</div>');
    $('#republicadosUsuariosModal').modal('show');
    $('#search-republicados-user').hide().val('');

    $.ajax({
        url: `/republicados/${postId}/usuarios`,
        method: 'GET',
        success: function (response) {
            usuariosRepublicaram = response.usuarios || [];
            renderizaUsuariosRepublicaram(usuariosRepublicaram);

            if (usuariosRepublicaram.length > 1) {
                $('#search-republicados-user').show();
            }
        },
        error: function () {
            $('#republicados-usuarios-lista').html('<p>Erro ao carregar usuários.</p>');
        }
    });
});

$('#search-republicados-user').on('input', function () {
    const termo = $(this).val().toLowerCase();
    const filtrados = usuariosRepublicaram.filter(user => user.username.toLowerCase().includes(termo));
    renderizaUsuariosRepublicaram(filtrados);
});

function renderizaUsuariosRepublicaram(lista) {
    let html = '';

    if (usuariosRepublicaram.length === 0) {
        html = `
            <div class="text-center">
                <i class='bx bxs-user-x' style="font-size:2rem;"></i><br>
                Ainda ninguém republicou este post.
            </div>
        `;
    } else if (lista.length === 0) {
        html = `
            <div class="text-center">
                <i class='bx bxs-user-x' style="font-size:2rem;"></i><br>
                Nenhum usuário encontrado.
            </div>
        `;
    } else {
        html += '<ul class="list-group">';
        lista.forEach(function (user) {
            const foto = user.fotos_perfil || '/static/img/icone/user.png';
            html += `
            <li class="list-group-item d-flex align-items-center p-0">
                <a href="/info-user/${user.id}" class="font-weight-bold d-flex align-items-center w-100 px-3 py-2 text-white text-decoration-none">
                    <img src="${foto}" width="32" height="32" class="rounded-circle mr-2">
                    ${user.username}
                </a>
            </li>
        `;

        });
        html += '</ul>';
    }

    $('#republicados-usuarios-lista').html(html);
}
