// Função para compartilhar post
function compartilharPost(postId) {
    const link = `${window.location.origin}/post/${postId}`;
    navigator.clipboard.writeText(link).then(() => {
        alert('Link copiado para a área de transferência: ' + link);
    }).catch(err => {
        console.error('Erro ao copiar o link: ', err);
    });
}