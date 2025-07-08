// Garante exibição de cada notificação push apenas uma vez por usuário (enquanto não marcar como lida)
let ultimaNotificacaoId = localStorage.getItem('ultimaNotificacaoId') || null;

// Função para montar a mensagem igual ao template do backend
function montaMensagemNotificacao(item) {
    if (!item) return null;
    let username = item.origem_username || 'Usuário';
    let msg = '';
    if (item.tipo === 'curtida') {
        msg = `${username} curtiu seu post.`;
    } else if (item.tipo === 'comentario') {
        msg = `${username} comentou no seu post.`;
    } else if (item.tipo === 'resposta') {
        msg = `${username} respondeu seu comentário.`;
    } else if (item.tipo === 'seguidor') {
        msg = `${username} começou a te seguir.`;
    } else if (item.tipo === 'mencao') {
        msg = item.comentario_id ? `${username} mencionou você em um comentário.` : `${username} mencionou você em um post.`;
    } else if (item.tipo === 'aceite_pedido') {
        msg = `${username} aceitou seu pedido para seguir.`;
    } else if (item.tipo === 'pedido_seguir') {
        msg = `${username} pediu para te seguir.`;
    }
    return msg;
}

// Função para exibir a notificação push
function exibirNotificacao(item) {
    if (!item) return;
    if (String(item.id) === String(ultimaNotificacaoId)) return; // Já exibiu essa notificação

    ultimaNotificacaoId = item.id;
    localStorage.setItem('ultimaNotificacaoId', item.id);

    let mensagem = montaMensagemNotificacao(item);
    let url = '/notificacoes'; // link padrão
    if (item.post_id) {
        url = `/post/${item.post_id}`;
        if (item.comentario_id) url += `?comentario_id=${item.comentario_id}`;
    }
    let icon = item.origem_foto || '/static/img/icone/user.png';

    if (Notification.permission === 'granted') {
        let notification = new Notification('Nova notificação', {
            body: mensagem,
            icon: icon
        });
        notification.onclick = function () {
            window.open(url, '_blank');
        }
    }
}

// Função periódica para buscar novas notificações
function checarNovasNotificacoes() {
    fetch('/api/notificacoes_ultimas')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.notificacao) {
                exibirNotificacao(data.notificacao);
            }
        });
}

if (window.Notification) {
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
    // Checa a cada 2 segundos (ajuste se quiser menos frequente)
    setInterval(checarNovasNotificacoes, 2000);
}