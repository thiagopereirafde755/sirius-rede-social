// Helper para encontrar a palavra depois de #
function getHashtagQuery(textarea) {
    const caret = textarea.selectionStart;
    const text = textarea.value.substring(0, caret);
    const match = text.match(/#(\w*)$/);
    return match ? '#' + match[1] : null;
}

const textarea = document.getElementById('post-textarea');
const suggestionsBox = document.getElementById('hashtag-suggestions');
const contador = document.getElementById('contador-caracteres');

// Atualiza contador de caracteres
function atualizarContador() {
    contador.innerText = textarea.value.length;
}

textarea.addEventListener('keyup', function () {
    const query = getHashtagQuery(textarea);
    if (query && query.length > 1) {
        fetch(`/autocomplete_hashtags?q=${encodeURIComponent(query)}`)
            .then(resp => resp.json())
            .then(data => {
                if (data.length > 0) {
                    let html = '';
                    data.forEach(item => {
                        html += `<div class="hashtag-suggestion-item" data-hashtag="${item.nome}">${item.nome} <span class="hashtag-count">${item.total}</span></div>`;
                    });
                    suggestionsBox.innerHTML = html;
                    suggestionsBox.style.display = 'block';
                    const rect = textarea.getBoundingClientRect();
                    suggestionsBox.style.left = rect.left + 'px';
                    suggestionsBox.style.top = (rect.top + window.scrollY - suggestionsBox.offsetHeight - 2) + 'px';
                    suggestionsBox.style.width = '220px';
                } else {
                    suggestionsBox.style.display = 'none';
                }
            });
    } else {
        suggestionsBox.style.display = 'none';
    }
});

// Clique para inserir hashtag sugerida
suggestionsBox.addEventListener('click', function (e) {
    if (e.target.classList.contains('hashtag-suggestion-item')) {
        const hashtag = e.target.getAttribute('data-hashtag');
        const caret = textarea.selectionStart;
        const texto = textarea.value;
        const before = texto.substring(0, caret).replace(/#\w*$/, hashtag);
        const after = texto.substring(caret);

        const novoTexto = before + after;

        // Validação: ultrapassa limite total?
        if (novoTexto.length > 280) {
            Swal.fire({
                icon: 'warning',
                title: 'Limite de caracteres',
                text: 'Essa hashtag faz a postagem ultrapassar os 280 caracteres.',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        // Validação: mais de 3 hashtags?
        if (contarHashtags(novoTexto) > 3) {
            Swal.fire({
                icon: 'warning',
                title: 'Limite atingido',
                text: 'Você só pode usar até 3 hashtags por postagem.',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        textarea.value = novoTexto;
        textarea.focus();
        suggestionsBox.style.display = 'none';
        atualizarContador();
    }
});

// Esconde caixa de sugestão se clicar fora
document.addEventListener('click', function (e) {
    if (!suggestionsBox.contains(e.target) && e.target !== textarea) {
        suggestionsBox.style.display = 'none';
    }
});

// Conta hashtags no texto
function contarHashtags(text) {
    return (text.match(/#[\wÀ-ÿ]{1,}/g) || []).length;
}

// Validações durante a digitação
textarea.addEventListener('input', function (e) {
    const texto = textarea.value;
    const caret = textarea.selectionStart;

    // 1. Limite de hashtags
    if (contarHashtags(texto) > 3) {
        Swal.fire({
            icon: 'warning',
            title: 'Limite atingido',
            text: 'Você só pode usar até 3 hashtags por postagem.',
            confirmButtonColor: '#3085d6'
        });
        textarea.value = texto.replace(/(#[\wÀ-ÿ]{1,})[^#]*$/, '');
        atualizarContador();
        return;
    }

    // 2. Limite de 20 caracteres por hashtag
    const query = getHashtagQuery(textarea);
    if (query && query.length > 21) {
        Swal.fire({
            icon: 'warning',
            title: 'Hashtag muito longa',
            text: 'Cada hashtag pode ter no máximo 20 caracteres.',
            confirmButtonColor: '#3085d6'
        });
        textarea.value = texto.substring(0, caret - 1) + texto.substring(caret);
        textarea.setSelectionRange(caret - 1, caret - 1);
        atualizarContador();
        return;
    }

    // 3. Limite total de 280 caracteres
    if (query && texto.length > 280) {
        Swal.fire({
            icon: 'warning',
            title: 'Limite de caracteres',
            text: 'Sua hashtag faz a postagem ultrapassar o limite de 280 caracteres.',
            confirmButtonColor: '#3085d6'
        });
        textarea.value = texto.replace(/#\w*$/, ''); // Remove hashtag parcial
        atualizarContador();
        return;
    }

    atualizarContador();
});
