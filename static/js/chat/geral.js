// VARIÁVEIS GLOBAIS COMPARTILHADAS
window.usuarioId = document.currentScript.getAttribute('data-user-id') || "{{ usuario_id }}";
window.isVideoPlaying = false;
window.isUserScrollingUp = false;
window.hasNewMessages = false;

// VARIÁVEIS LOCAIS
let scrollTimeout;
let replyingTo = null;

// MOSTRA O INDICADOR DE RESPOSTA
function showReplyingIndicator(messageId, username, messageContent, mediaType = null) {
    let contentDisplay = messageContent || '[Mídia]';
    if (mediaType) {
        contentDisplay = `[${mediaType === 'image' ? 'Imagem' : 'Vídeo'}]`;
    }

    const replyingIndicator = document.createElement('div');
    replyingIndicator.className = 'replying-indicator';
    replyingIndicator.innerHTML = `
        <div>Respondendo a ${username}: ${contentDisplay}</div>
        <button class="cancel-reply" onclick="cancelReply()">×</button>
    `;
    
    const form = document.getElementById('form-enviar-mensagem');
    const existingIndicator = form.querySelector('.replying-indicator');
    
    if (existingIndicator) {
        form.replaceChild(replyingIndicator, existingIndicator);
    } else {
        form.insertBefore(replyingIndicator, form.querySelector('.input-wrapper'));
    }
    
    // ATUALIZA O CAMPO ESCONDIDO DO FORMULÁRIO
    document.getElementById('id_mensagem_respondida').value = messageId;
    
    replyingTo = {
        id: messageId,
        username: username,
        content: messageContent,
        mediaType: mediaType
    };

    // DESATIVA O BOTÃO "VOLTAR AO FINAL"
    const backToBottomBtn = document.getElementById('back-to-bottom-btn');
    if (backToBottomBtn) {
        backToBottomBtn.classList.add('disabled');
    }
}

// CANCELA A RESPOSTA
function cancelReply() {
    const indicator = document.querySelector('.replying-indicator');
    if (indicator) {
        indicator.remove();
    }
    // LIMPA O CAMPO ESCONDIDO DO FORMULÁRIO
    document.getElementById('id_mensagem_respondida').value = '';
    replyingTo = null;

    // REATIVA O BOTÃO "VOLTAR AO FINAL" SE ESTIVER VISÍVEL
    const backToBottomBtn = document.getElementById('back-to-bottom-btn');
    if (backToBottomBtn && backToBottomBtn.classList.contains('visible')) {
        backToBottomBtn.classList.remove('disabled');
    }
}

// ESCONDE O BOTÃO DE NOVAS MENSAGENS
function hideNewMessagesButton() {
    const newMessagesBtn = document.getElementById('new-messages-btn');
    if (newMessagesBtn) {
        newMessagesBtn.classList.remove('visible');
        newMessagesBtn.classList.add('hidden');
        window.hasNewMessages = false;
    }
}

// MODIFICA A FUNÇÃO scrollToBottom PARA ESCONDER O BOTÃO QUANDO O USUÁRIO ROLAR PARA BAIXO
function scrollToBottom() {
    const mensagensContainer = document.getElementById('mensagens-container');
    const backToBottomBtn = document.getElementById('back-to-bottom-btn');
    
    if (mensagensContainer) {
        setTimeout(() => {
            mensagensContainer.scrollTo({
                top: mensagensContainer.scrollHeight,
                behavior: 'smooth'
            });
            
            // ESCONDE E REATIVA O BOTÃO APÓS ROLAR
            if (backToBottomBtn) {
                backToBottomBtn.classList.remove('visible', 'disabled');
                backToBottomBtn.classList.add('hidden');
            }
            isAtBottom = true;
        }, 100);
    }
}

// MOSTRA O BOTÃO DE NOVAS MENSAGENS
function showNewMessagesButton() {
    const newMessagesBtn = document.getElementById('new-messages-btn');
    if (newMessagesBtn) {
        newMessagesBtn.classList.remove('hidden');
        newMessagesBtn.classList.add('visible');
        window.hasNewMessages = true;
        
        // CONFIGURA O CLIQUE DO BOTÃO
        newMessagesBtn.addEventListener('click', scrollToBottom);
    }
}

// ROLA ATÉ A MENSAGEM CITADA
function scrollToQuotedMessage(element) {
    const quotedId = element.getAttribute('data-quoted-id');
    if (!quotedId) return;
    
    const targetMessage = document.querySelector(`.message[data-message-id="${quotedId}"]`);
    if (targetMessage) {
        targetMessage.classList.add('highlight-message');
        targetMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        setTimeout(() => {
            targetMessage.classList.add('highlight-pulse');
        }, 300);
        
        setTimeout(() => {
            targetMessage.classList.remove('highlight-message', 'highlight-pulse');
        }, 5000);
    } else {
        alert('A mensagem original foi apagada');
    }
}

