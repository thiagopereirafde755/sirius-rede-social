 // Compartilhar link do comentário
$(document).on('click', '.btn-compartilhar-comentario', function(e) {
    e.preventDefault();
    const postId = $(this).data('post-id');
    const comentarioId = $(this).data('comentario-id');
    // Monta o link igual notificação (abre modal e rola até comentário)
    const url = `${window.location.origin}/post/${postId}?comentario_id=${comentarioId}`;
    const titulo = "Veja este comentário!";

    if (navigator.share) {
        navigator.share({
            title: titulo,
            text: "Veja esse comentário que encontrei:",
            url: url,
        }).catch(err => {
            copiarLink(url); // fallback
        });
    } else {
        copiarLink(url);
    }
});

// Função para copiar link (você já tem)
function copiarLink(url) {
    navigator.clipboard.writeText(url)
        .then(() => alert("Link copiado: " + url))
        .catch(() => prompt("Copie manualmente:", url));
}