document.addEventListener('DOMContentLoaded', () => {
    const isMobile = /Mobi|Android/i.test(navigator.userAgent);

    if (isMobile && document.documentElement.requestFullscreen) {
        let fullscreenAtivado = false;

        const ativarFullscreen = () => {
            if (!fullscreenAtivado && !document.fullscreenElement) {
                document.documentElement.requestFullscreen()
                    .then(() => fullscreenAtivado = true)
                    .catch(err => console.warn('Erro ao entrar em fullscreen:', err));
            }
        };

        document.addEventListener('click', ativarFullscreen, { once: true });
        document.addEventListener('touchstart', ativarFullscreen, { once: true });
    }

    const textarea = document.getElementById('mensagem');
    if (textarea) {
        textarea.addEventListener('focus', () => {
            setTimeout(() => {
                textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });
    }
});
