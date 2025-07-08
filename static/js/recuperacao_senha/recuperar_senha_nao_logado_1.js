document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('RecupForm');
  const emailInput = document.getElementById('email');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const email = emailInput.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email) {
      Swal.fire({ icon: 'warning', title: 'Campo vazio', text: 'Por favor, preencha o email.' });
      return;
    }

    if (!emailRegex.test(email)) {
      Swal.fire({ icon: 'error', title: 'Email inválido', text: 'Digite um email válido.' });
      return;
    }

    Swal.fire({
      icon: 'info',
      title: 'Processando...',
      text: 'Aguarde, estamos enviando o código.',
      showConfirmButton: false,
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
        form.submit();
      }
    });
  });

  const alertData = document.getElementById('alert-data');
  const erroEmail = alertData.getAttribute('data-erro') === '1';
  const sucesso = alertData.getAttribute('data-sucesso') === '1';
  const urlParte2 = alertData.getAttribute('data-url');

  if (erroEmail) {
    Swal.fire({ icon: 'error', title: 'Email não encontrado', text: 'Não encontramos este email. Tente novamente.' });
  } else if (sucesso) {
    Swal.fire({ icon: 'success', title: 'Código enviado', text: 'Enviamos o código de recuperação para o seu email.' })
      .then(() => window.location.href = urlParte2);
  }
});
