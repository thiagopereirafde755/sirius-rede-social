    document.addEventListener("DOMContentLoaded", function () {
        const perguntas = document.querySelectorAll('.faq-question');
        
        perguntas.forEach(pergunta => {
            pergunta.addEventListener('click', () => {
                const resposta = pergunta.nextElementSibling;
                if (resposta) {
                    resposta.classList.toggle('active');
                }
            });
        });
    });