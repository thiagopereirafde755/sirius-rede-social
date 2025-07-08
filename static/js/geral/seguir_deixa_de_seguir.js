function toggleSeguir(element) {
    const btn = $(element);
    const userId = btn.data('user-id');
    const postId = btn.data('post-id');
    const isSeguindo = btn.text().trim() === 'Deixar de seguir';

    $.ajax({
        url: '/toggle_seguir',
        type: 'POST',
        data: {
            user_id: userId,
            seguir: !isSeguindo
        },
        success: function(response) {
            if (response.success) {
                // Atualiza o texto e ícone do botão
                if (isSeguindo) {
                    btn.html("<i class='bx bx-user-plus'></i> Seguir");
                } else {
                    btn.html("<i class='bx bx-user-minus'></i> Deixar de seguir");
                }
                if (response.seguidores_count !== undefined) {
                    $(`#seguidores-count-${userId}`).text(response.seguidores_count);
                }
            } else {
                alert(response.message || 'Erro ao atualizar status de seguimento');
            }
        },
        error: function() {
            alert('Erro na comunicação com o servidor');
        }
    });
}