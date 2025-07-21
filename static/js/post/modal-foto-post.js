document.querySelectorAll('.foto-post').forEach(function(img) {
    img.addEventListener('click', function() {
        var modalImage = document.getElementById('modal-image');
        modalImage.src = this.src; 
        $('#imageModal').modal('show'); 
    });
});