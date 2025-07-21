// Bloquear scroll ao abrir qualquer modal com classe "modal-de-comentario"
$('.modal-de-comentario').on('show.bs.modal', function () {
  $('body').css('overflow', 'hidden');
});

// Liberar scroll ao fechar
$('.modal-de-comentario').on('hidden.bs.modal', function () {
  $('body').css('overflow', '');
});

function atualizarContadorComentarios(postId) {
    fetch(`/comentarios_count/${postId}`)
      .then(response => response.json())
      .then(data => {
        const countElem = document.getElementById(`comment-count-${postId}`);
        if (countElem) countElem.textContent = data.count;
      });
}

function recarregarComentarios(postId) {
    const btn = document.querySelector(`#commentModal-${postId} .btn-recarregar-comentarios`);
    if (btn) btn.disabled = true;

    fetch(window.location.href, { cache: "reload" })
        .then(response => response.text())
        .then(html => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            // Atualiza lista de comentários
            const novaDivComentarios = tempDiv.querySelector(`#commentModal-${postId} .comentarios`);
            const atualDivComentarios = document.querySelector(`#commentModal-${postId} .comentarios`);
            if (novaDivComentarios && atualDivComentarios) {
                atualDivComentarios.innerHTML = novaDivComentarios.innerHTML;
                inicializarContadores();
                atualDivComentarios.querySelectorAll('textarea[name="comentario"]').forEach(setupMentionInput);
            }

            const novaCommentInput = tempDiv.querySelector(`#commentModal-${postId} .comment-input`);
            const atualCommentInput = document.querySelector(`#commentModal-${postId} .comment-input`);
            if (novaCommentInput && atualCommentInput) {
                atualCommentInput.innerHTML = novaCommentInput.innerHTML;
                atualCommentInput.querySelectorAll('textarea[name="comentario"]').forEach(setupMentionInput);
            }

            atualizarContadorComentarios(postId);

        })
        .finally(() => { if (btn) btn.disabled = false; })
        .catch(() => { alert('Erro ao recarregar comentários!'); if (btn) btn.disabled = false; });
}

// Função para atualizar contador de caracteres
function atualizarContador(input, contadorElement, limite) {
    const tamanho = input.value.length;
    contadorElement.textContent = `${tamanho}/${limite}`;
    if (tamanho > limite) {
        contadorElement.classList.add('contador-excedido');
    } else {
        contadorElement.classList.remove('contador-excedido');
    }
}

// Função para limitar caracteres e exibir alerta
function limitarCaracteres(input, contadorElement, limite) {
    atualizarContador(input, contadorElement, limite);

    input.addEventListener('input', function() {
        if (input.value.length > limite) {
            input.value = input.value.substring(0, limite);
        }
        atualizarContador(input, contadorElement, limite);
    });
}

