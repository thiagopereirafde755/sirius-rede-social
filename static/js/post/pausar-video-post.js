$(document).ready(function () {
    /* -----------------------------
     * 1. Pausar vídeos ao fechar modais
     * ----------------------------- */
    $('#modalCriarPost, #imageModal, .modal-coment').on('hidden.bs.modal', function () {
        $(this).find('video').each(function () { this.pause(); });
    });

    /* -----------------------------
     * 2. Pausar vídeo ao clicar em outro post
     * ----------------------------- */
    $('.post').on('click', function () {
        const $postClicado = $(this);

        // Pausa todos os vídeos que NÃO estão dentro do post clicado
        $('video').not($postClicado.find('video')).each(function () {
            this.pause();
        });
    });

    /* -----------------------------
     * 3. Pausar vídeo ao mudar slide do carrossel
     * ----------------------------- */
    $('.carousel').on('afterChange', function (event, slick, currentSlide) {
        $(slick.$slides.get(currentSlide)).find('video').each(function () { this.pause(); });
    });

    /* -----------------------------
     * 4. Tocar/pausar vídeos automaticamente
     *    – bloqueia novos plays se há vídeo em fullscreen
     * ----------------------------- */
    const videos  = document.querySelectorAll('video');
    const options = { root: null, rootMargin: '0px', threshold: 0.8 };

    const isVideoFullscreen = () =>
        document.fullscreenElement && document.fullscreenElement.tagName === 'VIDEO';

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const video = entry.target;

            if (isVideoFullscreen()) {
                if (video !== document.fullscreenElement) video.pause();
                return;
            }

            if (entry.isIntersecting) {
                video.play().catch(() => {});
            } else {
                video.pause();
            }
        });
    }, options);

    videos.forEach(video => observer.observe(video));

    ['fullscreenchange', 'webkitfullscreenchange', 'mozfullscreenchange', 'MSFullscreenChange']
        .forEach(evt => document.addEventListener(evt, () => {
            if (!isVideoFullscreen()) {
                videos.forEach(v => observer.unobserve(v));
                videos.forEach(v => observer.observe(v));
            }
        }));

    /* -----------------------------
     * 5. Pausar vídeos ao sair da aba ou página
     * ----------------------------- */
    window.addEventListener('beforeunload', () => {
        document.querySelectorAll('video').forEach(v => v.pause());
    });
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            document.querySelectorAll('video').forEach(v => v.pause());
        }
    });

    /* -----------------------------
     * 6. Tocar vídeos visíveis no carregamento
     * ----------------------------- */
    videos.forEach(video => {
        const rect   = video.getBoundingClientRect();
        const inside = rect.top >= 0 &&
                       rect.left >= 0 &&
                       rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                       rect.right  <= (window.innerWidth  || document.documentElement.clientWidth);
        if (inside) {
            video.play().catch(() => {});
        }
    });

    /* -----------------------------
     * 7. Ativar áudio após interação do usuário
     *    – ao clicar/tocar/pressionar qualquer parte da página
     * ----------------------------- */
    const enableAudio = () => {
        videos.forEach(video => {
            const rect = video.getBoundingClientRect();
            const visible = rect.top < window.innerHeight && rect.bottom > 0;
            if (visible) {
                video.muted  = false;
                video.volume = 1;
            }
        });
    /* -----------------------------
     * 8. Repetir vídeo automaticamente ao terminar
     * ----------------------------- */
    videos.forEach(video => {
        video.addEventListener('ended', () => {
            video.currentTime = 0;
            video.play().catch(() => {});
        });
    });
        // Remove os listeners após a primeira interação
        window.removeEventListener('click', enableAudio);
        window.removeEventListener('touchstart', enableAudio);
        window.removeEventListener('keydown', enableAudio);
    };

    window.addEventListener('click', enableAudio, { once: true });
    window.addEventListener('touchstart', enableAudio, { once: true });
    window.addEventListener('keydown', enableAudio, { once: true });
});
