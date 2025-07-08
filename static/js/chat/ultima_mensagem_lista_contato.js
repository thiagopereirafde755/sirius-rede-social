function atualizarUltimasMsgs() {
    fetch('/api/ultimas_msgs')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                data.contatos.forEach(function(contato) {
                    let item = document.querySelector('.contact-item a[href$="/' + contato.contato_id + '"]').parentElement;
                    if (!item) return;
                    // Remove bloco antigo, se existir
                    let lastMsgDiv = item.querySelector('.last-message-info');
                    if (lastMsgDiv) lastMsgDiv.remove();
                    // Monta novo bloco
                    let div = document.createElement('div');
                    div.className = 'last-message-info';

                    if (contato.ultima_midia) {
                        if (/\.(png|jpg|jpeg|gif)$/i.test(contato.ultima_midia)) {
                            div.innerHTML += '<i class="fa fa-image" title="Foto"></i><span class="last-msg-text">Foto</span>';
                        } else if (/\.(mp4|mov|avi)$/i.test(contato.ultima_midia)) {
                            div.innerHTML += '<i class="fa fa-video" title="Vídeo"></i><span class="last-msg-text">Vídeo</span>';
                        }
                    } else if (contato.ultima_mensagem) {
                        div.innerHTML += '<span class="last-msg-text">' + contato.ultima_mensagem + '</span>';
                    }
                    if (contato.ultima_hora) {
                        div.innerHTML += '<span class="last-msg-time">' + contato.ultima_hora + '</span>';
                    }
                    item.querySelector('a').appendChild(div);
                });
            }
        });
}

// Atualiza a cada 5 segundos (ajuste conforme desejar)
setInterval(atualizarUltimasMsgs, 2000);
window.addEventListener('DOMContentLoaded', atualizarUltimasMsgs);
