document.addEventListener("DOMContentLoaded", function () {
    // Função para mostrar alerta de erro com SweetAlert
    function mostrarErro(titulo, texto) {
        Swal.fire({
            icon: 'error',
            title: titulo,
            text: texto,
        });
    }

    // Função para gerar o preview da mídia
    function previewMedia(input, type) {
        const previewContainer = document.getElementById('previewContainer');

        // Remove previews existentes do mesmo tipo
        const existingItems = previewContainer.querySelectorAll('.preview-item');
        existingItems.forEach(item => {
            if ((type === 'image' && item.querySelector('.preview-image')) ||
                (type === 'video' && item.querySelector('.preview-video'))) {
                previewContainer.removeChild(item);
            }
        });

        if (input.files && input.files[0]) {
            const file = input.files[0];

            // Validação do tamanho do arquivo
            if (type === 'image' && file.size > 10 * 1024 * 1024) { // 10MB
                mostrarErro('Arquivo muito grande', 'A imagem deve ter no máximo 10MB.');
                input.value = '';
                return;
            }
            if (type === 'video' && file.size > 10 * 1024 * 1024) { // 10MB
                mostrarErro('Arquivo muito grande', 'O vídeo deve ter no máximo 10MB.');
                input.value = '';
                return;
            }

            const reader = new FileReader();

            reader.onload = function (e) {
                const previewItem = document.createElement('div');
                previewItem.className = 'preview-item';

                let mediaElement;
                if (type === 'image') {
                    mediaElement = document.createElement('img');
                    mediaElement.className = 'preview-image';
                    mediaElement.src = e.target.result;
                } else {
                    mediaElement = document.createElement('video');
                    mediaElement.className = 'preview-video';
                    mediaElement.src = e.target.result;
                    mediaElement.controls = true;
                }

                const removeButton = document.createElement('button');
                removeButton.className = 'remove-preview';
                removeButton.type = 'button';
                removeButton.innerHTML = '×';
                removeButton.title = 'Remover arquivo selecionado';
                removeButton.onclick = function () {
                    previewContainer.removeChild(previewItem);
                    input.value = ''; // Limpa o input file
                };

                previewItem.appendChild(mediaElement);
                previewItem.appendChild(removeButton);
                previewContainer.appendChild(previewItem);
            };

            reader.readAsDataURL(file);
        }
    }

    // Associa os eventos onchange dos inputs
    const inputImagem = document.getElementById('input-imagem');
    const inputVideo = document.getElementById('input-video');

    if (inputImagem) {
        inputImagem.addEventListener('change', function () {
            previewMedia(this, 'image');
        });
    }

    if (inputVideo) {
        inputVideo.addEventListener('change', function () {
            previewMedia(this, 'video');
        });
    }

    // Limpar previews ao enviar o formulário
    const form = document.querySelector('form[action="/adicionar_postagem"]');
    if (form) {
        form.addEventListener('submit', function () {
            document.getElementById('previewContainer').innerHTML = '';
        });
    }
});