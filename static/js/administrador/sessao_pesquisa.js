document.addEventListener('DOMContentLoaded', () => {
    // Evento para abrir modal de detalhes
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('modalPesquisaId').textContent = btn.dataset.id;
            document.getElementById('modalPesquisaUsername').textContent = btn.dataset.username;
            document.getElementById('modalPesquisaTermo').textContent = btn.dataset.termo;
            document.getElementById('modalPesquisaData').textContent = btn.dataset.data;
        });
    });

    // Evento para deletar termo com SweetAlert2
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', () => {
            const termoId = btn.dataset.id;

            Swal.fire({
                title: 'Tem certeza?',
                text: "Quer apagar este termo da pesquisa?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sim, apagar!',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/apagar_pesquisa/${termoId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            Swal.fire(
                                'Apagado!',
                                'O termo foi removido com sucesso.',
                                'success'
                            );
                            btn.closest('tr').remove();
                        } else {
                            Swal.fire(
                                'Erro!',
                                'Não foi possível apagar o termo.',
                                'error'
                            );
                        }
                    })
                    .catch(() => {
                        Swal.fire(
                            'Erro!',
                            'Não foi possível apagar o termo.',
                            'error'
                        );
                    });
                }
            });
        });
    });
});
