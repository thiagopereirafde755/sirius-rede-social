function abrirEnviarAoChatModal(postId) {
    // limpa busca
    document.getElementById('pesquisaUsuarioChat').value = '';
    $('#msgSemAmigos').hide(); // esconde mensagem
    $('#enviarAoChatModal').modal('show');
    carregarUsuariosMutuos(postId);
}


function filtrarUsuariosChat() {
    const input   = document.getElementById('pesquisaUsuarioChat');
    const filtro  = input.value.toUpperCase();
    const itens   = document.querySelectorAll('.usuario-chat-item');
    const msg     = document.getElementById('msgSemAmigos');

    let algumVisivel = false;

    itens.forEach(item => {
        const nome = item.querySelector('.usuario-chat-nome').textContent.toUpperCase();
        if (nome.includes(filtro)) {
            item.style.display = ''; 
            algumVisivel = true;
        } else {
            item.style.display = 'none'; 
        }
    });

    msg.style.display = algumVisivel ? 'none' : 'block';
}


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
                                <div class="usuario-chat-nome">${usuario.username} </div>
                            </div>
                        </div>
                    `;
                });

                if (response.usuarios.length > 1) {
                    document.getElementById('containerPesquisaUsuarioChat').style.display = 'block';
                } else {
                    document.getElementById('containerPesquisaUsuarioChat').style.display = 'none';
                }

                if (html === '') {
                    html = '<p>Nenhum amigo encontrado.</p>';
                }

                $('#listaUsuariosChat').html(html);
            } else {
                $('#containerPesquisaUsuarioChat').style.display = 'none';
                $('#listaUsuariosChat').html('<p>Erro ao carregar usuários.</p>');
            }
        },
        error: function() {
            document.getElementById('containerPesquisaUsuarioChat').style.display = 'none';
            $('#listaUsuariosChat').html('<p>Erro ao carregar usuários.</p>');
        }
    });
}

// Função para enviar o post para o chat
function enviarPostParaChat(postId, usuarioId) {
    Swal.fire({
        icon: 'info',
        title: 'Enviando...',
        text: `Enviando post ${postId} para o usuário ${usuarioId}`,
        showConfirmButton: false,
        allowOutsideClick: false,
        timer: 1000
    });

    $('#enviarAoChatModal').modal('hide');
    
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