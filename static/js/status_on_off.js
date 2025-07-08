// 1. Mantém o status online com ping 
setInterval(function() {
    fetch('/api/ping_online', {method: 'POST', credentials: 'same-origin'});
}, 1000);

// 2. Ao fechar a aba, marca como offline
window.addEventListener('beforeunload', function () {
    navigator.sendBeacon('/api/set_offline');
});

// 3. Atualiza o status do destinatário em tempo real
function checarStatusDestinatario() {
    // destinatarioId deve ser definida globalmente no HTML!
    if (typeof destinatarioId === 'undefined' || !destinatarioId) return;
    fetch(`/api/status_usuario/${destinatarioId}`)
        .then(response => response.json())
        .then(data => {
            const statusSpan = document.getElementById('status-online-offline');
            if (statusSpan) {
                if (data.online) {
                    statusSpan.innerHTML = "<span style='color: green; font-size: 0.8em; margin-left: 10px;'>●</span>";
                } else {
                    statusSpan.innerHTML = "<span style='color: rgb(228, 225, 225); font-size: 0.8em; margin-left: 10px;'>●</span>";
                }
            }
        });
}
setInterval(checarStatusDestinatario, 500); 
checarStatusDestinatario();