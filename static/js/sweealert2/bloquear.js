function bloquearUsuario(userId) {
    Swal.fire({
        title: 'Tem certeza?',
        text: 'Tem certeza que deseja bloquear este usuário? Você não verá mais os posts dele.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, bloquear!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('bloquear-form-' + userId).submit();
        }
    });
}

$(document).on('click', '.btn-bloquear-usuario', function(e) {
    e.preventDefault();
    var id = $(this).data('id');
    Swal.fire({
        title: 'Tem certeza?',
        text: "Tem certeza que deseja bloquear este usuário? Você não verá mais os posts dele.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, bloquear',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('form-bloquear-' + id).submit();
        }
    });
});

$(document).on('click', '.btn-bloquear-usuario', function(e) {
    e.preventDefault();
    var id = $(this).data('id');
    Swal.fire({
        title: 'Bloquear usuário?',
        text: "Tem certeza que deseja bloquear este usuário? Você deixará de ver os posts, não poderá enviar mensagens e nem seguir.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, bloquear',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('form-bloquear-' + id).submit();
        }
    });
});