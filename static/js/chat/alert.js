document.addEventListener('DOMContentLoaded', function () {
  const btnAmigo = document.getElementById('abrir-amizade');
  if (btnAmigo) {
    const totalMensagens = parseInt(btnAmigo.dataset.mensagens, 10) || 0;
    btnAmigo.addEventListener('click', function (e) {
      e.preventDefault(); 
      Swal.fire({
        title: '💬 Amizade Digital',
        html: `<p>Vocês já trocaram <strong>${totalMensagens}</strong> mensagens!</p>`,
        icon: 'info',
        confirmButtonText: 'Fechar'
      });
    });
  }

  const botaoAjuda = document.getElementById('abrir-ajuda');
  if (botaoAjuda) {
    botaoAjuda.addEventListener('click', function (e) {
      e.preventDefault();
      Swal.fire({
        title: 'Central de Ajuda',
      html: 'Aqui você encontrará informações e orientações sobre o chat. <a target="_blank" href="/central_ajuda/chat" style="color: #4da6ff;" class="link">Ir para a Central de Ajuda</a>',
        icon: 'info',
        confirmButtonText: 'Entendi',
      });
    });
  }
});