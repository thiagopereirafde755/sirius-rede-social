function deletarMensagem(mensagemId) {
    Swal.fire({
        title: 'Tem certeza?',
        text: 'Tem certeza que deseja apagar esta mensagem?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, apagar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/deletar_mensagem/${mensagemId}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    lastMessageId = 0;
                    atualizarMensagens(true);
                    Swal.fire({
                        title: 'Apagada!',
                        text: 'A mensagem foi removida.',
                        icon: 'success',
                        timer: 1200,
                        showConfirmButton: false
                    });
                } else {
                    Swal.fire(
                        'Erro',
                        'Erro ao apagar a mensagem: ' + (data.error || ''),
                        'error'
                    );
                }
            })
            .catch(error => {
                Swal.fire(
                    'Erro',
                    'Erro ao apagar a mensagem.',
                    'error'
                );
                console.error('Erro:', error);
            });
        }
    });
}