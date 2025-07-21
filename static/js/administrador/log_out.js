document.addEventListener('DOMContentLoaded', function() {
    const logoutLink = document.querySelector('.logout');
    
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            Swal.fire({
                title: 'Tem certeza?',
                text: "Você será desconectado do sistema!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#a76ab6', 
                cancelButtonColor: '#6c757d', 
                confirmButtonText: 'Sim, sair!',
                cancelButtonText: 'Cancelar',
                background: '#2d2a32', 
                color: '#e0e0e0' 
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/logout_adm';
                }
            });
        });
    }
});