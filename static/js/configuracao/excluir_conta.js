    document.addEventListener('DOMContentLoaded', function() {
  // Mostrar/ocultar senha
  document.getElementById('toggleSenhaExcluir').addEventListener('click', function () {
    const senhaInput = document.getElementById('senhaExcluir');
    senhaInput.type = senhaInput.type === 'password' ? 'text' : 'password';
    this.classList.toggle('bx-show');
    this.classList.toggle('bx-hide');
  });

  document.getElementById('formExcluirConta').addEventListener('submit', function (e) {
    e.preventDefault();

    const senha = document.getElementById('senhaExcluir').value.trim();
    const confirmar = document.getElementById('confirmarSenhaExcluir').value.trim();

    if (senha !== confirmar) {
      Swal.fire({
        icon: 'error',
        title: 'Erro',
        text: 'As senhas não coincidem!',
        confirmButtonColor: '#d33'
      });
      return;
    }

    Swal.fire({
      title: 'Tem certeza?',
      text: "Esta ação é irreversível e excluirá sua conta permanentemente!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sim, excluir!',
      cancelButtonText: 'Cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        fetch('/excluir_conta', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ senha: senha, confirmarSenhaExcluir: confirmar })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            Swal.fire({
              icon: 'success',
              title: 'Conta excluída',
              text: data.message || 'Sua conta foi excluída com sucesso.',
              confirmButtonColor: '#3085d6'
            }).then(() => {
              window.location.href = '/'; 
            });
          } else {
            Swal.fire({
              icon: 'error',
              title: 'Erro',
              text: data.message || 'Erro ao excluir a conta.',
              confirmButtonColor: '#d33'
            });
          }
        })
        .catch(() => {
          Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: 'Erro na comunicação com o servidor.',
            confirmButtonColor: '#d33'
          });
        });
      } else {
        const modalEl = document.getElementById('excluirContaModal');
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) modalInstance.hide();
      }
    });
  });
});
