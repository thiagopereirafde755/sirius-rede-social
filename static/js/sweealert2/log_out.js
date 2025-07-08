document.getElementById('logout-link').addEventListener('click', function(e) {
    e.preventDefault();
    Swal.fire({
        title: 'Tem certeza que deseja sair?',
        text: "Você será deslogado da sua conta.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#a76ab6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sim, sair',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = '/logout';
        }
    });
});