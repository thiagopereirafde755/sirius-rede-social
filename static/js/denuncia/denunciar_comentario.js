document.addEventListener("DOMContentLoaded", () => {
  $('.modal').on('hide.bs.modal', function (e) {
    if (Swal.isVisible()) {
      e.preventDefault();
      Swal.getPopup().focus();
    }
  });

  document.querySelectorAll(".btn-denunciar-comentario").forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();

      const comentarioId = btn.dataset.comentarioId;
      const postId = btn.dataset.postId;
      const modal = btn.closest(".modal");

      $(modal).one("hidden.bs.modal", () => Swal.close());

      Swal.fire({
        title: "Denunciar Comentário",
        target: modal,
        backdrop: false,
        scrollbarPadding: false,
        allowOutsideClick: false,
        allowEscapeKey: false,
        html: `
          <style>
            .swal2-title:after {
              content: "";
              display: block;
              border-top: 1px solid #e0e0e0;
              margin: 15px 0;
            }
            .swal2-actions:before {
              content: "";
              display: block;
              border-top: 1px solid #e0e0e0;
              margin: 20px 0;
              padding-top: 10px;
            }
               .linha-acima-botoes {
        border-top: 1px solid #e0e0e0;
        margin-top: 20px;
        padding-top: 15px;
            }
          </style>
          <div class="form-group text-left">
            <label for="motivo" class="texto-denuncia-comentario">Motivo da denúncia:</label>
            <select class="form-control" id="motivo" required>
              <option value="">Selecione um motivo</option>
              <option value="odio">Ódio</option>
              <option value="abuso e assedio">Abuso e assédio</option>
              <option value="discurso violento">Discurso violento</option>
              <option value="segurança infantil">Segurança infantil</option>
              <option value="privacidade">Privacidade</option>
              <option value="spam">Spam</option>
              <option value="suicidio ou automutilacao">Suicídio ou automutilação</option>
              <option value="midia sensível">Exposição a mídia sensível</option>
              <option value="falsa Identidade">Falsa Identidade</option>
              <option value="conteudo violento">Conteúdo violento</option>
              <option value="outros">Outros</option>
            </select>
          </div>
          <div class="form-group text-left">
            <label for="detalhes" class="texto-denuncia-comentario">Detalhes (opcional):</label>
            <textarea class="form-control" id="detalhes" rows="3" maxlength="80"
                      placeholder="Descreva melhor a denúncia" style="resize:none;"></textarea>
            <small id="contadorDetalhesComentario" class="form-text text-muted">0/80</small>
          </div>
           <div class="linha-acima-botoes"></div>
        `,
        showCancelButton: true,
        confirmButtonText: "Enviar denúncia",
        cancelButtonText: "Cancelar",
        focusConfirm: false,
        customClass: {
          popup: 'swal2-popup-custom',
          title: 'swal2-title-custom',
          actions: 'swal2-actions-custom'
        },

        didOpen: () => {
          const txt = document.getElementById("detalhes");
          const cnt = document.getElementById("contadorDetalhesComentario");
          txt.addEventListener("input", () => {
            cnt.textContent = `${txt.value.length}/80`;
          });
          document.getElementById("motivo").focus();
        },

        preConfirm: () => {
          const motivo = document.getElementById("motivo").value;
          const detalhes = document.getElementById("detalhes").value;
          
          if (!motivo) {
            Swal.showValidationMessage("Por favor, selecione um motivo");
            return false;
          }

          return fetch("/denunciar_comentario", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
              comentario_id: comentarioId,
              post_id: postId,
              motivo,
              detalhes
            })
          })
          .then(async r => {
            const data = await r.json();
            if (!r.ok) throw new Error(data.message || "Erro desconhecido");
            return data;
          })
          .catch(err => {
            Swal.showValidationMessage(`Erro: ${err.message}`);
            return false;
          });
        },

        willClose: () => {
          // Remove container do SweetAlert do modal para evitar reaparecer
          const sc = modal.querySelector(".swal2-container");
          if (sc) sc.remove();
        }
      })
      .then(res => {
        if (res.isConfirmed) {
          Swal.fire({
            icon: "success",
            title: "Enviado!",
            text: "Denúncia enviada. Obrigado por ajudar a manter a comunidade segura!",
            timer: 2000,
            showConfirmButton: false
          });
        }
      });
    });
  });
});