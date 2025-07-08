document.querySelectorAll('.btn-excluir-post').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const form = btn.closest('form');
        Swal.fire({
            title: 'Tem certeza?',
            text: 'Deseja mesmo excluir este post?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sim, excluir!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                form.submit();
            }
        });
    });
});