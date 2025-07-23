document.addEventListener('DOMContentLoaded', () => {
    const toggleSenha    = document.getElementById('toggleSenha');
    const toggleSenha2   = document.getElementById('toggleSenha2');
    const inputSenha     = document.getElementById('nova_senha');
    const inputSenha2    = document.getElementById('confirmar_senha');
    const senhaMensagem  = document.getElementById('senhaMensagem');

    toggleSenha.addEventListener('click', () => {
        const mostrar = inputSenha.type === 'password';
        inputSenha.type = mostrar ? 'text' : 'password';
        toggleSenha.classList.toggle('bx-show', !mostrar);
        toggleSenha.classList.toggle('bx-hide', mostrar);
    });

    toggleSenha2.addEventListener('click', () => {
        const mostrar = inputSenha2.type === 'password';
        inputSenha2.type = mostrar ? 'text' : 'password';
        toggleSenha2.classList.toggle('bx-show', !mostrar);
        toggleSenha2.classList.toggle('bx-hide', mostrar);
    });

    const senhaRegex = /^.{6,12}$/;

    inputSenha.addEventListener('input', () => {
        const ok = senhaRegex.test(inputSenha.value);
        senhaMensagem.style.color = ok ? 'green' : 'red';
        senhaMensagem.textContent = 'A senha deve ter entre 6 e 12 caracteres.';
    });
});
