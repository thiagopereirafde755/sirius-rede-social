// Função para abrir o modal com a imagem em tamanho completo
document.querySelectorAll('.foto-post').forEach(function(img) {
    img.addEventListener('click', function() {
        var modalImage = document.getElementById('modal-image');
        modalImage.src = this.src; // Define a imagem do modal para ser a mesma da imagem clicada
        $('#imageModal').modal('show'); // Abre o modal usando o Bootstrap
    });
});