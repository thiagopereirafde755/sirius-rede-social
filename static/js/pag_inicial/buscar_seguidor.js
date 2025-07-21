document.addEventListener('DOMContentLoaded', function() {
    // Função auxiliar para mostrar/ocultar mensagem de "nenhum encontrado"
    function handleEmptyList(inputId, listSelector, usernameSelector, emptyMsgId, emptyMsgHTML) {
        const input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('keyup', function() {
            const filter = input.value.toLowerCase();
            const list = document.querySelectorAll(listSelector + ' li');
            let found = 0;

            list.forEach(function(li) {
                const username = li.querySelector(usernameSelector).textContent.toLowerCase();
                if (username.indexOf(filter) > -1) {
                    li.style.display = '';
                    found++;
                } else {
                    li.style.display = 'none';
                }
            });

            let emptyMsg = document.getElementById(emptyMsgId);
            // Adiciona mensagem apenas se não houver itens visíveis
            if (found === 0) {
                if (!emptyMsg) {
                    emptyMsg = document.createElement('div');
                    emptyMsg.id = emptyMsgId;
                    emptyMsg.innerHTML = emptyMsgHTML;
                    emptyMsg.style.marginTop = "30px";
                    emptyMsg.style.textAlign = "center";
                    emptyMsg.style.color = "#fff";
                    document.querySelector(listSelector).parentNode.appendChild(emptyMsg);
                }
            } else {
                if (emptyMsg) emptyMsg.remove();
            }
        });
    }

    // Filtro de seguidores
    handleEmptyList(
        'search-seguidor',
        '#seguidores-list',
        '.seguidor-username',
        'nenhum-seguidor-encontrado',
        "<i class='bx bx-user-x' style='font-size:2.5rem;'></i><p>Nenhum usuário encontrado</p>"
    );

    // Filtro de seguindo
    handleEmptyList(
        'search-seguindo',
        '#seguindo-list',
        '.seguindo-username',
        'nenhum-seguindo-encontrado',
        "<i class='bx bx-user-x' style='font-size:2.5rem;'></i><p>Nenhum usuário encontrado</p>"
    );

    // Filtro de amigos em comum (adicionado)
    handleEmptyList(
        'search-amigos-comuns',       // id do input de busca no modal de amigos em comum
        '#amigos-comuns-list',        // seletor da lista de amigos
        '.amigo-username',            // seletor do elemento com username dentro do li
        'nenhum-amigo-comum-encontrado', // id para a mensagem "nenhum amigo encontrado"
        "<i class='bx bx-user-x' style='font-size:2.5rem;'></i><p>Nenhum amigo encontrado</p>" // html da mensagem
    );
});
