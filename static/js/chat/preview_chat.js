document.addEventListener("DOMContentLoaded", function () {
    // Seleciona os elementos do DOM
    const fotoInput = document.getElementById('foto');
    const videoInput = document.getElementById('video');
    const previewContainer = document.getElementById('preview-container');
    const form = document.getElementById('form-enviar-mensagem');

    // Função para mostrar alerta de erro com SweetAlert
    function mostrarErro(titulo, texto) {
        Swal.fire({
            icon: 'error',
            title: titulo,
            text: texto,
        });
    }

    // Função para mostrar o preview da mídia selecionada
    function mostrarPreview(file, tipoInput) {
        previewContainer.innerHTML = '';

        if (file) {
            // Valida tamanho do arquivo
            if (file.type.startsWith('image/') && file.size > 10 * 1024 * 1024) {
                mostrarErro('Arquivo muito grande', 'A imagem deve ter no máximo 10MB.');
                if (tipoInput === 'foto') fotoInput.value = '';
                if (tipoInput === 'video') videoInput.value = '';
                previewContainer.style.display = 'none';
                return;
            }
            if (file.type.startsWith('video/') && file.size > 10 * 1024 * 1024) {
                mostrarErro('Arquivo muito grande', 'O vídeo deve ter no máximo 10MB.');
                if (tipoInput === 'foto') fotoInput.value = '';
                if (tipoInput === 'video') videoInput.value = '';
                previewContainer.style.display = 'none';
                return;
            }

            // Mostra o container de preview
            previewContainer.style.display = 'flex';

            const url = URL.createObjectURL(file);

            // Cria o wrapper do preview
            const previewWrapper = document.createElement('div');
            previewWrapper.classList.add('preview-wrapper');

            // Cria o botão para fechar o preview
            const closeButton = document.createElement('button');
            closeButton.innerHTML = '✖';
            closeButton.classList.add('close-button');
            closeButton.type = 'button';
            closeButton.title = 'Remover arquivo selecionado';
            closeButton.onclick = function () {
                previewContainer.innerHTML = '';
                previewContainer.style.display = 'none';
                fotoInput.value = '';
                videoInput.value = '';
            };

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = url;
                img.classList.add('preview-img');
                previewWrapper.appendChild(img);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.src = url;
                video.controls = true;
                video.classList.add('preview-video');
                previewWrapper.appendChild(video);
            }

            previewWrapper.appendChild(closeButton);
            previewContainer.appendChild(previewWrapper);
        } else {
            previewContainer.style.display = 'none';
        }
    }

    if (fotoInput) {
        fotoInput.addEventListener('change', function (event) {
            mostrarPreview(event.target.files[0], 'foto');
        });
    }
    if (videoInput) {
        videoInput.addEventListener('change', function (event) {
            mostrarPreview(event.target.files[0], 'video');
        });
    }

    if (form) {
        form.addEventListener('submit', function () {
            previewContainer.innerHTML = '';
            previewContainer.style.display = 'none';
            fotoInput.value = '';
            videoInput.value = '';
        });
    }
});
