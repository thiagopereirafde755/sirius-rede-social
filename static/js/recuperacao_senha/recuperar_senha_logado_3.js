document.addEventListener('DOMContentLoaded', () => {
    const toggleSenha    = document.getElementById('toggleSenha');
    const inputSenha     = document.getElementById('nova_senha');
    const senhaMensagem  = document.getElementById('senhaMensagem');

    toggleSenha.addEventListener('click', () => {
        const mostrar = inputSenha.type === 'password';
        inputSenha.type = mostrar ? 'text' : 'password';
        toggleSenha.classList.toggle('bx-show', !mostrar);
        toggleSenha.classList.toggle('bx-hide',  mostrar);
    });

    const senhaRegex = /^.{6,12}$/;

    inputSenha.addEventListener('input', () => {
        const ok = senhaRegex.test(inputSenha.value);
        senhaMensagem.style.color   = ok ? 'green' : 'red';
        senhaMensagem.textContent   = 'A senha deve ter entre 6 e 12 caracteres.';
    });
});
