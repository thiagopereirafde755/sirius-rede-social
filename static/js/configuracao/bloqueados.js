$(document).ready(function() {
    // Carrega a lista de bloqueados ao abrir a página
    carregarBloqueados();

    // Pesquisa de usuários
    $('#pesquisa-usuario').on('input', function() {
        const termo = $(this).val().trim();

        if (termo.length > 0) {
            $.post(
                buscaUrl('pesquisar_usuarios'),
                { termo: termo },
                function(data) {
                    let resultados;
                    try {
                        resultados = JSON.parse(data);
                    } catch (e) {
                        $('#resultados-pesquisa').empty().append('<div class="alert alert-danger">Erro de resposta do servidor.</div>').show();
                        return;
                    }
                    const container = $('#resultados-pesquisa');
                    container.empty();

                    if (resultados.error) {
                        container.append(`<div class="alert alert-danger">${resultados.error}</div>`);
                    } else if (resultados.length === 0) {
                        container.append('<div class="alert alert-info">Nenhum usuário encontrado</div>');
                    } else {
                        resultados.forEach(usuario => {
                            const btnTexto = usuario.ja_bloqueado ? 'Desbloquear' : 'Bloquear';
                            const btnClasse = usuario.ja_bloqueado ? 'btn-desbloquear' : 'btn-bloquear';

                            container.append(`
                                <div class="usuario-item" data-id="${usuario.id}">
                                    <img src="${usuario.foto_perfil}" alt="${usuario.nome}">
                                    <div class="usuario-info">
                                        <strong>${usuario.nome}</strong>
                                        <small>${usuario.username}</small>
                                    </div>
                                    <button class="${btnClasse}" data-id="${usuario.id}">
                                        ${btnTexto}
                                    </button>
                                </div>
                            `);
                        });
                    }
                    container.show();
                }
            );
        } else {
            $('#resultados-pesquisa').hide().empty();
        }
    });

    $(document).on('click', '.btn-bloquear, .btn-desbloquear', function() {
        const usuarioId = $(this).data('id');
        const isBloquear = $(this).hasClass('btn-bloquear');
        const endpoint = isBloquear ? buscaUrl('bloquear_usuario') : buscaUrl('desbloquear_usuario');
        const btn = $(this);

        $.post(endpoint, { bloqueado_id: usuarioId }, function(data) {
            let response;
            try {
                response = JSON.parse(data);
            } catch (e) {
                alert('Erro de resposta do servidor.');
                return;
            }

            if (response.error) {
                alert('Erro: ' + response.error);
            } else {
                carregarBloqueados();
                $('#pesquisa-usuario').trigger('input');
            }
        });
    });

    function carregarBloqueados() {
        $.get(buscaUrl('listar_bloqueados'), function(data) {
            let bloqueados;
            try {
                bloqueados = JSON.parse(data);
            } catch (e) {
                $('#lista-bloqueados').empty().append('<div class="alert alert-danger">Erro de resposta do servidor.</div>');
                return;
            }
            const container = $('#lista-bloqueados');
            container.empty();

            if (bloqueados.error) {
                container.append(`<div class="alert alert-danger">${bloqueados.error}</div>`);
            } else if (bloqueados.length === 0) {
                container.append('<div class="alert alert-info">Você não bloqueou nenhum usuário ainda.</div>');
            } else {
                bloqueados.forEach(usuario => {
                    container.append(`
                        <div class="usuario-item" data-id="${usuario.id}">
                            <img src="${usuario.foto_perfil}" alt="${usuario.nome}">
                            <div class="usuario-info">
                                <strong>${usuario.nome}</strong>
                                <small>${usuario.username}</small>
                            </div>
                            <button class="btn-desbloquear" data-id="${usuario.id}">
                                Desbloquear
                            </button>
                        </div>
                    `);
                });
            }
        });
    }

    function buscaUrl(endpoint) {
        // Estes valores devem ser passados no template para o JS como variáveis globais
        // Exemplo de uso no template:
        // <script>
        //   window.URL_CONFIG = {
        //     pesquisar_usuarios: "{{ url_for('configuracao.pesquisar_usuarios') }}",
        //     bloquear_usuario: "{{ url_for('configuracao.bloquear_usuario') }}",
        //     desbloquear_usuario: "{{ url_for('configuracao.desbloquear_usuario') }}",
        //     listar_bloqueados: "{{ url_for('configuracao.listar_bloqueados') }}"
        //   }
        // </script>
        if (window.URL_CONFIG && window.URL_CONFIG[endpoint]) {
            return window.URL_CONFIG[endpoint];
        }
        return endpoint;
    }
});