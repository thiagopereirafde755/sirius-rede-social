function atualizarContador() {
    var textarea = document.getElementById('post-textarea');
    var contador = document.getElementById('contador-caracteres');
    contador.textContent = textarea.value.length;
}

// Atualiza o contador ao carregar a página (caso de edição)
document.addEventListener('DOMContentLoaded', atualizarContador);