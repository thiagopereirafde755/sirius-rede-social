document.addEventListener('DOMContentLoaded', function() {
    // ALERTA PARA REMOVER FOTO DE PERFIL
    const removerFotoBtn = document.getElementById('remover-foto-btn');
    
    if (removerFotoBtn) {
        removerFotoBtn.addEventListener('click', function() {
            Swal.fire({
                title: 'Remover Foto de Perfil',
                text: 'Tem certeza que deseja remover sua foto de perfil?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sim, remover',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6'
            }).then((result) => {
                if (result.isConfirmed) {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = '/alterar_foto_perfil';
                    
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'remover_foto_perfil';
                    input.value = '1';
                    form.appendChild(input);
                    
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // ALERTA PARA REMOVER FOTO DE CAPA
    const removerCapaBtn = document.getElementById('remover-capa-btn');
    
    if (removerCapaBtn) {
        removerCapaBtn.addEventListener('click', function() {
            Swal.fire({
                title: 'Remover Foto de Capa',
                text: 'Tem certeza que deseja remover sua foto de capa?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sim, remover',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = '/alterar_capa';
                    
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'remover_foto_capa';
                    input.value = '1';
                    form.appendChild(input);
                    
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // ALERTA PARA BIO
    const bioForm = document.getElementById('bioForm');
    if (!bioForm) return;

    // Corrigido para pegar o textarea
    const bioInput = bioForm.querySelector('textarea[name="nova_bio"]');
    const bioAtual = bioInput ? bioInput.defaultValue.trim() : '';

    bioForm.addEventListener('submit', function(e) {
        const submitter = e.submitter;

        if (submitter && submitter.name === 'apagar_bio') {
            e.preventDefault();

            Swal.fire({
                title: 'Apagar Biografia',
                text: 'Tem certeza que deseja apagar sua biografia?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sim, apagar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = 'apagar_bio';
                    input.value = '1';
                    bioForm.appendChild(input);
                    bioForm.submit();
                }
            });
            return;
        }

        if (submitter && submitter.name === 'alterar_bio') {
            e.preventDefault();

            const novaBio = bioInput.value.trim();

            if (!novaBio) {
                Swal.fire({
                    title: 'Campo vazio',
                    text: 'Por favor, digite uma biografia antes de enviar.',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                return;
            }

            if (novaBio === bioAtual) {
                Swal.fire({
                    title: 'Nenhuma alteração',
                    text: 'A biografia digitada é igual à atual.',
                    icon: 'info',
                    confirmButtonText: 'OK'
                });
                return;
            }

            Swal.fire({
                title: 'Confirmar alteração',
                text: 'Tem certeza que deseja alterar sua biografia?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sim, alterar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    bioForm.submit();
                }
            });
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // ALERTA PARA O NOME
    const nomeForm = document.getElementById('nomeForm');
    if (!nomeForm) return;

    const nomeInput = nomeForm.querySelector('textarea[name="novo_nome"]');
    const nomeCharCount = document.getElementById('nome-char-count');
    const nomeAtual = nomeInput ? nomeInput.defaultValue.trim() : '';

    // Atualiza contador ao digitar e impede números/caracteres especiais
    if (nomeInput && nomeCharCount) {
        nomeInput.addEventListener('input', function() {
            // Só permite letras (maiúsculas/minúsculas), acentuadas e espaço
            const sanitized = this.value.replace(/[^a-zA-ZÀ-ÿ\s]/g, "");
            if (sanitized !== this.value) {
                this.value = sanitized;
            }
            nomeCharCount.textContent = this.value.length + '/60';
        });
    }

    nomeForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const novoNome = nomeInput.value.trim();

        // Bloqueia envio se houver caracteres inválidos (números ou especiais)
        if (/[^a-zA-ZÀ-ÿ\s]/.test(novoNome)) {
            Swal.fire({
                title: 'Caracteres inválidos',
                text: 'O nome não pode conter números nem caracteres especiais. Use apenas letras e espaços.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;
        }

        if (!novoNome) {
            Swal.fire({
                title: 'Campo vazio',
                text: 'Por favor, digite um nome antes de enviar.',
                icon: 'warning',
                confirmButtonText: 'OK'
            });
            return;
        }

        if (novoNome === nomeAtual) {
            Swal.fire({
                title: 'Nenhuma alteração',
                text: 'O nome digitado é igual ao atual.',
                icon: 'info',
                confirmButtonText: 'OK'
            });
            return;
        }

        Swal.fire({
            title: 'Confirmar alteração',
            html: `Você está alterando seu nome de <strong>${nomeAtual}</strong> para <strong>${novoNome}</strong>`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sim, alterar',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33'
        }).then((result) => {
            if (result.isConfirmed) {
                nomeForm.submit();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const alterarUserForm = document.getElementById('alterarUserForm');
    const novoUserInput = document.getElementById('novoUserInput');
    const userCharCount = document.getElementById('user-char-count');
    const userAtual = novoUserInput.value.trim();

    // Inicializa o contador de caracteres ao carregar
    if (novoUserInput && userCharCount) {
        userCharCount.textContent = novoUserInput.value.length + '/12';
        novoUserInput.addEventListener('input', function() {
            userCharCount.textContent = this.value.length + '/12';
            // Limita caracteres especiais ao digitar (opcional)
            this.value = this.value.replace(/[^a-zA-Z0-9_]/g, "");
            userCharCount.textContent = this.value.length + '/12';
        });
    }

    if (alterarUserForm) {
        alterarUserForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const novoUser = novoUserInput.value.trim();

            // Verifica se contém caracteres especiais proibidos
            if (/[^a-zA-Z0-9_]/.test(novoUser)) {
                Swal.fire({
                    title: 'Caracteres inválidos',
                    text: 'O nome de usuário não pode conter caracteres especiais como - @ * # $. Use apenas letras, números ou _ (underline)',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
                return;
            }

            if (!novoUser) {
                Swal.fire({
                    title: 'Campo vazio',
                    text: 'Por favor, digite um novo nome de usuário',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                return;
            }

            if (novoUser === userAtual) {
                Swal.fire({
                    title: 'Nenhuma alteração',
                    text: 'O nome de usuário digitado é igual ao atual',
                    icon: 'info',
                    confirmButtonText: 'OK'
                });
                return;
            }

            if (novoUser.length < 3) {
                Swal.fire({
                    title: 'Nome muito curto',
                    text: 'O nome de usuário deve ter pelo menos 3 caracteres',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                return;
            }

            Swal.fire({
                title: 'Confirmar alteração',
                html: `Você está alterando seu nome de usuário de <strong>${userAtual}</strong> para <strong>${novoUser}</strong>`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sim, alterar',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33'
            }).then((result) => {
                if (result.isConfirmed) {
                    alterarUserForm.removeEventListener('submit', arguments.callee);
                    alterarUserForm.submit();
                }
            });
        });
    }
});