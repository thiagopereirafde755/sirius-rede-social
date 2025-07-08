// Função para abrir o modal e carregar os usuários
function abrirEnviarAoChatModal(postId) {
    $('#enviarAoChatModal').modal('show');
    carregarUsuariosMutuos(postId);
}

// Função para carregar os usuários mútuos via AJAX
function carregarUsuariosMutuos(postId) {
    $.ajax({
        url: '/get_usuarios_mutuos',
        type: 'GET',
        data: { post_id: postId },
        success: function(response) {
            if (response.success) {
                let html = '';
                response.usuarios.forEach(usuario => {
                    html += `
                        <div class="usuario-chat-item" onclick="enviarPostParaChat(${postId}, ${usuario.id})">
                            <img src="${usuario.foto_perfil || '/static/img/icone/user.png'}" alt="${usuario.username}">
                            <div class="usuario-chat-info">
                                <div class="usuario-chat-nome">${usuario.username}</div>
                            </div>
                        </div>
                    `;
                });
                
                if (html === '') {
                    html = '<p>Nenhum amigo encontrado.</p>';
                }
                
                $('#listaUsuariosChat').html(html);
            } else {
                $('#listaUsuariosChat').html('<p>Erro ao carregar usuários.</p>');
            }
        },
        error: function() {
            $('#listaUsuariosChat').html('<p>Erro ao carregar usuários.</p>');
        }
    });
}

// Função para filtrar usuários na pesquisa
function filtrarUsuariosChat() {
    const input = document.getElementById('pesquisaUsuarioChat');
    const filter = input.value.toUpperCase();
    const items = document.querySelectorAll('.usuario-chat-item');
    
    items.forEach(item => {
        const nome = item.querySelector('.usuario-chat-nome').textContent.toUpperCase();
        if (nome.includes(filter)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Função para enviar o post para o chat
function enviarPostParaChat(postId, usuarioId) {
    // Alerta visual de envio (SweetAlert2)
    Swal.fire({
        icon: 'info',
        title: 'Enviando...',
        text: `Enviando post ${postId} para o usuário ${usuarioId}`,
        showConfirmButton: false,
        allowOutsideClick: false,
        timer: 1000
    });

    $('#enviarAoChatModal').modal('hide');
    
    // Aqui você pode fazer uma chamada AJAX para enviar o post para o chat
    $.ajax({
        url: '/enviar_post_para_chat',
        type: 'POST',
        data: {
            post_id: postId,
            usuario_id: usuarioId
        },
        success: function(response) {
            if (response.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso!',
                    text: 'Post enviado com sucesso!',
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'Erro ao enviar post: ' + response.message
                });
            }
        },
        error: function() {
            Swal.fire({
                icon: 'error',
                title: 'Erro',
                text: 'Erro na comunicação com o servidor'
            });
        }
    });
}