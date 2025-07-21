$(document).on('click', '.btn-compartilhar-perfil', function(e) {
    e.preventDefault();
    const idUsuario = $(this).data('id');
    const url = `${window.location.origin}/info-user/${idUsuario}`;
    const titulo = "Veja este perfil!";
    if (navigator.share) {
        navigator.share({
            title: titulo,
            text: "Veja esse perfil:",
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

