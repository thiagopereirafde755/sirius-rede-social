   function atualizarStatusVisto() {
    const destinatarioId = window.destinatarioId || document.querySelector('input[name="destinatario_id"]')?.value;
    if (!destinatarioId) return;
    fetch(`/api/status_visto/${destinatarioId}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;
            const status = data.status;
            for (const [msgId, visto] of Object.entries(status)) {
                // Procura a div da mensagem enviada pelo usuário logado
                const msgDiv = document.querySelector(`.message.sent[data-message-id="${msgId}"]`);
                if (msgDiv) {
                    const ts = msgDiv.querySelector('.timestamp-status');
                    if (ts) {
                        // Atualiza o ícone de acordo com o status
                        if (visto) {
                            ts.querySelector('.status-nao-visto')?.classList.remove('status-nao-visto');
                            ts.querySelector('.bx-check')?.classList.replace('bx-check', 'bx-check-double');
                            ts.querySelector('.bx-check-double')?.classList.add('status-visto');
                        } else {
                            ts.querySelector('.status-visto')?.classList.remove('status-visto');
                            ts.querySelector('.bx-check-double')?.classList.replace('bx-check-double', 'bx-check');
                            ts.querySelector('.bx-check')?.classList.add('status-nao-visto');
                        }
                    }
                }
            }
        });
}

// Dispara a cada 5 segundos
setInterval(atualizarStatusVisto, 5000);
document.addEventListener('DOMContentLoaded', atualizarStatusVisto);