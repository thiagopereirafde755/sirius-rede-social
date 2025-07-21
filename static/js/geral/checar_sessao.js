function verificarSessao() {
    fetch('/check_session')
        .then(response => response.json())
        .then(data => {
            if (!data.valid) {
                Swal.fire({
                    title: 'Sessão expirada',
                    text: 'Você foi desconectado porque sua conta foi acessada em outro dispositivo.',
                    icon: 'warning',
                    showConfirmButton: false,  
                    timer: 5000,               
                    timerProgressBar: true,
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        document.body.style.overflow = 'hidden'
                    },
                    willClose: () => {
                        document.body.style.overflow = ''
                    }
                }).then(() => {
                    window.location.href = '/logout';
                });
            }
        })
        .catch(err => {
            console.error('Erro ao verificar sessão:', err);
        });
}

setInterval(verificarSessao, 12000);

verificarSessao();
