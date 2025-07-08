// VARIAVEIS
let lastMessageCount = 0;
let isAtBottom = true;
let backToBottomBtn = null;

// FUNÇÃO PARA DEIXAR URL CLICAVEL NAS MENSAGENS
function linkify(text) {
    if (!text) return text;
    const urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    return text.replace(urlRegex, function(url) {
        const maxLength = 30;
        let displayText;
        if (url.length > maxLength) {
            displayText = url.substring(0, maxLength) + '...';
        } else {
            displayText = url;
        }
        try {
            new URL(url);
        } catch (e) {
            displayText = url.match(/:\/\/(.[^/]+)/)?.[1] || url;
        }
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="message-link">${displayText}</a>`;
    });
}

// FUNÇÃO PARA PROCESSAR LINKS
function processMessageLinks() {
    const messageContents = document.querySelectorAll('.message .content');
    messageContents.forEach(content => {
        if (!content.querySelector('a')) {
            content.innerHTML = linkify(content.textContent);
        }
    });
}

// FUNÇÃO PARA TER MODAL NAS FOTOS DAS MENSAGENS
function initImageModals() {
    const images = document.querySelectorAll('.mensagem-midia');
    images.forEach(img => {
        if (img.tagName.toLowerCase() === 'img') {
            img.addEventListener('click', function() {
                openImageModal(this.src, this.alt);
            });
        }
    });
}

// FUNÇÃO PARA ABRIR O MODAL DE FOTO
function openImageModal(src, alt) {
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    const captionText = document.getElementById('modal-caption');
    modal.style.display = "block";
    modalImg.src = src;
    captionText.innerHTML = alt || "Imagem da mensagem";
    document.querySelector('.close-modal').onclick = function() {
        modal.style.display = "none";
    };
    modal.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
    document.addEventListener('keydown', function eventListener(event) {
        if (event.key === "Escape") {
            modal.style.display = "none";
            document.removeEventListener('keydown', eventListener);
        }
    });
}

// FUNÇÃO PARA VERIFICA SE O USUARIO ESTA PERTO DO FINAL DO CHAT
function isNearBottom(container, threshold = 100) {
    if (!container) return true;
    const scrollPosition = container.scrollTop + container.clientHeight;
    return scrollPosition >= container.scrollHeight - threshold;
}

// FUNÇÃO PARA CRIAR CARROSSEL DE MÍDIA PARA POST
function createMediaCarousel(images, videos) {
    if (images.length === 0 && videos.length === 0) return '';
    let carouselId = 'carousel_' + Math.random().toString(36).substr(2, 9);
    let slides = '';
    let indicators = '';
    let slideIdx = 0;
    images.forEach((img, idx) => {
        slides += `
            <div class="carousel-slide${idx === 0 ? ' active' : ''}">
                <img src="${img}" class="post-image">
            </div>
        `;
        indicators += `<span class="carousel-dot${idx === 0 ? ' active' : ''}" data-idx="${slideIdx}"></span>`;
        slideIdx++;
    });
    videos.forEach((vid, idx) => {
        slides += `
            <div class="carousel-slide${images.length === 0 && idx === 0 ? ' active' : ''}">
                <video controls class="post-video">
                    <source src="${vid}" type="video/mp4">
                </video>
            </div>
        `;
        indicators += `<span class="carousel-dot${(images.length === 0 && idx === 0) ? ' active' : ''}" data-idx="${slideIdx}"></span>`;
        slideIdx++;
    });
    setTimeout(() => {
        const carousel = document.getElementById(carouselId);
        if (!carousel) return;
        let slides = carousel.querySelectorAll('.carousel-slide');
        let dots = carousel.querySelectorAll('.carousel-dot');
        let current = 0;
        function showSlide(idx) {
            slides.forEach((s, i) => {
                s.classList.toggle('active', i === idx);
            });
            dots.forEach((d, i) => {
                d.classList.toggle('active', i === idx);
            });
            current = idx;
        }
        carousel.querySelector('.carousel-prev').onclick = () => {
            let next = (current - 1 + slides.length) % slides.length;
            showSlide(next);
        };
        carousel.querySelector('.carousel-next').onclick = () => {
            let next = (current + 1) % slides.length;
            showSlide(next);
        };
        dots.forEach((d, i) => {
            d.onclick = () => showSlide(i);
        });
    }, 0);
    return `
        <div class="carousel" id="${carouselId}">
            <div class="carousel-slides">
                ${slides}
            </div>
            <div class="carousel-controls">
                <span class="carousel-prev">&#10094;</span>
                <span class="carousel-next">&#10095;</span>
            </div>
            <div class="carousel-indicators">
                ${indicators}
            </div>
        </div>
    `;
}

// FUNÇÃO PARA ATUALIZAR AS MENSAGENS
function atualizarMensagens(forceScroll = false, isUserMessage = false) {
    if (window.isVideoPlaying || window.isUserScrollingUp) return;
    const destinatarioId = document.querySelector('input[name="destinatario_id"]')?.value;
    if (!destinatarioId) return;
    const mensagensContainer = document.getElementById('mensagens-container');
    if (!mensagensContainer) return;
    const wasNearBottom = isNearBottom(mensagensContainer, 400);
    const scrollPositionBeforeUpdate = mensagensContainer.scrollTop;
    const scrollHeightBeforeUpdate = mensagensContainer.scrollHeight;
    fetch(`/atualizar_mensagens/${destinatarioId}`)
        .then(response => {
            if (!response.ok) throw new Error('Erro na requisição');
            return response.json();
        })
        .then(data => {
            if (data.success && data.mensagens.length > 0) {
                if (data.mensagens.length === lastMessageCount && !forceScroll) return;
                mensagensContainer.innerHTML = '';
                let ultimaData = '';
                setTimeout(processMessageLinks, 0);
                setTimeout(initImageModals, 0);
                data.mensagens.forEach(mensagem => {
                    if (mensagem.data_dia !== ultimaData) {
                        const dataDiv = document.createElement('div');
                        dataDiv.classList.add('mensagem-data');
                        dataDiv.textContent = mensagem.data_dia;
                        mensagensContainer.appendChild(dataDiv);
                        ultimaData = mensagem.data_dia;
                    }
                    const novaMensagem = document.createElement('div');
                    novaMensagem.classList.add('message', mensagem.id_remetente == window.usuarioId ? 'sent' : 'received');
                    novaMensagem.setAttribute('data-message-id', mensagem.id);
                    let conteudoMensagem = `
                        <div class="message-header">
                            <div class="username">${mensagem.username}</div>
                            <div class="message-options">
                                <button class="options-btn" onclick="toggleDropdown(this)">&#x22EE;</button>
                                <div class="dropdown-menu">
                                    <button class="reply-btn" data-message-id="${mensagem.id}"> <i class='bx bx-reply'></i> Responder</button>`;
                    if (mensagem.id_remetente == window.usuarioId) {
                        conteudoMensagem += `<button class="delete-message" data-message-id="${mensagem.id}"> <i class='bx bx-trash'></i> Apagar</button>`;
                    }
                    conteudoMensagem += `</div></div></div>`;
                    // BLOCO DE MENSAGEM DE POST
                    if (mensagem.post_id) {
                        if (mensagem.post_disponivel) {
                            conteudoMensagem += `
                                <div class="shared-post">
                                    <div class="shared-post-content">
                                        <div class="post-author">Post de ${mensagem.post_autor_username || 'usuário'}</div>`;
                            let images = [];
                            let videos = [];
                            if (mensagem.post_imagem) images.push(`../static/${mensagem.post_imagem}`);
                            if (mensagem.post_video) videos.push(`../static/${mensagem.post_video}`);
                            if (mensagem.post_conteudo) {
                                conteudoMensagem += `<div class="post-text">${mensagem.post_conteudo}</div>`;
                            }
                            if (images.length + videos.length > 1) {
                                conteudoMensagem += createMediaCarousel(images, videos);
                            } else {
                                if (images.length === 1) {
                                    conteudoMensagem += `<a href="/post/${mensagem.post_id}" target="_blank"><img src="${images[0]}" class="post-image"></a>`;
                                }
                                if (videos.length === 1) {
                                    conteudoMensagem += `
                                        <a href="/post/${mensagem.post_id}" target="_blank">
                                        <video controls class="post-video">
                                            <source src="${videos[0]}" type="video/mp4">
                                        </video>
                                        </a>`;
                                }
                            }
                            conteudoMensagem += `
                                <div style="text-align:center;margin-top:8px;">
                                    <a href="/post/${mensagem.post_id}" target="_blank" class="ver-post-btn" style="display:inline-block;padding:2px 18px 2px 10px;font-size:15px;border-radius:18px;background:#222;color:#fff;text-decoration:none;">
                                        <i class="fa fa-external-link-alt"></i> Ver post
                                    </a>
                                </div>
                            </div></div>`;
                        } else {
                            conteudoMensagem += `
                                <div class="shared-post unavailable">
                                    <div class="shared-post-content">
                                        <div class="post-unavailable">
                                            <i class='bx bxs-lock'></i>
                                            <span>Post indisponível</span>
                                        </div>
                                    </div>
                                </div>`;
                        }
                    }
                    // BLOCO DE MENSAGEM RESPONDIDA
                    if (mensagem.id_mensagem_respondida) {
                        let quotedContent = '<div class="quoted-content">';
                        if (mensagem.username_respondido) {
                            quotedContent += `<div class="quoted-username">${mensagem.username_respondido}</div>`;
                        }
                        if (mensagem.midia_respondida) {
                            const extensao = mensagem.midia_respondida.split('.').pop().toLowerCase();
                            if (['png', 'jpg', 'jpeg', 'gif'].includes(extensao)) {
                                quotedContent += `<img src="../static/${mensagem.midia_respondida}" class="quoted-photo">`;
                            } else if (['mp4', 'mov', 'avi'].includes(extensao)) {
                                quotedContent += `
                                    <video controls class="quoted-video">
                                        <source src="../static/${mensagem.midia_respondida}" type="video/mp4">
                                        Seu navegador não suporta o vídeo.
                                    </video>
                                `;
                            }
                        }
                        if (mensagem.mensagem_respondida) {
                            quotedContent += `<div class="quoted-text">${mensagem.mensagem_respondida}</div>`;
                        }
                        quotedContent += '</div>';
                        conteudoMensagem += `
                            <div class="quoted-message" data-quoted-id="${mensagem.id_mensagem_respondida}" onclick="scrollToQuotedMessage(this)">
                                ${quotedContent}
                            </div>
                        `;
                    }
                    // BLOCO DE FOTO E VIDEO
                    if (mensagem.caminho_arquivo) {
                        const extensao = mensagem.caminho_arquivo.split('.').pop().toLowerCase();
                        if (['png', 'jpg', 'jpeg', 'gif'].includes(extensao)) {
                            conteudoMensagem += `
                                <div class="media">
                                    <img src="../static/${mensagem.caminho_arquivo}" 
                                         class="mensagem-midia" 
                                         alt="Imagem enviada por ${mensagem.username}">
                                </div>`;
                        } else if (['mp4', 'mov', 'avi'].includes(extensao)) {
                            conteudoMensagem += `<div class="media"><video src="../static/${mensagem.caminho_arquivo}" controls class="mensagem-midia"></video></div>`;
                        }
                    }
                    // BLOCO DE CONTEUDO DA MENSAGEM
                    if (mensagem.mensagem) {
                        conteudoMensagem += `<div class="content">${mensagem.mensagem}</div>`;
                    }
                    // HORA E VISTO DA MENSAGEM
                    let timestampContent = `<div class="timestamp-status">`;
                    timestampContent += `<span class="timestamp-text">${mensagem.data_envio}</span>`;
                    if (mensagem.id_remetente == window.usuarioId) {
                        if (mensagem.data_visualizacao) {
                            timestampContent += `<span class="status-visto" title="Visualizada"><i class='bx bx-check-double'></i></span>`;
                        } else {
                            timestampContent += `<span class="status-nao-visto" title="Entregue"><i class='bx bx-check' ></i></span>`;
                        }
                    }
                    timestampContent += `</div>`;
                    conteudoMensagem += timestampContent;
                    novaMensagem.innerHTML = conteudoMensagem;
                    mensagensContainer.appendChild(novaMensagem);
                });
                if (forceScroll || isUserMessage) {
                    setTimeout(() => scrollToBottom(), 50);
                } else if (wasNearBottom) {
                    setTimeout(() => scrollToBottom(), 50);
                } else {
                    const lastMessage = data.mensagens[data.mensagens.length - 1];
                    const isFromCurrentUser = lastMessage.id_remetente == window.usuarioId;
                    if (isFromCurrentUser) {
                        setTimeout(() => scrollToBottom(), 50);
                    } else {
                        showNewMessagesButton();
                    }
                    const newScrollHeight = mensagensContainer.scrollHeight;
                    const heightDifference = newScrollHeight - scrollHeightBeforeUpdate;
                    mensagensContainer.scrollTop = scrollPositionBeforeUpdate + heightDifference;
                }
                lastMessageCount = data.mensagens.length;
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar mensagens:', error);
        });
}

// FUNÇÃO PARA VERIFICAR POSIÇÃO DO USUARIO NO CHAT
function setupScrollPositionChecker() {
    backToBottomBtn = document.getElementById('back-to-bottom-btn');
    const mensagensContainer = document.getElementById('mensagens-container');
    if (!mensagensContainer || !backToBottomBtn) return;
    mensagensContainer.addEventListener('scroll', () => {
        const isReplying = document.querySelector('.replying-indicator') !== null;
        isAtBottom = isNearBottom(mensagensContainer, 200);
        if (isAtBottom || isReplying) {
            backToBottomBtn.classList.remove('visible');
            backToBottomBtn.classList.add('hidden');
        } else {
            backToBottomBtn.classList.remove('hidden');
            backToBottomBtn.classList.add('visible');
            if (isReplying) {
                backToBottomBtn.classList.add('disabled');
            } else {
                backToBottomBtn.classList.remove('disabled');
            }
        }
    });
    backToBottomBtn.addEventListener('click', () => {
        if (!backToBottomBtn.classList.contains('disabled')) {
            scrollToBottom();
        }
    });
}

//CHAME A FUNÇÃO DEPOIS DE O DOM ESTAR CARREGADO
document.addEventListener('DOMContentLoaded', () => {
    initImageModals();
    processMessageLinks();
    setupScrollPositionChecker();
});