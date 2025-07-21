// MODIFIQUE A FUNÇÃO deletarMensagem
function deletarMensagem(mensagemId) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Você não poderá reverter isso!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sim, apagar!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/deletar_mensagem/${mensagemId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Força a atualização marcando como exclusão
                    atualizarMensagens(false, false, true);
                    
                    Swal.fire(
                        'Apagada!',
                        'Sua mensagem foi apagada.',
                        'success'
                    );
                } else {
                    Swal.fire(
                        'Erro!',
                        'Não foi possível apagar a mensagem.',
                        'error'
                    );
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                Swal.fire(
                    'Erro!',
                    'Ocorreu um erro ao tentar apagar a mensagem.',
                    'error'
                );
            });
        }
    });
}
