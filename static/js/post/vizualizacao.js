document.addEventListener("DOMContentLoaded", function () {
    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const postDiv = entry.target;
                const postId = postDiv.getAttribute('data-post-id');

                fetch("/marcar_visualizacao", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ post_id: postId })
                });

                obs.unobserve(postDiv); // evita marcar mais de uma vez
            }
        });
    }, {
        threshold: 0.6
    });

    document.querySelectorAll(".post").forEach(post => {
        observer.observe(post);
    });
});

function explicarVisualizacoes() {
    Swal.fire({
        title: 'Visualizações',
        html: 'Vezes que este post foi visto.',
        icon: 'info',
        confirmButtonText: 'Entendi'
    });
}