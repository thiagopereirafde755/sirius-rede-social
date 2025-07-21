document.addEventListener('DOMContentLoaded', function () {
  document.addEventListener('click', function (e) {
    if (e.target.classList.contains('mention-link')) {
      e.preventDefault();
      const userId = e.target.dataset.id;
      if (userId) {
        window.location.href = `/info-user/${userId}`;
      } else {
        console.error('ID do usuário não encontrado no link.');
      }
    }
  });
});
