function apagarComentario(event, botao) {
    event.preventDefault();

    Swal.fire({
        title: 'Tem certeza?',
        text: 'Deseja apagar este comentário?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, apagar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (!result.isConfirmed) return;
function apagarComentario(event, botao) {
    event.preventDefault();
    Swal.fire({
        title: 'Tem certeza?',
        text: 'Deseja apagar este comentário?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, apagar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (!result.isConfirmed) return;

        const comentarioId = botao.getAttribute('data-comentario-id');
        const comentarioElement = botao.closest('.comentario');
        const postId = comentarioElement.getAttribute('data-post-id');
        const comentariosDiv = document.querySelector(`#commentModal-${postId} .comentarios`);

        const scrollAntes = comentariosDiv.scrollTop;

        setTimeout(() => {
            comentarioElement.remove();

            if (comentariosDiv.querySelectorAll('.comentario').length === 0) {
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

            comentariosDiv.scrollTop = scrollAntes;

            Swal.fire({
                icon: 'success',
                title: 'Comentário apagado!',
                text: 'O comentário foi removido com sucesso.'
            });

        }, 500); 
    });
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
            if (!response.ok) throw new Error('Erro na resposta do servidor');
            return response.json();
        })
        .then(data => {
            if (!data.success) throw new Error(data.message || 'Erro ao apagar o comentário');

            // Recarrega os comentários do modal após apagar
            recarregarComentarios(postId);

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

// Função auxiliar reutilizável para recarregar os comentários
function recarregarComentarios(postId) {
    const btn = document.querySelector(`#commentModal-${postId} .btn-recarregar-comentarios`);
    if (btn) btn.disabled = true;

    fetch(window.location.href, { cache: "reload" })
        .then(response => response.text())
        .then(html => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            const novaDivComentarios = tempDiv.querySelector(`#commentModal-${postId} .comentarios`);
            const atualDivComentarios = document.querySelector(`#commentModal-${postId} .comentarios`);
            if (novaDivComentarios && atualDivComentarios) {
                atualDivComentarios.innerHTML = novaDivComentarios.innerHTML;
                inicializarContadores();
                atualDivComentarios.querySelectorAll('textarea[name="comentario"]').forEach(setupMentionInput);
            }

            const novaCommentInput = tempDiv.querySelector(`#commentModal-${postId} .comment-input`);
            const atualCommentInput = document.querySelector(`#commentModal-${postId} .comment-input`);
            if (novaCommentInput && atualCommentInput) {
                atualCommentInput.innerHTML = novaCommentInput.innerHTML;
                atualCommentInput.querySelectorAll('textarea[name="comentario"]').forEach(setupMentionInput);
            }

            atualizarContadorComentarios(postId);
        })
        .finally(() => {
            if (btn) btn.disabled = false;
        })
        .catch(() => {
            alert('Erro ao recarregar comentários!');
            if (btn) btn.disabled = false;
        });
}
