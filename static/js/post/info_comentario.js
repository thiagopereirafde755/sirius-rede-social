document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.comment-count').forEach(element => {
    element.addEventListener('click', () => {
      const count = element.getAttribute('data-count');
      Swal.fire({
        icon: 'info',
        title: 'Quantidade de Comentários',
        html: 'Esse número mostra quantos comentários esse post teve. Para mais informações, visite a <a target="_blank" href="/central_ajuda/comentarios_de_post" style="color: #3b7ddd; text-decoration: underline;">central de ajuda</a>.',
        confirmButtonText: 'Ok',
        confirmButtonColor: '#3085d6'
      });
    });
  });
});
