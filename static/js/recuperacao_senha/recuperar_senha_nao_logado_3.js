document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formRecuperarSenha');
    const senhaInput = document.getElementById('senha');
    const confirmarInput = document.getElementById('confirmar_senha');

    const senhaError = document.getElementById('senha-error');
    const confirmarError = document.getElementById('confirmar-error');

    function validarSenha() {
        const senha = senhaInput.value;
        const confirmar = confirmarInput.value;

        let valid = true;

        // Valida tamanho da senha
        if (senha.length < 6 || senha.length > 12) {
            senhaError.textContent = 'A senha deve ter entre 6 e 12 caracteres';
            senhaError.style.display = 'block';
            senhaInput.parentElement.classList.add('invalid');
            valid = false;
        } else {
            senhaError.textContent = '';
            senhaError.style.display = 'none';
            senhaInput.parentElement.classList.remove('invalid');
        }

        // Valida se senhas batem (apenas se confirmar não vazio)
        if (confirmar !== '') {
            if (senha !== confirmar) {
                confirmarError.textContent = 'As senhas não coincidem';
                confirmarError.style.display = 'block';
                confirmarInput.parentElement.classList.add('invalid');
                valid = false;
            } else {
                confirmarError.textContent = '';
                confirmarError.style.display = 'none';
                confirmarInput.parentElement.classList.remove('invalid');
            }
        } else {
            confirmarError.textContent = '';
            confirmarError.style.display = 'none';
            confirmarInput.parentElement.classList.remove('invalid');
        }

        return valid;
    }

    senhaInput.addEventListener('input', validarSenha);
    confirmarInput.addEventListener('input', validarSenha);

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!validarSenha()) {
            Swal.fire({
                icon: 'error',
                title: 'Erro no formulário',
                text: 'Por favor, corrija os erros antes de enviar o formulário.',
                confirmButtonColor: '#a76ab6'
            });
            return;
        }

        const nova_senha = senhaInput.value;
        const confirmar_senha = confirmarInput.value;

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nova_senha, confirmar_senha })
            });

            const data = await response.json();

            if (!response.ok) {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: data.error || 'Erro desconhecido',
                    confirmButtonColor: '#a76ab6'
                });
            } else {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso',
                    text: data.message || 'Senha alterada com sucesso!',
                    confirmButtonColor: '#a76ab6'
                }).then(() => {
                    window.location.href = data.redirect || '/';
                });
            }
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Erro de conexão',
                text: 'Não foi possível conectar ao servidor.',
                confirmButtonColor: '#a76ab6'
            });
        }
    });
});
