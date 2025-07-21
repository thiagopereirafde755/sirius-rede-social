document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.link-perfil').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const idPesquisado = link.dataset.id;
            const destino = link.dataset.url;

            fetch('/salvar-historico', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id_pesquisado: idPesquisado })
            })
            .then(res => {
                window.location.href = destino;
            })
            .catch(() => {
                window.location.href = destino;
            });
        });
    });
});