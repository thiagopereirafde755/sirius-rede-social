let notificacoesAtivadas = localStorage.getItem('notificacoesNavegador') !== 'desativado';

document.getElementById('form-notificacoes-navegador').addEventListener('submit', function (e) {
    e.preventDefault();
    const selecao = document.getElementById('notificacoes_navegador').value;
    localStorage.setItem('notificacoesNavegador', selecao);
    notificacoesAtivadas = selecao === 'ativado';

    Swal.fire({
        icon: 'success',
        title: 'Preferência atualizada!',
        text: 'Suas notificações do navegador foram configuradas com sucesso.',
        confirmButtonColor: '#3085d6',
        confirmButtonText: 'OK'
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('notificacoes_navegador');
    const status = localStorage.getItem('notificacoesNavegador') || 'ativado';
    select.value = status;
    notificacoesAtivadas = status === 'ativado';
});