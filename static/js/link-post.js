function linkify(text) {
    // Expressão regular para detectar URLs
    const urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;

    // Substitui URLs por links clicáveis com texto truncado
    return text.replace(urlRegex, function(url) {
        // Define o comprimento máximo do texto do link
        const maxLength = 30;
        // Trunca o texto do link se for muito longo
        const displayText = url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
        // Retorna o link com o texto truncado, mas o href contém a URL completa
        return '<a href="' + url + '" target="_blank" title="' + url + '">' + displayText + '</a>';
    });
}

// Aplicar a função a todos os posts, mas apenas se o conteúdo não contiver links
document.querySelectorAll('.post-content').forEach(function(postContent) {
    // Verifica se já existem links no conteúdo, para evitar duplicação
    if (!postContent.querySelector('a')) {
        postContent.innerHTML = linkify(postContent.textContent); // usa textContent para garantir que apenas texto puro seja processado
    }
});




// TESTE
function compartilharPost(postId) {
    // Monta a URL do post (ajuste conforme sua rota)
    const url = `${window.location.origin}/post/${postId}`;
    const titulo = "Confira este post incrível!";

    if (navigator.share) {
        navigator.share({
            title: titulo,
            text: "Veja este post que encontrei:",
            url: url,
        })
        .catch(err => {
            console.error("Erro ao compartilhar:", err);
            copiarLink(url); // Fallback: copia o link se o compartilhamento falhar
        });
    } else {
        // Fallback para navegadores que não suportam a API
        copiarLink(url);
    }
}

function copiarLink(url) {
    navigator.clipboard.writeText(url)
        .then(() => alert("Link copiado: " + url))
        .catch(() => prompt("Copie manualmente:", url));
}