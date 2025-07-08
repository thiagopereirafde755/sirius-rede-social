// Função para apagar comentário com SweetAlert2
function apagarComentario(botao) {
    // Substituindo o confirm padrão pelo SweetAlert2
    Swal.fire({
        title: 'Tem certeza?',
        text: 'Deseja apagar este comentário e todas as suas respostas?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, apagar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (!result.isConfirmed) {
            return;
        }

        const comentarioId = botao.getAttribute('data-comentario-id');
        const comentarioElement = botao.closest('.comentario');
        const postId = comentarioElement.getAttribute('data-post-id');
        
        fetch(`/apagar_comentario/${comentarioId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.message || 'Erro ao apagar o comentário');
            }

            // Remove o comentário principal e todas as respostas
            const comentarioPrincipal = document.querySelector(`.comentario[data-comentario-id="${comentarioId}"]`);
            if (comentarioPrincipal) {
                // Encontra e remove todas as respostas (elementos com classe 'resposta' que estão depois)
                let nextElement = comentarioPrincipal.nextElementSibling;
                while (nextElement && (nextElement.classList.contains('resposta') || 
                       nextElement.classList.contains('resposta-comentario'))) {
                    const temp = nextElement.nextElementSibling;
                    nextElement.remove();
                    nextElement = temp;
                }
                
                // Remove o comentário principal
                comentarioPrincipal.remove();
            }

            // Atualiza a contagem de comentários em todos os lugares necessários
            const comentariosCountElements = document.querySelectorAll(`.comment-count[data-post-id="${data.post_id}"], #comment-count-${data.post_id}`);
            comentariosCountElements.forEach(element => {
                element.textContent = data.comentarios_count;
            });

            // Mostra mensagem se não houver mais comentários
            const comentariosDiv = document.querySelector(`#commentModal-${data.post_id} .comentarios`);
            if (comentariosDiv && comentariosDiv.querySelectorAll('.comentario').length === 0) {
                const noCommentsContainer = document.createElement('div');
                noCommentsContainer.className = 'texto-sem-comentario';
                const iconElement = document.createElement('i');
                iconElement.className = 'bx bxs-comment-dots';
                const textElement = document.createElement('p');
                textElement.textContent = 'Nenhum comentário ainda. Seja o primeiro a comentar!';
                noCommentsContainer.appendChild(iconElement);
                noCommentsContainer.appendChild(textElement);
                comentariosDiv.appendChild(noCommentsContainer);
            }

            Swal.fire({
                icon: 'success',
                title: 'Comentário apagado!',
                text: data.message
            });
        })
        .catch(error => {
            console.error('Erro:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro',
                text: error.message
            });
        });
    });
}