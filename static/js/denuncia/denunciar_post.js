$('#modalDenunciar').on('show.bs.modal', function (event) {
  const btn   = $(event.relatedTarget);
  const pId   = btn.data('post-id');
  $(this).find('#denunciarPostId').val(pId);
});

$('#modalDenunciar form').on('submit', async function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);

  try {
    const resp = await fetch('/api/denunciar', {
      method: 'POST',
      body:   formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const data = await resp.json();

    if (data.success) {
      $('#modalDenunciar').modal('hide');
      Swal.fire({icon: 'success', title: 'Pronto!', text: data.message});
      form.reset();
    } else {
      Swal.fire({icon: 'error', title: 'Ops!', text: data.message});
    }
  } catch (err) {
    Swal.fire({icon: 'error', title: 'Erro de rede', text: 'Tente novamente.'});
  }
});

document.addEventListener('DOMContentLoaded', function () {
  const textarea = document.getElementById('detalhes');
  const contador = document.getElementById('contadorDetalhes');
  const maxChars = 80;

  if (textarea && contador) {
    textarea.addEventListener('input', () => {
      const charsDigitados = textarea.value.length;
      contador.textContent = `${charsDigitados}/${maxChars}`;
    });

    contador.textContent = `0/${maxChars}`;
  }
});
