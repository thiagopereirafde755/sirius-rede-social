document.addEventListener('DOMContentLoaded', () => {
    const toggleSenha = document.getElementById('toggleSenha');
    const senhaInput = document.getElementById('password');

    toggleSenha.addEventListener('click', () => {
        if (senhaInput.type === 'password') {
            senhaInput.type = 'text';
            toggleSenha.classList.remove('bx-show');
            toggleSenha.classList.add('bx-hide');
        } else {
            senhaInput.type = 'password';
            toggleSenha.classList.remove('bx-hide');
            toggleSenha.classList.add('bx-show');
        }
    });
});
