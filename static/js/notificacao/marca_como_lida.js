 // Marcar notificações como lidas quando a página é carregada
    document.addEventListener('DOMContentLoaded', function() {
        fetch('/api/marcar_como_lidas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                // Atualizar o contador de notificações não lidas
                atualizarContadorNotificacoes();
            }
        });
    });