document.addEventListener('DOMContentLoaded', () => {
  // SweetAlert para "Publicando..."
 const form = document.querySelector('form[action="/adicionar_postagem"]');
if (form) {
  form.addEventListener('submit', () => {
    // Bloqueia rolagem
    document.body.style.overflow = 'hidden';

    Swal.fire({
      title: 'Publicando...',
      text: 'Aguarde enquanto sua postagem é publicada.',
      allowOutsideClick: false,
      allowEscapeKey: false,
      allowEnterKey: false,
      didOpen: () => {
        Swal.showLoading();
      },
      willClose: () => {
        // Libera rolagem ao fechar o modal
        document.body.style.overflow = '';
      }
    });
  });
}


  // SweetAlert para "Informações da Conta"
  const infoContaLink = document.getElementById('infoContaLink');
  if (infoContaLink) {
    infoContaLink.addEventListener('click', (e) => {
      e.preventDefault();

      // Esses valores devem vir do HTML com data-atributos ou preenchidos pelo backend antes
      const username = infoContaLink.dataset.username;
      const email = infoContaLink.dataset.email;
      const dataNascimento = infoContaLink.dataset.nascimento;
      const dataCadastro = infoContaLink.dataset.cadastro;

      Swal.fire({
        title: 'Informações da sua Conta',
        html: `
          <div style="text-align: left; font-size: 1rem;">
            <p><strong>Username:</strong> ${username}</p>
            <p><strong>E-mail:</strong> ${email}</p>
            <p><strong>Data de nascimento:</strong> ${dataNascimento}</p>
            <p><strong>Data de Cadastro:</strong> ${dataCadastro}</p>
          </div>
        `,
        icon: 'info',
        confirmButtonText: 'Fechar',
        customClass: {
          popup: 'swal2-rounded swal2-padding'
        }
      });
    });
  }
});
