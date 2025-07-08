document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('post-textarea');
    const suggestionsContainer = document.getElementById('mention-suggestions');
    const contador = document.getElementById('contador-caracteres'); // Se você tiver contador de caracteres
    let currentMentionStart = -1;
    let users = [];

    if (!textarea || !suggestionsContainer) return;

    function getMentions(text) {
        return (text.match(/@([A-Za-z0-9_.-]+)/g) || []).map(m => m.slice(1).toLowerCase());
    }

    function atualizarContador() {
        if (contador) {
            contador.innerText = textarea.value.length;
        }
    }

    textarea.addEventListener('input', function(e) {
        const cursorPos = textarea.selectionStart;
        const textBeforeCursor = textarea.value.substring(0, cursorPos);
        const texto = textarea.value;
        const mentions = getMentions(texto);
        const uniqueMentions = [...new Set(mentions)];

        // 1. Limite de menções únicas
        if (uniqueMentions.length > 5) {
            textarea.value = textBeforeCursor.replace(/@[\w.-]*$/, '') + texto.substring(cursorPos);
            Swal.fire({
                icon: 'warning',
                title: 'Limite de menções atingido',
                text: 'Você pode mencionar no máximo 5 usuários diferentes por post.',
                confirmButtonColor: '#3085d6'
            });
            suggestionsContainer.style.display = 'none';
            atualizarContador();
            return;
        }

        // 2. Limite total de 280 caracteres
        const lastAt = textBeforeCursor.lastIndexOf('@');
        const afterAt = textBeforeCursor.substring(lastAt + 1);
        const isMention = lastAt !== -1 && /^[\w.-]*$/.test(afterAt);

        if (isMention && texto.length > 280) {
            textarea.value = texto.replace(/@[\w.-]*$/, ''); // remove menção parcial
            Swal.fire({
                icon: 'warning',
                title: 'Limite de caracteres',
                text: 'Sua menção faz a postagem ultrapassar o limite de 280 caracteres.',
                confirmButtonColor: '#3085d6'
            });
            atualizarContador();
            suggestionsContainer.style.display = 'none';
            return;
        }

        atualizarContador();

        // Busca de sugestões
        const lastAtPos = textBeforeCursor.lastIndexOf('@');
        if (lastAtPos > -1 && (lastAtPos === 0 || /\s/.test(textBeforeCursor[lastAtPos - 1]))) {
            const afterAt = textBeforeCursor.substring(lastAtPos + 1);
            const validUsernameMatch = afterAt.match(/^[a-zA-Z0-9_]*/);

            if (validUsernameMatch) {
                const searchTerm = validUsernameMatch[0].toLowerCase();
                currentMentionStart = lastAtPos;

                if (searchTerm.length > 0) {
                    fetch(`/buscar_usuarios?q=${encodeURIComponent(searchTerm)}`)
                        .then(response => response.json())
                        .then(data => {
                            users = data;
                            showSuggestions(users, uniqueMentions);
                        });
                } else {
                    suggestionsContainer.style.display = 'none';
                }
            }
        } else {
            suggestionsContainer.style.display = 'none';
        }
    });

    function showSuggestions(users, uniqueMentions) {
        if (users.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        suggestionsContainer.innerHTML = '';
        users.forEach(user => {
            if (uniqueMentions.includes(user.username.toLowerCase())) return;

            const div = document.createElement('div');
            div.className = 'mention-suggestion';
            div.innerHTML = `
                <img src="${user.fotos_perfil || '../static/img/icone/user.png'}" alt="${user.username}">
                <span class="username">${user.username}</span>
            `;

            div.addEventListener('click', function() {
                insertMention(user);
            });

            suggestionsContainer.appendChild(div);
        });

        if (!suggestionsContainer.hasChildNodes()) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        const textareaRect = textarea.getBoundingClientRect();
        suggestionsContainer.style.top = `${textareaRect.bottom + window.scrollY}px`;
        suggestionsContainer.style.left = `${textareaRect.left + window.scrollX}px`;
        suggestionsContainer.style.display = 'block';
    }

    function insertMention(user) {
        const mentions = getMentions(textarea.value);
        const uniqueMentions = [...new Set(mentions)];

        if (uniqueMentions.includes(user.username.toLowerCase())) {
            Swal.fire({
                icon: 'warning',
                title: 'Menção duplicada',
                text: 'Você já mencionou este usuário.',
                confirmButtonColor: '#3085d6'
            });
            suggestionsContainer.style.display = 'none';
            return;
        }

        if (uniqueMentions.length >= 5) {
            Swal.fire({
                icon: 'warning',
                title: 'Limite de menções atingido',
                text: 'Você pode mencionar no máximo 5 usuários diferentes por post.',
                confirmButtonColor: '#3085d6'
            });
            suggestionsContainer.style.display = 'none';
            return;
        }

        const texto = textarea.value;
        const before = texto.substring(0, currentMentionStart);
        const after = texto.substring(textarea.selectionStart);

        const novaMenção = `@${user.username} `;
        const novoTexto = before + novaMenção + after;

        if (novoTexto.length > 280) {
            Swal.fire({
                icon: 'warning',
                title: 'Limite de caracteres',
                text: 'Essa menção faz a postagem ultrapassar o limite de 280 caracteres.',
                confirmButtonColor: '#3085d6'
            });
            suggestionsContainer.style.display = 'none';
            return;
        }

        textarea.value = novoTexto;
        const newCursorPos = before.length + novaMenção.length;
        textarea.selectionStart = newCursorPos;
        textarea.selectionEnd = newCursorPos;
        textarea.focus();
        suggestionsContainer.style.display = 'none';
        atualizarContador();
    }

    document.addEventListener('click', function(e) {
        if (e.target !== textarea && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
});
