// Seleciona os elementos do DOM
const fotoInput = document.getElementById('foto');
const videoInput = document.getElementById('video');
const previewContainer = document.getElementById('preview-container');
const form = document.getElementById('form-enviar-mensagem');

// Adiciona event listeners para os inputs de arquivo
fotoInput.addEventListener('change', function(event) {
    mostrarPreview(event.target.files[0]);
});

videoInput.addEventListener('change', function(event) {
    mostrarPreview(event.target.files[0]);
});

// Função para mostrar o preview da mídia selecionada
function mostrarPreview(file) {
    // Limpa qualquer preview anterior
    previewContainer.innerHTML = '';
    
    // Se um arquivo foi selecionado
    if (file) {
        // Mostra o container de preview
        previewContainer.style.display = 'flex';
        
        const tipo = file.type;
        const url = URL.createObjectURL(file);

        // Cria o wrapper do preview
        const previewWrapper = document.createElement('div');
        previewWrapper.classList.add('preview-wrapper');

        // Cria o botão para fechar o preview
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '✖';
        closeButton.classList.add('close-button');
        closeButton.onclick = function() {
            previewContainer.innerHTML = '';
            previewContainer.style.display = 'none';
            fotoInput.value = '';
            videoInput.value = '';
        };

        // Cria o elemento de mídia apropriado (imagem ou vídeo)
        if (tipo.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = url;
            img.classList.add('preview-img');
            previewWrapper.appendChild(img);
        } else if (tipo.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = url;
            video.controls = true;
            video.classList.add('preview-video');
            previewWrapper.appendChild(video);
        }

        // Adiciona o botão de fechar e o wrapper ao container
        previewWrapper.appendChild(closeButton);
        previewContainer.appendChild(previewWrapper);
    } else {
        // Esconde o container se nenhum arquivo foi selecionado
        previewContainer.style.display = 'none';
    }
}

// Limpa o preview quando o formulário é enviado
form.addEventListener('submit', function() {
    previewContainer.innerHTML = '';
    previewContainer.style.display = 'none';
});

