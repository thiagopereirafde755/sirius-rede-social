document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formCadastro');
    const campos = {
        nome: {
            input: document.getElementById('nome'),
            error: document.getElementById('nome-error'),
            regex: /^[A-Za-zÀ-ÖØ-öø-ÿ\s]{1,60}$/,
            mensagem: 'O nome deve conter apenas letras e espaços e no máximo 60 caracteres'
        },
        username: {
            input: document.getElementById('username'),
            error: document.getElementById('username-error'),
            regex: /^[a-zA-Z0-9_]{1,12}$/,
            mensagem: 'O usuário deve conter apenas letras, números e "_" e ter no máximo 12 caracteres'
        },
        senha: {
            input: document.getElementById('senha'),
            error: document.getElementById('senha-error'),
            validacao: function () {
                const senha = this.input.value;
                if (senha.length < 6 || senha.length > 12) {
                    this.error.textContent = 'A senha deve ter entre 6 e 12 caracteres';
                    return false;
                }
                this.error.textContent = '';
                return true;
            }
        },
        confirmar_senha: {
            input: document.getElementById('confirmar_senha'),
            error: document.getElementById('confirmar-error'),
            validacao: function () {
                if (this.input.value !== campos.senha.input.value) {
                    this.error.textContent = 'As senhas não coincidem';
                    return false;
                }
                this.error.textContent = '';
                return true;
            }
        },
        data_nascimento: {
            input: document.getElementById('data_nascimento'),
            error: document.getElementById('idade-error'),
            validacao: function () {
                const nascimento = new Date(this.input.value);
                const hoje = new Date();
                let idade = hoje.getFullYear() - nascimento.getFullYear();
                const m = hoje.getMonth() - nascimento.getMonth();
                if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) {
                    idade--;
                }
                if (idade < 13) {
                    this.error.textContent = 'Você deve ter pelo menos 13 anos';
                    return false;
                }
                this.error.textContent = '';
                return true;
            }
        }
    };

    function exibirErro(campo) {
        campo.error.style.display = 'block';
        campo.input.parentElement.classList.add('invalid');
    }

    function esconderErro(campo) {
        campo.error.style.display = 'none';
        campo.input.parentElement.classList.remove('invalid');
        campo.error.textContent = '';
    }

    Object.keys(campos).forEach(id => {
        const campo = campos[id];

        if (id === 'senha') {
            // Ao digitar em senha, valida senha e confirmar_senha
            campo.input.addEventListener('input', () => {
                if (!campo.validacao()) {
                    exibirErro(campo);
                } else {
                    esconderErro(campo);
                }

                // Também valida confirmar_senha para atualizar o erro se as senhas agora batem
                const confirmar = campos.confirmar_senha;
                if (!confirmar.validacao()) {
                    exibirErro(confirmar);
                } else {
                    esconderErro(confirmar);
                }
            });
        } else if (campo.regex) {
            campo.input.addEventListener('input', () => {
                if (!campo.regex.test(campo.input.value) && campo.input.value.trim() !== '') {
                    campo.error.textContent = campo.mensagem;
                    exibirErro(campo);
                } else {
                    esconderErro(campo);
                }
            });
        } else if (campo.validacao) {
            campo.input.addEventListener('input', () => {
                if (!campo.validacao()) {
                    exibirErro(campo);
                } else {
                    esconderErro(campo);
                }
            });
        }
    });

    form.addEventListener('submit', function (e) {
        let isValid = true;

        Object.values(campos).forEach(campo => {
            if (campo.validacao && !campo.validacao()) {
                exibirErro(campo);
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
            Swal.fire({
                icon: 'error',
                title: 'Erro no formulário',
                text: 'Por favor, corrija os erros antes de enviar o formulário.',
                confirmButtonColor: '#a76ab6'
            });
        }
    });

    // Reexibe erros do back-end (já inseridos via Jinja)
    document.querySelectorAll('.error-message').forEach(el => {
        if (el.textContent.trim() !== '') {
            el.style.display = 'block';
            el.parentElement.classList.add('invalid');
        }
    });
});
