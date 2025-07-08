document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form-enviar-mensagem');
    if (!form) return;

    const messageInput = document.getElementById('mensagem');
    const photoInput = document.getElementById('foto');
    const videoInput = document.getElementById('video');
    const sendButton = document.getElementById('send-button');
    const previewContainer = document.getElementById('preview-container');

    // Função para verificar se há conteúdo para enviar
// formulario.js - Modifique a função hasContentToSend()
function hasContentToSend() {
    return (
        (messageInput && messageInput.value.trim() !== '') ||  // Tem texto
        (photoInput && photoInput.files.length > 0) ||        // Tem foto selecionada
        (videoInput && videoInput.files.length > 0) ||        // Tem vídeo selecionado
        (previewContainer && previewContainer.querySelector('.preview-item') !== null)  // Tem preview visível
    );
}
    // Atualiza a visibilidade do botão de enviar
    function updateSendButton() {
        sendButton.style.display = hasContentToSend() ? 'flex' : 'none';
    }

    // Event listeners para todos os elementos que podem conter conteúdo
    messageInput.addEventListener('input', updateSendButton);
    photoInput.addEventListener('change', updateSendButton);
    videoInput.addEventListener('change', updateSendButton);

    // Observar mudanças no container de preview (para quando mídias são adicionadas/removidas)
    const observer = new MutationObserver(updateSendButton);
    observer.observe(previewContainer, {
        childList: true,
        subtree: true
    });

    // Ajuste automático da altura do textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });

    // Envio com Enter (exceto Shift+Enter)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && hasContentToSend()) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    });

    // Submissão do formulário
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (form.dataset.isSubmitting === 'true') return;
        form.dataset.isSubmitting = 'true';

        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Limpa os campos após envio
                messageInput.value = '';
                photoInput.value = '';
                videoInput.value = '';
                previewContainer.innerHTML = '';
                messageInput.style.height = 'auto';
                
                // Atualiza a interface
                updateSendButton();
                
                // Se houver função para atualizar mensagens
                if (typeof window.atualizarMensagens === 'function') {
                    window.atualizarMensagens(true, true);
                }
            }
        })
        .finally(() => {
            form.dataset.isSubmitting = 'false';
        });
    });

    // Verificação inicial
    updateSendButton();
});