// Inicializa contador em todos os textareas de comentário
function inicializarContadores() {
    document.querySelectorAll('textarea[name="comentario"]').forEach(function(input) {
        if (input._contadorAdicionado) return;
        input._contadorAdicionado = true;

        const limite = 300;

        input.addEventListener('input', function () {
            if (input.value.length > limite) {
                input.value = input.value.substring(0, limite);
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', inicializarContadores);

const observer = new MutationObserver(inicializarContadores);
observer.observe(document.body, { childList: true, subtree: true });

// TOGGLE VISIBILIDADE DAS RESPOSTAS
function toggleRespostas(button) {
    const comentarioId = button.getAttribute('data-comentario-id');
    const comentarioPrincipal = button.closest('.comentario');
    const postId = comentarioPrincipal.dataset.postId;
    
    const todasRespostas = document.querySelectorAll(`.resposta-comentario[data-post-id="${postId}"]`);
    const respostas = Array.from(todasRespostas).filter(resposta => {
        if (resposta.previousElementSibling === comentarioPrincipal) return true;
        
        let prev = resposta.previousElementSibling;
        while (prev && prev.classList.contains('resposta-comentario')) {
            if (prev.previousElementSibling === comentarioPrincipal) return true;
            prev = prev.previousElementSibling;
        }
        return false;
    });
    
    if (respostas.length > 0) {
        const isHidden = respostas[0].classList.contains('respostas-ocultas');
        
        // Alternar visibilidade
        respostas.forEach(resposta => {
            resposta.classList.toggle('respostas-ocultas', !isHidden);
        });
        
        // Atualizar ícone e texto
        const icon = isHidden ? 'bx-chevron-up' : 'bx-chevron-down';
        const text = isHidden ? 'Ocultar' : 'Mostrar';
        button.innerHTML = `<i class='bx ${icon}'></i> ${text} respostas (${respostas.length})`;
    }
}

// MOSTRA O FORMULARIO DE RESPOSTA
function mostrarFormResposta(button) {
    const formsAbertos = document.querySelectorAll('.form-resposta.mostrar-resposta');
    formsAbertos.forEach(form => {
        form.classList.remove('mostrar-resposta');
    });
    
    const formResposta = button.nextElementSibling;
    formResposta.classList.add('mostrar-resposta');
    formResposta.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ESCONDE O FORMULARIO DE RESPOSTA
function esconderFormResposta(button) {
    const formResposta = button.closest('.form-resposta');
    formResposta.classList.remove('mostrar-resposta');
}

// Função para ativar autocomplete de menção em um input específico
function setupMentionInput(input) {
    if (!input || input._mentionSetup) return; 
    input._mentionSetup = true;

    let currentMentionStart = -1;
    let users = [];
    let suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'mention-suggestions';
    suggestionsContainer.style.position = 'absolute';
    suggestionsContainer.style.display = 'none';
    suggestionsContainer.style.zIndex = 9999;
    document.body.appendChild(suggestionsContainer);

    function getMentions(text) {
        return (text.match(/@([A-Za-z0-9_.-]+)/g) || []).map(m => m.slice(1).toLowerCase());
    }

    function positionContainer() {
        const rect = input.getBoundingClientRect();
        // Aparecer acima do input
        const containerHeight = suggestionsContainer.offsetHeight || 180;
        suggestionsContainer.style.top = `${rect.top + window.scrollY - containerHeight - 4}px`;
        suggestionsContainer.style.left = `${rect.left + window.scrollX}px`;
        suggestionsContainer.style.width = `${rect.width}px`;
    }

    input.addEventListener('input', function(e) {
        const cursorPos = input.selectionStart;
        const textBeforeCursor = input.value.substring(0, cursorPos);

        const mentions = getMentions(input.value);
        const uniqueMentions = [...new Set(mentions)];
        if (uniqueMentions.length > 5) {
            input.value = input.value.substring(0, cursorPos - 1) + input.value.substring(cursorPos);
            Swal.fire({
                icon: 'warning',
                title: 'Limite de menções atingido',
                text: 'Você pode mencionar no máximo 5 usuários diferentes por comentário.',
                confirmButtonColor: '#3085d6'
            });
            suggestionsContainer.style.display = 'none';
            return;
        }

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
            div.addEventListener('mousedown', function(e) {
                e.preventDefault(); 
                insertMention(user);
            });
            suggestionsContainer.appendChild(div);
        });
        if (!suggestionsContainer.hasChildNodes()) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        positionContainer();
        suggestionsContainer.style.display = 'block';
    }

function insertMention(user) {
    const mentions = getMentions(input.value);
    const uniqueMentions = [...new Set(mentions)];

    // Menção duplicada
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

    // Limite de menções
    if (uniqueMentions.length >= 5) {
        Swal.fire({
            icon: 'warning',
            title: 'Limite de menções atingido',
            text: 'Você pode mencionar no máximo 5 usuários diferentes por comentário.',
            confirmButtonColor: '#3085d6'
        });
        suggestionsContainer.style.display = 'none';
        return;
    }

    const text = input.value;
    const before = text.substring(0, currentMentionStart);
    const after = text.substring(input.selectionStart);
    const novaMencao = `@${user.username} `;

    const novoTamanho = before.length + novaMencao.length + after.length;

    // Verifica se ultrapassa o limite de 300
    if (novoTamanho > 300) {
        Swal.fire({
            icon: 'warning',
            title: 'Limite de caracteres excedido',
            text: `A menção ultrapassaria o limite de caracteres.`,
            confirmButtonColor: '#3085d6'
        });
        suggestionsContainer.style.display = 'none';
        return;
    }

    // Insere menção
    input.value = before + novaMencao + after;

    // Reposiciona cursor
    const newCursorPos = before.length + novaMencao.length;
    input.selectionStart = input.selectionEnd = newCursorPos;
    input.focus();

    suggestionsContainer.style.display = 'none';

    // Atualiza contador se tiver
    const contador = input.parentNode.querySelector('.contador-caracteres');
    if (contador) atualizarContador(input, contador, 300);
}


    document.addEventListener('mousedown', function(e) {
        if (e.target !== input && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });

    input.addEventListener('blur', function() {
        setTimeout(() => suggestionsContainer.style.display = 'none', 150);
    });

    window.addEventListener('scroll', positionContainer);
    input.addEventListener('focus', positionContainer);
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('textarea[name="comentario"]').forEach(setupMentionInput);
});

// ENVIA RESPOSTA A COMENTÁRIO
function submitReply(event, postId, parentCommentId) {
    event.preventDefault();

    const form = event.target;
    const comentario = form.querySelector('textarea[name="comentario"]').value;

    fetch(`/comentar/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'comentario': comentario,
            'parent_comment_id': parentCommentId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            form.querySelector('textarea[name="comentario"]').value = '';
            form.classList.remove('mostrar-resposta');

            const parentComment = document.querySelector(`.comentario[data-comentario-id="${parentCommentId}"]`);
            const fotoPerfil = data.fotos_perfil ? data.fotos_perfil : '../static/img/icone/user.png';

            const parentUserLink = data.parent_usuario_id && data.parent_username 
                ? (data.parent_usuario_id == data.usuario_id
                    ? `<a href="/inicio" class="username-link">${data.parent_username}</a>`
                    : `<a href="/info-user/${data.parent_usuario_id}" class="username-link">${data.parent_username}</a>`)
                : '';

            const newReply = `
            <div class="comentario resposta-comentario" data-comentario-id="${data.comentario_id}" data-post-id="${postId}">
                <p>
                    <a href="/inicio">
                        <img src="${fotoPerfil}" style="border-radius:50%;" alt="${data.username}'s foto" class="foto-perfil-comentario">
                        <strong>${data.username}:</strong>
                    </a>
                    ${parentUserLink ? `<span class="resposta-para"> resposta para ${parentUserLink}</span>` : ''}
                    
                    <p class="conteudo-comentario">${data.comentario}</p>
                </p>
                <p class="data-do-comentario">${data.data_comentario}</p>
                
                <div class="dropdown-container-comentario ">
                    <div class="dropdown">
                        <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <i class='bx bx-dots-vertical'></i>
                        </button>
                        <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                            <form action="/apagar_comentario/${data.comentario_id}" method="POST" style="display:inline;">
                                <a href="#" class="dropdown-item" data-comentario-id="${data.comentario_id}" onclick="apagarComentario(event, this)">
                                    <i class='bx bx-trash'></i> Excluir comentário
                                </a>

                            <a href="#" class="dropdown-item btn-compartilhar-comentario" data-post-id="${postId}" data-comentario-id="${data.comentario_id}">
                                <i class='bx bx-share-alt'></i> Compartilhar
                            </a>

                            <a href="/inicio" class="dropdown-item" data-post-id="${postId}" data-comentario-id="${data.comentario_id}">
                                <i class='bx bx-user'></i></i> Meu perfil
                            </a>

                            </form>
                        </div>
                    </div>
                </div>
                
                <br>
                <button class="btn-resposta" onclick="mostrarFormResposta(this)">Responder</button>
               <div class="form-resposta">
                    <form class="form-resposta-comentario" onsubmit="submitReply(event, '${postId}', '${data.comentario_id}')">
                        <textarea name="comentario" placeholder="Digite sua resposta..." maxlength="300" required rows="1" style="resize: vertical; overflow:auto;"></textarea>
                        <button type="submit"><i class='bx bx-send'></i></button>
                        <button type="button" class="btn-cancelar-resposta" onclick="esconderFormResposta(this)">
                            <i class='bx bx-x'></i>
                        </button>
                    </form>
                </div>
            </div>
            `;

            let insertedReply;
            if (parentComment.nextElementSibling && parentComment.nextElementSibling.classList.contains('resposta-comentario')) {
                let lastReply = parentComment;
                while (lastReply.nextElementSibling && lastReply.nextElementSibling.classList.contains('resposta-comentario')) {
                    lastReply = lastReply.nextElementSibling;
                }
                lastReply.insertAdjacentHTML('afterend', newReply);
                insertedReply = lastReply.nextElementSibling;
            } else {
                parentComment.insertAdjacentHTML('afterend', newReply);
                insertedReply = parentComment.nextElementSibling;
            }

            // ATIVA AUTOCOMPLETE DE MENÇÃO NO NOVO INPUT DA RESPOSTA
            if (insertedReply) {
                const textarea = insertedReply.querySelector('textarea[name="comentario"]');
                if (textarea) setupMentionInput(textarea);
            }

            // Atualiza o botão de toggle de respostas
            const toggleButton = parentComment.querySelector('.btn-toggle-respostas');
            if (toggleButton) {
                // Verifica se as respostas estão visíveis atualmente
                const respostasVisiveis = !document.querySelector(`.resposta-comentario[data-post-id="${postId}"]`).classList.contains('respostas-ocultas');
                
                // Conta todas as respostas novamente
                const todasRespostas = document.querySelectorAll(`.resposta-comentario[data-post-id="${postId}"]`);
                const respostas = Array.from(todasRespostas).filter(resposta => {
                    if (resposta.previousElementSibling === parentComment) return true;
                    
                    let prev = resposta.previousElementSibling;
                    while (prev && prev.classList.contains('resposta-comentario')) {
                        if (prev.previousElementSibling === parentComment) return true;
                        prev = prev.previousElementSibling;
                    }
                    return false;
                });
                
                // Atualiza o botão mantendo o estado atual
                const icon = respostasVisiveis ? 'bx-chevron-up' : 'bx-chevron-down';
                const text = respostasVisiveis ? 'Ocultar' : 'Mostrar';
                toggleButton.innerHTML = `<i class='bx ${icon}'></i> ${text} respostas (${respostas.length})`;
            }

            // Atualiza o contador de comentários
            const comentariosCountElement = document.querySelector(`#comment-count-${postId}`);
            if (comentariosCountElement) {
                comentariosCountElement.textContent = data.comentarios_count;
            }
        } else {
            console.error('Erro ao enviar resposta:', data.error);
        }
    })
    .catch(error => console.error('Erro na requisição AJAX:', error));
}

// ENVIA COMENTÁRIO PRINCIPAL
function submitComment(event, postId) {
    event.preventDefault();

    const form = document.getElementById(`commentForm-${postId}`);
    const comentario = document.getElementById(`comentario-${postId}`).value;

    fetch(form.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'comentario': comentario
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`comentario-${postId}`).value = '';

            const comentariosDiv = document.querySelector(`#commentModal-${postId} .comentarios`);
            const mensagemSemComentario = comentariosDiv.querySelector('.texto-sem-comentario');
            if (mensagemSemComentario) {
                mensagemSemComentario.remove();
            }

            const fotoPerfil = data.fotos_perfil ? data.fotos_perfil : '../static/img/icone/user.png';

            const newComment = `
            <div class="comentario" data-comentario-id="${data.comentario_id}" data-post-id="${postId}">
                <p>
                    <a href="/inicio">
                        <img src="${fotoPerfil}" style="border-radius:50%;" alt="${data.username}'s foto" class="foto-perfil-comentario">
                        <strong>${data.username}</strong>
                    </a>:
                    <p class="conteudo-comentario">${data.comentario}</p>
                </p>
                <p class="data-do-comentario">${data.data_comentario}</p>
                
                <div class="dropdown-container-comentario ">
                    <div class="dropdown">
                        <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <i class='bx bx-dots-vertical'></i>
                        </button>
                        <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                            <form action="/apagar_comentario/${data.comentario_id}" method="POST" style="display:inline;">
                                <a href="#" class="dropdown-item" data-comentario-id="${data.comentario_id}" onclick="apagarComentario(event, this)">
                                    <i class='bx bx-trash'></i> Excluir comentário
                                </a>
                            </form>

                            <a href="#" class="dropdown-item btn-compartilhar-comentario" data-post-id="${postId}" data-comentario-id="${data.comentario_id}">
                                <i class='bx bx-share-alt'></i> Compartilhar
                            </a>

                            <a href="/inicio" class="dropdown-item" data-post-id="${postId}" data-comentario-id="${data.comentario_id}">
                                <i class='bx bx-user'></i></i> Meu perfil
                            </a>
    
                        </div>
                    </div>
                </div>
                
                <br>
                
                <button class="btn-resposta" onclick="mostrarFormResposta(this)">Responder</button>
                <div class="form-resposta">
                    <form class="form-resposta-comentario" onsubmit="submitReply(event, '${postId}', '${data.comentario_id}')">
                        <textarea name="comentario" placeholder="Digite sua resposta..." maxlength="300" required rows="1" style="resize: vertical; overflow:auto;"></textarea>
                        <button type="submit"><i class='bx bx-send'></i></button>
                        <button type="button" class="btn-cancelar-resposta" onclick="esconderFormResposta(this)">
                            <i class='bx bx-x'></i>
                        </button>
                    </form>
                </div>
            </div>
            `;
            comentariosDiv.insertAdjacentHTML('afterbegin', newComment);

            // ATIVA AUTOCOMPLETE DE MENÇÃO NO NOVO INPUT DO COMENTÁRIO
            const insertedComment = comentariosDiv.querySelector('.comentario');
            if (insertedComment) {
              const textarea = insertedComment.querySelector('textarea[name="comentario"]');
                if (textarea) setupMentionInput(textarea);
            }

            const comentariosCountElement = document.querySelector(`#comment-count-${postId}`);
            if (comentariosCountElement) {
                comentariosCountElement.textContent = data.comentarios_count;
            }
        }
    })
    .catch(error => console.error('Erro na requisição AJAX:', error));
}