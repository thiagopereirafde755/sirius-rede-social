$('#imageModal').on('show.bs.modal', function () {
    $('body').addClass('modal-open');
});

$('#imageModal').on('hidden.bs.modal', function () {
    $('body').removeClass('modal-open');
});