$(document).ready(function() {
    // Quando o modal é fechado
    $('#modalCriarPost').on('hidden.bs.modal', function () {
        // Pausa todos os vídeos dentro do modal
        $(this).find('video').each(function() {
            this.pause();
        });
    });

    // Quando o modal de imagem é fechado
    $('#imageModal').on('hidden.bs.modal', function () {
        // Pausa todos os vídeos dentro do modal
        $(this).find('video').each(function() {
            this.pause();
        });
    });
});$(document).ready(function() {
    // Quando você clica em outro post ou navega para outra seção
    $('.post').on('click', function() {
        // Pausa todos os vídeos no post atual
        $(this).find('video').each(function() {
            this.pause();
        });
    });
});$(document).ready(function() {
    // Quando o slide do carrossel muda
    $('.carousel').on('afterChange', function(event, slick, currentSlide) {
        // Pausa todos os vídeos no slide anterior
        $(slick.$slides.get(currentSlide)).find('video').each(function() {
            this.pause();
        });
    });
});$(document).ready(function() {
    // Quando o modal de comentários é fechado
    $('.modal-coment').on('hidden.bs.modal', function () {
        // Pausa todos os vídeos dentro do modal
        $(this).find('video').each(function() {
            this.pause();
        });
    });
});window.addEventListener('beforeunload', function() {
    // Pausa todos os vídeos na página
    document.querySelectorAll('video').forEach(function(video) {
        video.pause();
    });
});document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pausa todos os vídeos na página
        document.querySelectorAll('video').forEach(function(video) {
            video.pause();
        });
    }
});document.addEventListener('DOMContentLoaded', function () {
    // Seleciona todos os vídeos na página
    const videos = document.querySelectorAll('video');

    // Configurações do Intersection Observer
    const options = {
        root: null, // Observa a viewport
        rootMargin: '0px', // Sem margem
        threshold: 0.7, // 70% do vídeo precisa estar visível
    };

    // Função que será chamada quando a visibilidade mudar
    const callback = (entries, observer) => {
        entries.forEach(entry => {
            const video = entry.target;

            if (entry.isIntersecting) {
                // Se o vídeo está visível, toca o vídeo
                video.play();
            } else {
                // Se o vídeo não está visível, pausa o vídeo
                video.pause();
            }
        });
    };

    // Cria o Intersection Observer
    const observer = new IntersectionObserver(callback, options);

    // Observa cada vídeo na página
    videos.forEach(video => {
        observer.observe(video);
    });
});