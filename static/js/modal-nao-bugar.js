$(document).on('hidden.bs.modal', function (e) {
    $('.modal-backdrop').remove();
});

// Quando o modal abrir
$('#modalEditarPerfil').on('shown.bs.modal', function () {
    document.body.classList.add('modal-open');
});

// Quando o modal for fechado
$('#modalEditarPerfil').on('hidden.bs.modal', function () {
    document.body.classList.remove('modal-open');
});