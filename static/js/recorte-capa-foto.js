document.addEventListener('DOMContentLoaded', function() {
    // =============================================
    //  MODAL DE RECORTAR FOTO DE CAPA
    //  ============================================= 
    (function() {
        const uploadInput = document.getElementById('upload-capa');
        const cropModal = document.getElementById('crop-modal');
        const imageToCrop = document.getElementById('image-to-crop');
        const cancelCrop = document.getElementById('cancel-crop');
        const saveCrop = document.getElementById('save-crop');
        const croppedImageInput = document.getElementById('cropped-image');
        const form = document.getElementById('capa-form');
        let cropper;

        function initCropper() {
            if (cropper) {
                cropper.destroy();
            }
            
            cropper = new Cropper(imageToCrop, {
                aspectRatio: 16 / 9,
                viewMode: 1,
                autoCropArea: 0.8,
                responsive: true,
                guides: true
            });
        }

        function handleFileSelect(e) {
            if (e.target.files.length === 0) return;
            
            const file = e.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function(event) {
                imageToCrop.src = event.target.result;
                cropModal.style.display = 'block';
                
                imageToCrop.onload = initCropper;
            };
            
            reader.readAsDataURL(file);
        }

        function saveCroppedImage() {
            if (!cropper) return;

            const canvas = cropper.getCroppedCanvas({
                width: 1200,
                height: 675,
                minWidth: 800,
                minHeight: 450,
                maxWidth: 2000,
                maxHeight: 1125,
                fillColor: '#fff',
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });
            
            if (canvas) {
                croppedImageInput.value = canvas.toDataURL('image/jpeg', 0.9);
                form.submit();
            }
        }

        function cancelCropAction() {
            cropModal.style.display = 'none';
            uploadInput.value = '';
            if (cropper) {
                cropper.destroy();
                cropper = null;
            }
        }

        // Event listeners
        uploadInput.addEventListener('change', handleFileSelect);
        cancelCrop.addEventListener('click', cancelCropAction);
        saveCrop.addEventListener('click', saveCroppedImage);
    })();

    // =============================================
    //  MODAL DE RECORTAR FOTO DE PERFIL
    //  ============================================= 
    (function() {
        const uploadFotoPerfil = document.getElementById('upload-foto-perfil');
        const cropModalPerfil = document.getElementById('crop-modal-perfil');
        const imageToCropPerfil = document.getElementById('image-to-crop-perfil');
        const cancelCropPerfil = document.getElementById('cancel-crop-perfil');
        const saveCropPerfil = document.getElementById('save-crop-perfil');
        const croppedImageInputPerfil = document.getElementById('cropped-image-perfil');
        const formFotoPerfil = document.getElementById('foto-perfil-form');
        let cropperPerfil;

        function initCropperPerfil() {
            if (cropperPerfil) {
                cropperPerfil.destroy();
            }
            
            cropperPerfil = new Cropper(imageToCropPerfil, {
                aspectRatio: 1,
                viewMode: 1,
                autoCropArea: 0.8,
                responsive: true,
                guides: true
            });
        }

        function handleFileSelectPerfil(e) {
            if (e.target.files.length === 0) return;
            
            const file = e.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function(event) {
                imageToCropPerfil.src = event.target.result;
                cropModalPerfil.style.display = 'block';
                
                imageToCropPerfil.onload = initCropperPerfil;
            };
            
            reader.readAsDataURL(file);
        }

        function saveCroppedImagePerfil() {
            if (!cropperPerfil) return;

            const canvas = cropperPerfil.getCroppedCanvas({
                width: 500,
                height: 500,
                minWidth: 200,
                minHeight: 200,
                maxWidth: 1000,
                maxHeight: 1000,
                fillColor: '#fff',
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });
            
            if (canvas) {
                croppedImageInputPerfil.value = canvas.toDataURL('image/jpeg', 0.9);
                formFotoPerfil.submit();
            }
        }

        function cancelCropActionPerfil() {
            cropModalPerfil.style.display = 'none';
            uploadFotoPerfil.value = '';
            if (cropperPerfil) {
                cropperPerfil.destroy();
                cropperPerfil = null;
            }
        }

        // ** REMOVIDO EVENT LISTENER DE CLICK FORA PARA NÃO FECHAR O MODAL **

        // Event listeners
        uploadFotoPerfil.addEventListener('change', handleFileSelectPerfil);
        cancelCropPerfil.addEventListener('click', cancelCropActionPerfil);
        saveCropPerfil.addEventListener('click', saveCroppedImagePerfil);
        // NÃO ADICIONA EVENT LISTENER DE CLICK NO MODAL PARA FECHAR AO CLICAR FORA
    })();
});
