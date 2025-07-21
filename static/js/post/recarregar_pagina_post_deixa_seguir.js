document.addEventListener('DOMContentLoaded', () => {
    const botoesRecarregar = document.querySelectorAll('.seguir-btn[data-recarregar="1"]');

    botoesRecarregar.forEach(botao => {
        botao.addEventListener('click', () => {
            sessionStorage.setItem('pular_loading_uma_vez', 'true');

            setTimeout(() => {
                location.reload();
            }, 500);
        });
    });
});
