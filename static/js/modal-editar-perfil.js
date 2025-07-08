const modal = document.getElementById("modal-editar-perfil");
const btnEditarPerfil = document.getElementById("editar-perfil-btn");
const closeBtn = document.getElementsByClassName("close-btn")[0];

// Abrir o modal
btnEditarPerfil.onclick = function() {
    modal.style.display = "flex";
    document.body.style.overflow = "hidden"; // Bloquear rolagem
}

// Fechar o modal com o botão de fechar
closeBtn.onclick = function() {
    modal.style.display = "none";
    document.body.style.overflow = "auto"; // Restaurar rolagem
}

// Fechar o modal se clicar fora dele
window.onclick = function(event) {
    if (event.target === modal) {
        modal.style.display = "none";
        document.body.style.overflow = "auto"; // Restaurar rolagem
    }
}
