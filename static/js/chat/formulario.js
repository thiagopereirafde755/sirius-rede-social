document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form-enviar-mensagem');
    if (!form) return;

    const messageInput = document.getElementById('mensagem');
    const photoInput = document.getElementById('foto');
    const videoInput = document.getElementById('video');
    const sendButton = document.getElementById('send-button');
    const previewContainer = document.getElementById('preview-container');

function hasContentToSend() {
    return (
        (messageInput && messageInput.value.trim() !== '') ||  
        (photoInput && photoInput.files.length > 0) ||        
        (videoInput && videoInput.files.length > 0) ||       
        (previewContainer && previewContainer.querySelector('.preview-item') !== null)  
    );
}
    function updateSendButton() {
        sendButton.style.display = hasContentToSend() ? 'flex' : 'none';
    }

    messageInput.addEventListener('input', updateSendButton);
    photoInput.addEventListener('change', updateSendButton);
    videoInput.addEventListener('change', updateSendButton);

    const observer = new MutationObserver(updateSendButton);
    observer.observe(previewContainer, {
        childList: true,
        subtree: true
    });

    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });

    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && hasContentToSend()) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (form.dataset.isSubmitting === 'true') return;
        form.dataset.isSubmitting = 'true';

  const hasPhoto = photoInput.files.length > 0;
const hasVideo = videoInput.files.length > 0;

if (hasPhoto || hasVideo) {
    Swal.fire({
        title: 'Enviando mídia...',
        text: 'Aguarde enquanto sua midia é enviado',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            Swal.close();
            if (data.success) {
                messageInput.value = '';
                photoInput.value = '';
                videoInput.value = '';
                previewContainer.innerHTML = '';
                messageInput.style.height = 'auto';
                
                updateSendButton();

                if (typeof window.cancelReply === 'function') {
                    window.cancelReply();
                }
                
                if (typeof window.atualizarMensagens === 'function') {
                    window.atualizarMensagens(true, true);
                }
            }
        })
        .finally(() => {
            form.dataset.isSubmitting = 'false';
        });
    });

    updateSendButton();
});