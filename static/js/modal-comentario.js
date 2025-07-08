function openCommentModal(postId) {
    $('#commentModal-' + postId).show();
    // Bloquear a rolagem da página
    $('body').css('overflow', 'hidden');

    // Adicionar um evento para fechar o modal se clicar fora
    $('#commentModal-' + postId).on('click', function(event) {
        // Se o clique não for dentro do modal-content, fecha o modal
        if (!$(event.target).closest('.modal-content-coment').length) {
            closeCommentModal(postId);
        }
    });
}

function closeCommentModal(postId) {
    $('#commentModal-' + postId).hide();
    // Restaurar a rolagem da página
    $('body').css('overflow', 'auto');
    
    // Remover o evento de clique
    $('#commentModal-' + postId).off('click');
    
    // Verificar se a rolagem não está bloqueada por outros estilos
    setTimeout(function() {
        $('body').css('overflow', 'auto');  // Forçar após o modal ser fechado
    }, 100);
}
