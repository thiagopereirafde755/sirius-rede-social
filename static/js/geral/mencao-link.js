document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('mention-link')) {
            e.preventDefault();
            const username = e.target.dataset.username;
            
            // Faz uma requisição para obter o ID do usuário mencionado
            fetch(`/obter_id_usuario?username=${username}`)
                .then(response => response.json())
                .then(data => {
                    if (data.id) {
                        // Redireciona para a página do usuário
                        window.location.href = `/info-user/${data.id}`;
                    } else {
                        console.error('Usuário não encontrado');
                    }
                })
                .catch(error => {
                    console.error('Erro ao buscar usuário:', error);
                });
        }
    });
});