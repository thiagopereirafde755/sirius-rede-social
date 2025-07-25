   document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.hashtag-nome').forEach(function (el) {
    const maxLength = 10;
    const textoOriginal = el.textContent.trim();

    // Separa o nome da hashtag e o total
    const partes = textoOriginal.split(' -'); 

    if (partes.length === 2) {
      const nome = partes[0];
      const total = partes[1];

      // Adiciona "..." se o nome for muito longo
      const nomeFormatado = nome.length > maxLength
        ? nome.substring(0, maxLength) + '...'
        : nome;

      el.textContent = `${nomeFormatado} - ${total}`;
      el.title = textoOriginal;
    }
  });
});