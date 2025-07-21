document.addEventListener('DOMContentLoaded', function() {
    const btnSalvarSenha = document.getElementById('btnSalvarSenha');

    function toggleSenha(inputId, toggleId) {
        const input = document.getElementById(inputId);
        const icon = document.getElementById(toggleId);
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('bx-show');
            icon.classList.add('bx-hide');
        } else {
            input.type = 'password';
            icon.classList.remove('bx-hide');
            icon.classList.add('bx-show');
        }
    }

    document.getElementById('toggleSenhaAtual').addEventListener('click', function () {
        toggleSenha('senhaAtual', 'toggleSenhaAtual');
    });

    document.getElementById('toggleNovaSenha').addEventListener('click', function () {
        toggleSenha('novaSenha', 'toggleNovaSenha');
    });

    if (btnSalvarSenha) {
        btnSalvarSenha.addEventListener('click', function() {
            const senhaAtual = document.getElementById('senhaAtual').value;
            const novaSenha = document.getElementById('novaSenha').value;
            const confirmarSenha = document.getElementById('confirmarSenha').value;
            
            // Validações básicas no frontend
            if (!senhaAtual || !novaSenha || !confirmarSenha) {
                Swal.fire({
                    icon: 'error',
                    title: 'Campos vazios',
                    text: 'Por favor, preencha todos os campos!',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }

            if (novaSenha.length < 6 || novaSenha.length > 12) {
                Swal.fire({
                    icon: 'error',
                    title: 'Senha inválida',
                    text: 'A nova senha deve ter entre 6 e 12 caracteres.',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }

            if (novaSenha !== confirmarSenha) {
                Swal.fire({
                    icon: 'error',
                    title: 'Senhas não coincidem',
                    text: 'A nova senha e a confirmação devem ser iguais!',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }
            
            // Mostra loading enquanto processa
            Swal.fire({
                title: 'Alterando senha...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            // Chamada AJAX para o backend
            fetch(window.URL_CONFIG.alterar_senha || '{{ url_for("configuracao.alterar_senha") }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    senha_atual: senhaAtual,
                    nova_senha: novaSenha,
                    confirmar_senha: confirmarSenha
                })
            })
            .then(response => response.json())
            .then(data => {
                Swal.close();
                
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Sucesso!',
                        text: data.message,
                        confirmButtonColor: '#3085d6'
                    }).then(() => {
                        // Fecha o modal
                        var modal = bootstrap.Modal.getInstance(document.getElementById('alterarSenhaModal'));
                        modal.hide();
                        
                        // Limpa os campos
                        document.getElementById('formAlterarSenha').reset();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro',
                        text: data.message || 'Ocorreu um erro ao alterar a senha',
                        confirmButtonColor: '#3085d6'
                    });
                }
            })
            .catch(error => {
                Swal.close();
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: 'Erro na comunicação com o servidor',
                    confirmButtonColor: '#3085d6'
                });
            });
        });
    }
});
