function linkify(text) {
    // Expressão regular para detectar URLs
    const urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;

    return text.replace(urlRegex, function(url) {
        const maxLength = 30;
        const displayText = url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
        return '<a href="' + url + '" target="_blank" title="' + url + '">' + displayText + '</a>';
    });
}

document.querySelectorAll('.post-content').forEach(function(postContent) {
    if (!postContent.querySelector('a')) {
        postContent.innerHTML = linkify(postContent.textContent); // usa textContent para garantir que apenas texto puro seja processado
    }
});


// TESTE
function compartilharPost(postId) {
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
            copiarLink(url);
        });
    } else {
        
        copiarLink(url);
    }
}

function copiarLink(url) {
    navigator.clipboard.writeText(url)
        .then(() => alert("Link copiado: " + url))
        .catch(() => prompt("Copie manualmente:", url));
}