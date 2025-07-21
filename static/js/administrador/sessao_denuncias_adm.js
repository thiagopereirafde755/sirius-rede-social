const statusPossiveis = ['pendente', 'em_analise', 'resolvido', 'ignorado'];

function popularSelect(selectEl, statusAtual) {
  selectEl.innerHTML = ''; 

  statusPossiveis.forEach(st => {
    const option = document.createElement('option');
    option.value = st;
    option.textContent = st.charAt(0).toUpperCase() + st.slice(1).replace('_', ' ');
    if (st === statusAtual) {
      option.selected = true;
    }
    selectEl.appendChild(option);
  });
}

document.querySelectorAll('.btn-edit').forEach(btn => {
  btn.addEventListener('click', function () {
    const id             = this.dataset.id;
    const tipo           = this.dataset.tipo;
    const denunciante    = this.dataset.denunciante;
    const id_alvo        = this.dataset.id_alvo;
    const motivo         = this.dataset.motivo;
    const descricao      = this.dataset.descricao;
    const data_denuncia  = this.dataset.data_denuncia;
    const statusAtual    = this.dataset.status;

    document.getElementById('modal-id').textContent            = id;
    document.getElementById('modal-tipo').textContent          = tipo;
    document.getElementById('modal-denunciante').textContent   = denunciante;
    document.getElementById('modal-id_alvo').textContent       = id_alvo;
    document.getElementById('modal-motivo').textContent        = motivo;
    document.getElementById('modal-descricao').textContent     = descricao;
    document.getElementById('modal-data_denuncia').textContent = data_denuncia;
    document.getElementById('modal-status').textContent        = statusAtual;

    const selectStatus = document.getElementById('modal-novo-status');
    selectStatus.disabled = false;
    popularSelect(selectStatus, statusAtual);

    selectStatus.dataset.denunciaId = id;

    const modal = new bootstrap.Modal(document.getElementById('modalDetalhesDenuncia'));
    modal.show();
  });
});

document.getElementById('btn-salvar-status').addEventListener('click', function () {
  const selectStatus = document.getElementById('modal-novo-status');
  const novoStatus   = selectStatus.value;
  const denunciaId   = selectStatus.dataset.denunciaId;

  if (!novoStatus) {
    Swal.fire('Erro', 'Selecione um novo status.', 'error');
    return;
  }

  Swal.fire({
    title: 'Enviando e-mail...',
    text: 'Por favor, aguarde.',
    allowOutsideClick: false,
    didOpen: () => Swal.showLoading(),
  });

  fetch('/alterar_status_denuncia', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: denunciaId, novo_status: novoStatus }),
  })
    .then(res => res.json())
    .then(data => {
      Swal.close(); 

      if (data.sucesso) {
        const celula = document.querySelector(`#denuncia-row-${denunciaId} .status-col`);
        if (celula) celula.textContent = novoStatus;

        document.getElementById('modal-status').textContent = novoStatus;

        popularSelect(selectStatus, novoStatus);
        selectStatus.dataset.denunciaId = denunciaId;

        Swal.fire('Sucesso', 'Status alterado e e-mail enviado!', 'success');
      } else {
        Swal.fire('Erro', data.mensagem || 'Erro ao alterar status.', 'error');
      }
    })
    .catch(() => {
      Swal.close();
      Swal.fire('Erro', 'Erro de comunicação com o servidor.', 'error');
    });
});
