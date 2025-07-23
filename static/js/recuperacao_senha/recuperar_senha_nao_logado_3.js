document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('formRecuperarSenha');
  const senhaInput = document.getElementById('senha');
  const confirmarInput = document.getElementById('confirmar_senha');

  const senhaError = document.getElementById('senha-error');
  const confirmarError = document.getElementById('confirmar-error');

  function validarSenha() {
    const senha = senhaInput.value;
    const confirmar = confirmarInput.value;
    let valid = true;

    if (senha.length < 6 || senha.length > 12) {
      senhaError.textContent = 'A senha deve ter entre 6 e 12 caracteres';
      senhaError.style.display = 'block';
      senhaInput.parentElement.classList.add('invalid');
      valid = false;
    } else {
      senhaError.textContent = '';
      senhaError.style.display = 'none';
      senhaInput.parentElement.classList.remove('invalid');
    }

    if (confirmar !== '') {
      if (senha !== confirmar) {
        confirmarError.textContent = 'As senhas não coincidem';
        confirmarError.style.display = 'block';
        confirmarInput.parentElement.classList.add('invalid');
        valid = false;
      } else {
        confirmarError.textContent = '';
        confirmarError.style.display = 'none';
        confirmarInput.parentElement.classList.remove('invalid');
      }
    }

    return valid;
  }

  senhaInput.addEventListener('input', validarSenha);
  confirmarInput.addEventListener('input', validarSenha);

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    if (!validarSenha()) {
      Swal.fire({
        icon: 'error',
        title: 'Erro no formulário',
        text: 'Por favor, corrija os erros antes de enviar.',
        confirmButtonColor: '#a76ab6'
      });
      return;
    }

    Swal.fire({
      title: 'Aguarde...',
      text: 'Redefinindo sua senha...',
      allowOutsideClick: false,
      showConfirmButton: false,
      background: '#2d2a32',
      color: '#e0e0e0',
      didOpen: () => {
        Swal.showLoading();
      }
    });

    const nova_senha = senhaInput.value;
    const confirmar_senha = confirmarInput.value;

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nova_senha, confirmar_senha })
      });

      let data;
      try {
        data = await response.json();
      } catch (err) {
        return Swal.fire({
          icon: 'error',
          title: 'Erro inesperado',
          text: 'Resposta inválida do servidor.',
          confirmButtonColor: '#a76ab6',
          background: '#2d2a32',
          color: '#e0e0e0'
        });
      }

      if (!response.ok || !data.success) {
        Swal.fire({
          icon: 'error',
          title: 'Erro',
          text: data.error || 'Erro ao redefinir a senha.',
          confirmButtonColor: '#a76ab6',
          background: '#2d2a32',
          color: '#e0e0e0'
        });
        return;
      }

      Swal.fire({
        icon: 'success',
        title: 'Sucesso',
        text: data.message || 'Senha redefinida com sucesso!',
        confirmButtonColor: '#a76ab6',
        background: '#2d2a32',
        color: '#e0e0e0'
      }).then(() => {
        window.location.href = data.redirect || '/';
      });

    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Erro de conexão',
        text: 'Não foi possível conectar ao servidor.',
        confirmButtonColor: '#a76ab6',
        background: '#2d2a32',
        color: '#e0e0e0'
      });
      console.error('Erro na requisição:', error);
    }
  });

  // Mostrar/ocultar senha - senha principal
  const toggleSenha1 = document.getElementById('toggleSenha1');
  if (toggleSenha1 && senhaInput) {
    toggleSenha1.addEventListener('click', () => {
      if (senhaInput.type === 'password') {
        senhaInput.type = 'text';
        toggleSenha1.classList.remove('bx-show');
        toggleSenha1.classList.add('bx-hide');
      } else {
        senhaInput.type = 'password';
        toggleSenha1.classList.remove('bx-hide');
        toggleSenha1.classList.add('bx-show');
      }
    });
  }

  // Mostrar/ocultar senha - confirmação
  const toggleSenha2 = document.getElementById('toggleSenha2');
  if (toggleSenha2 && confirmarInput) {
    toggleSenha2.addEventListener('click', () => {
      if (confirmarInput.type === 'password') {
        confirmarInput.type = 'text';
        toggleSenha2.classList.remove('bx-show');
        toggleSenha2.classList.add('bx-hide');
      } else {
        confirmarInput.type = 'password';
        toggleSenha2.classList.remove('bx-hide');
        toggleSenha2.classList.add('bx-show');
      }
    });
  }
});
