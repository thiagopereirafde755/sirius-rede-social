        // Função para pré-visualizar a imagem
        function previewImage(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Exibe a imagem na pré-visualização
                    document.getElementById('preview-image').src = e.target.result;
                    document.getElementById('preview-container-imagem').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        // Função para remover a imagem
        function removeImage() {
            document.getElementById('input-imagem').value = '';  // Limpar o campo de input
            document.getElementById('preview-container-imagem').style.display = 'none';  // Esconder a pré-visualização
        }

        // Função para pré-visualizar o vídeo
        function previewVideo(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Exibe o vídeo na pré-visualização
                    document.getElementById('preview-video-source').src = e.target.result;
                    document.getElementById('preview-video').load();  // Carrega o vídeo no player
                    document.getElementById('preview-container-video').style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        // Função para remover o vídeo
        function removeVideo() {
            document.getElementById('input-video').value = '';  // Limpar o campo de input
            document.getElementById('preview-container-video').style.display = 'none';  // Esconder a pré-visualização
        }