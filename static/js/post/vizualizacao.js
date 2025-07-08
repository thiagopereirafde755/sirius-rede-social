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
        html: 'Vezes que este post foi visto. Para saber mais, consulte a <a href="/central-de-ajuda" target="_blank" style="color: #3b7ddd; text-decoration: underline;">Central de Ajuda</a>.',
        icon: 'info',
        confirmButtonText: 'Entendi'
    });
}