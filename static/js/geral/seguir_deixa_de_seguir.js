function toggleSeguir(element) {
    const btn = $(element);
    const userId = btn.data('user-id');
    const isSeguindo = btn.text().trim() === 'Deixar de seguir';
    const perfilPrivado = btn.data('perfil-publico') == 0;

    $.post('/toggle_seguir', {
        user_id: userId,
        seguir: !isSeguindo
    })
    .done(response => {
        if (!response.success) {
            alert(response.message || 'Erro ao atualizar status');
            return;
        }

        if (response.seguidores_count !== undefined) {
            $(`#seguidores-count-${userId}`).text(response.seguidores_count);
        }

        const botoesDoUsuario = $(`.seguir-btn[data-user-id='${userId}']`);

        if (isSeguindo) {
            if (perfilPrivado) {
                botoesDoUsuario.remove();
            } else {
                botoesDoUsuario.html("<i class='bx bx-user-plus'></i> Seguir");
            }
        } else {
            botoesDoUsuario.html("<i class='bx bx-user-minus'></i> Deixar de seguir");
        }
    })
    .fail(() => alert('Erro na comunicação com o servidor'));
}

document.addEventListener('DOMContentLoaded', function () {
    const dropdowns = document.querySelectorAll('.dropdown-menu');

    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function (e) {
            if (e.target.closest('.seguir-btn')) {
                e.stopPropagation(); // Impede que o clique feche o dropdown
            }
        });
    });
});