// FUNÇÕES DE MANIPULAÇÃO DE UI
function toggleDropdown(button) {
    const dropdown = button.nextElementSibling;
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

// LIDA COM O SCROLL
function handleScroll() {
    const mensagensContainer = document.getElementById('mensagens-container');
    const newMessageButton = document.getElementById('new-messages-btn');
    
    if (mensagensContainer) {
        const isNearBottom = mensagensContainer.scrollTop + mensagensContainer.clientHeight >= 
                           mensagensContainer.scrollHeight - 200;
        
        if (!isNearBottom) {
            window.isUserScrollingUp = true;
            
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                window.isUserScrollingUp = false;
                
                // SE HOUVER NOVAS MENSAGENS E O USUÁRIO NÃO ESTIVER PERTO DO FINAL, MOSTRA O BOTÃO
                if (window.hasNewMessages && !isNearBottom) {
                    showNewMessagesButton();
                }
            }, 1500);
        } else if (newMessageButton) {
            newMessageButton.classList.remove('visible');
            window.hasNewMessages = false;
        }
    }
}

// INICIALIZAÇÃO DO CHAT
function initChat() {
    // EVENT LISTENERS
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('reply-btn')) {
            const messageElement = e.target.closest('.message');
            const messageId = messageElement.getAttribute('data-message-id');
            const username = messageElement.querySelector('.username').textContent;
            
            const mediaElement = messageElement.querySelector('.mensagem-midia');
            if (mediaElement) {
                const mediaType = mediaElement.tagName.toLowerCase() === 'img' ? 'image' : 'video';
                showReplyingIndicator(messageId, username, null, mediaType);
            } else {
                const messageContent = messageElement.querySelector('.content')?.textContent || 
                                           messageElement.querySelector('.quoted-text')?.textContent || '';
                showReplyingIndicator(messageId, username, messageContent);
            }
        }
        
        if (e.target && e.target.classList.contains('delete-message')) {
            const mensagemId = e.target.getAttribute('data-message-id');
            deletarMensagem(mensagemId);
        }
    });

    // SCROLL E MÍDIA
    const mensagensContainer = document.getElementById('mensagens-container');
    if (mensagensContainer) {
        mensagensContainer.addEventListener('scroll', handleScroll);

        ['play', 'pause', 'ended'].forEach(event => {
            mensagensContainer.addEventListener(event, function(e) {
                if (e.target.tagName === 'VIDEO') {
                    window.isVideoPlaying = event === 'play';
                }
            }, true);
        });
    }

    // ENVIO DE MENSAGEM (DESABILITADO, AGORA EM formulario.js)
    // const formEnviar = document.getElementById('form-enviar-mensagem');
    // if (formEnviar) {
    //     formEnviar.addEventListener('submit', function(e) {
    //         e.preventDefault();
    //         const formData = new FormData(this);
            
    //         if (replyingTo) {
    //             formData.append('id_mensagem_respondida', replyingTo.id);
    //             formData.append('replying_username', replyingTo.username);
    //             if (replyingTo.mediaType) {
    //                 formData.append('replying_media_type', replyingTo.mediaType);
    //             }
    //         }

    //         fetch(this.action, {
    //             method: 'POST',
    //             body: formData,
    //             headers: {
    //                 'Accept': 'application/json',
    //             },
    //         })
    //         .then(response => response.json())
    //         .then(data => {
    //             if (data.success) {
    //                 this.reset();
    //                 document.getElementById('preview-container').innerHTML = '';
    //                 cancelReply();
    //                 // Call atualizarMensagens with forceScroll and isUserMessage true after sending
    //                 if (typeof atualizarMensagens === 'function') {
    //                     atualizarMensagens(true, true); 
    //                 } else {
    //                     console.error('Função atualizarMensagens não encontrada');
    //                 }
    //             }
    //         })
    //         .catch(error => {
    //             console.error('Erro ao enviar mensagem:', error);
    //         });
    //     });
    // }

    // CHAMADA INICIAL PARA ATUALIZAR AS MENSAGENS E SETAR INTERVALO
    atualizarMensagens(true); // CHAMA UMA VEZ AO CARREGAR PARA POPULAR AS MENSAGENS
    setInterval(atualizarMensagens, 2000); // DEPOIS ATUALIZA PERIODICAMENTE
}

// INICIA O CHAT QUANDO O DOM ESTIVER PRONTO
document.addEventListener('DOMContentLoaded', function() {
    initChat();
});