function previewMedia(input, type) {
    const previewContainer = document.getElementById('previewContainer');
    
    // Remove qualquer preview existente do mesmo tipo
    const existingItems = previewContainer.querySelectorAll('.preview-item');
    existingItems.forEach(item => {
        if ((type === 'image' && item.querySelector('.preview-image')) || 
            (type === 'video' && item.querySelector('.preview-video'))) {
            previewContainer.removeChild(item);
        }
    });

    if (input.files && input.files[0]) {
        const file = input.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            // Criar elemento de preview
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            
            // Criar elemento de mídia baseado no tipo
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
            
            // Botão para remover o preview
            const removeButton = document.createElement('button');
            removeButton.className = 'remove-preview';
            removeButton.innerHTML = '×';
            removeButton.onclick = function() {
                previewContainer.removeChild(previewItem);
                input.value = ''; // Limpa o input file
            };
            
            // Adiciona elementos ao container de preview
            previewItem.appendChild(mediaElement);
            previewItem.appendChild(removeButton);
            previewContainer.appendChild(previewItem);
        };
        
        reader.readAsDataURL(file);
    }
}

// Limpar previews ao enviar o formulário
document.querySelector('form').addEventListener('submit', function() {
    document.getElementById('previewContainer').innerHTML = '';
});