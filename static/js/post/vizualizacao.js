document.addEventListener("DOMContentLoaded", function () {
    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const postDiv = entry.target;
                const postId = postDiv.getAttribute('data-post-id');

                // Marca visualização ao entrar na tela (apenas uma vez)
                fetch("/marcar_visualizacao", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ post_id: postId })
                });

                obs.unobserve(postDiv);
            }
        });
    }, { threshold: 0.6 });

    document.querySelectorAll(".post").forEach(post => {
        observer.observe(post);

        const video = post.querySelector('video');
        if (video) {
            let podeContarVisualizacao = false;

            // Quando o vídeo termina, habilita contar nova visualização no próximo play
            video.addEventListener('ended', () => {
                podeContarVisualizacao = true;
            });

            // Quando o vídeo começa a rodar
            video.addEventListener('play', () => {
                if (podeContarVisualizacao) {
                    const postId = post.getAttribute('data-post-id');
                    fetch("/marcar_visualizacao", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ post_id: postId })
                    });
                    podeContarVisualizacao = false; // reseta a flag
                }
            });
        }
    });
});

// Função para exibir explicação das visualizações
function explicarVisualizacoes() {
    Swal.fire({
        title: 'Visualizações',
        html: 'Vezes que este post foi visto.',
        icon: 'info',
        confirmButtonText: 'Entendi'
    });
}
