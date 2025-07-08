document.addEventListener('DOMContentLoaded', function () {
  const alertData = document.getElementById('alert-data');
  const erro = alertData.getAttribute('data-erro') === '1';
  const sucesso = alertData.getAttribute('data-sucesso') === '1';
  const proximaEtapa = alertData.getAttribute('data-url');
  const btnReenviar = document.getElementById('reenviar-codigo');
  const contadorTempo = document.getElementById('contador-tempo');

  // *** NOVO: pega URL da div #url-data ***
  const urlData = document.getElementById('url-data');
  const urlReenviar = urlData ? urlData.getAttribute('data-url') : '';

  // Função para iniciar o contador (bloqueia link "Reenviar código" por X segundos)
  function iniciarContador(segundosRestantes) {
    btnReenviar.style.pointerEvents = 'none';
    btnReenviar.style.color = 'gray';
    contadorTempo.style.display = 'inline';

    const fim = Date.now() + segundosRestantes * 1000;
    localStorage.setItem('reenviar_codigo_fim', fim);

    const interval = setInterval(() => {
      const agora = Date.now();
      const restante = Math.round((fim - agora) / 1000);

      if (restante <= 0) {
        clearInterval(interval);
        btnReenviar.style.pointerEvents = 'auto';
        btnReenviar.style.color = '';
        contadorTempo.style.display = 'none';
        localStorage.removeItem('reenviar_codigo_fim');
      } else {
        contadorTempo.textContent = `(${restante}s)`;
      }
    }, 1000);
  }

  // Exibe alerta se erro ou sucesso na submissão do código
  if (erro) {
    Swal.fire({
      icon: 'error',
      title: 'Código incorreto',
      text: 'O código digitado está errado ou expirado. Tente novamente.'
    });
  }

  if (sucesso) {
    Swal.fire({
      icon: 'success',
      title: 'Código válido!',
      text: 'Redirecionando para redefinir sua senha...',
      timer: 2000,
      showConfirmButton: false
    }).then(() => {
      window.location.href = proximaEtapa;
    });
  }

  // Verifica se existe contador ativo no localStorage e reinicia-o
  const fimSalvo = localStorage.getItem('reenviar_codigo_fim');
  if (fimSalvo && parseInt(fimSalvo) > Date.now()) {
    const restante = Math.round((parseInt(fimSalvo) - Date.now()) / 1000);
    iniciarContador(restante);
  }

  // Clique no botão "Reenviar código"
  btnReenviar.addEventListener('click', function (e) {
    e.preventDefault();

    Swal.fire({
      icon: 'info',
      title: 'Processando...',
      text: 'Estamos reenviando o código para seu email.',
      showConfirmButton: false,
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });

    fetch(urlReenviar, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(res => res.json())
      .then(data => {
        Swal.close();

        if (data.success) {
          Swal.fire({
            icon: 'success',
            title: 'Código reenviado',
            text: 'Enviamos um novo código para seu email.'
          });
          iniciarContador(60);
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: data.message || 'Não foi possível reenviar o código.'
          }).then(() => {
            if (data.redirect) {
              window.location.href = data.redirect;
            }
          });
        }
      })
      .catch(() => {
        Swal.close();
        Swal.fire({
          icon: 'error',
          title: 'Erro',
          text: 'Erro ao comunicar com o servidor.'
        });
      });
  });
});
