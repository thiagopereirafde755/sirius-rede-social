 document.querySelector('.form-recuperacao').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch(window.location.href, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
    Swal.fire({
        icon: 'success',
        title: 'Sucesso!',
        text: 'Senha alterada com sucesso!',
        showConfirmButton: false,
        timer: 2000  // Fecha após 2 segundos
    }).then(() => {
        window.location.href = data.redirect;
    });
} else {
            Swal.fire({
                icon: 'error',
                title: 'Erro!',
                text: data.error || 'Ocorreu um erro',
                confirmButtonColor: '#3085d6'
            });
        }
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Erro!',
            text: 'Falha na comunicação com o servidor',
            confirmButtonColor: '#3085d6'
        });
    }
});