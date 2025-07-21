let notificacoesExibidas = JSON.parse(localStorage.getItem('notificacoesExibidas') || '[]');

let idsProcessados = new Set();

function montaMensagemNotificacao(item) {
    if (!item) return null;

    let username = item.origem_username || 'Usuário';
    switch (item.tipo) {
        case 'curtida':
            return `${username} curtiu seu post.`;
        case 'republicado':
            return `${username} republicou seu post.`;
        case 'comentario':
            return `${username} comentou no seu post.`;
        case 'resposta':
            return `${username} respondeu seu comentário.`;
        case 'seguidor':
            return `${username} começou a te seguir.`;
        case 'mencao':
            return item.comentario_id
                ? `${username} mencionou você em um comentário.`
                : `${username} mencionou você em um post.`;
        case 'aceite_pedido':
            return `${username} aceitou seu pedido para seguir.`;
        case 'pedido_seguir':
            return `${username} pediu para te seguir.`;
        default:
            return null;
    }
}

function exibirNotificacao(item) {
    if (!item || idsProcessados.has(item.id) || notificacoesExibidas.includes(item.id)) return;

    idsProcessados.add(item.id);
    notificacoesExibidas.push(item.id);
    localStorage.setItem('notificacoesExibidas', JSON.stringify(notificacoesExibidas));

    let mensagem = montaMensagemNotificacao(item);
    if (!mensagem) return;

    let url = '/notificacoes';
    if (item.post_id) {
        url = `/post/${item.post_id}`;
        if (item.comentario_id) url += `?comentario_id=${item.comentario_id}`;
    }

    let icon = item.origem_foto || '/static/img/icone/user.png';

    if (Notification.permission === 'granted' && notificacoesAtivadas) {
        let notification = new Notification('Nova notificação', {
            body: mensagem,
            icon: icon
        });

        notification.onclick = () => window.open(url, '_blank');
    }
}

function checarNovasNotificacoes() {
    fetch('/api/notificacoes_ultimas')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                let novas = Array.isArray(data.notificacao)
                    ? data.notificacao
                    : [data.notificacao];

                novas.forEach(notif => exibirNotificacao(notif));
            }
        });
}

if ('Notification' in window) {
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }

    setInterval(() => {
        idsProcessados.clear(); 
        checarNovasNotificacoes();
    }, 2000);
}
