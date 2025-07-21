$(document).on('click', '.btn-compartilhar-comentario', function(e) {
    e.preventDefault();
    const postId = $(this).data('post-id');
    const comentarioId = $(this).data('comentario-id');
    const url = `${window.location.origin}/post/${postId}?comentario_id=${comentarioId}`;
    const titulo = "Veja este comentário!";

    if (navigator.share) {
        navigator.share({
            title: titulo,
            text: "Veja esse comentário que encontrei:",
            url: url,
        }).catch(err => {
            copiarLink(url);
        });
    } else {
        copiarLink(url);
    }
});

function copiarLink(url) {
    navigator.clipboard.writeText(url)
        .then(() => alert("Link copiado: " + url))
        .catch(() => prompt("Copie manualmente:", url));
}