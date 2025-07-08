document.addEventListener('DOMContentLoaded', function () {
    const textarea = document.getElementById('mensagem');
    const charCount = document.getElementById('char-count');
    const sendButton = document.getElementById('send-button');
    const maxLength = 300;
    const form = document.getElementById('form-enviar-mensagem');

    function updateCharCount() {
        const len = textarea.value.length;
        charCount.textContent = `${len}/${maxLength}`;
        charCount.style.color = (len >= maxLength) ? 'red' : '';
        
        // Modificação principal: Remove a verificação "len === 0" para permitir envio sem texto
        sendButton.disabled = len > maxLength; // Apenas desabilita se exceder o limite
        
        if (len > maxLength) {
            textarea.value = textarea.value.substring(0, maxLength);
        }
    }

    textarea.addEventListener('input', updateCharCount);
    updateCharCount();

    form.addEventListener('submit', function (e) {
        setTimeout(function () {
            textarea.value = '';
            updateCharCount();
        }, 1000);
    });
});