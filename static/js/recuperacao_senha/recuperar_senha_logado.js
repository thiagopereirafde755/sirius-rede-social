if (window.erroEmail) {
    Swal.fire({
        icon: 'error',
        title: 'Erro!',
        text: 'O e-mail informado não corresponde ao seu usuário logado.',
        confirmButtonColor: '#3085d6'
    });
}

if (window.erroCodigo) {
    Swal.fire({
        icon: 'error',
        title: 'Código inválido',
        text: 'O código informado está incorreto ou expirou. Tente novamente.',
        confirmButtonColor: '#3085d6'
    });
}

if (window.erroSenha) {
    Swal.fire({
        icon: 'error',
        title: 'Erro!',
        text: window.msgErroSenha || 'As senhas não coincidem.',
        confirmButtonColor: '#3085d6'
    });
}

