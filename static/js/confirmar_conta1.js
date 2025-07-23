// Elementos
let countdown = 60;
const linkReenviar = document.getElementById('reenviar-codigo');
const contadorTempo = document.getElementById('contador-tempo');

// Verifica se há contador salvo ao carregar a página
function verificarContador() {
    const fim = localStorage.getItem('tempoFim');
    if (fim) {
        const tempoRestante = Math.floor((new Date(fim) - new Date()) / 1000);
        if (tempoRestante > 0) {
            iniciarContador(tempoRestante);
        } else {
            localStorage.removeItem('tempoFim');
        }
    }
}

// Inicia o contador de 60s (ou tempo personalizado)
function iniciarContador(tempo = 60) {
    countdown = tempo;
    const tempoFim = new Date(new Date().getTime() + tempo * 1000);
    localStorage.setItem('tempoFim', tempoFim);

    linkReenviar.style.pointerEvents = 'none';
    linkReenviar.style.opacity = '0.5';
    contadorTempo.style.display = 'inline';

    const interval = setInterval(() => {
        countdown--;
        contadorTempo.textContent = `(${countdown}s)`;

        if (countdown <= 0) {
            clearInterval(interval);
            contadorTempo.style.display = 'none';
            linkReenviar.style.pointerEvents = 'auto';
            linkReenviar.style.opacity = '1';
            localStorage.removeItem('tempoFim');
        }
    }, 1000);
}

// Evento de clique no link "Reenviar código"
linkReenviar.addEventListener('click', function (e) {
    e.preventDefault();

    Swal.fire({
        title: 'Reenviar Código',
        text: 'Deseja receber um novo código de confirmação?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sim, reenviar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#a76ab6',
        cancelButtonColor: '#6c757d',
        background: '#2d2a32',
        color: '#e0e0e0'
    }).then((result) => {
        if (result.isConfirmed) {
            iniciarContador();

            let timerInterval;
            Swal.fire({
                title: 'Enviando novo código...',
                html: 'Por favor, aguarde <b></b> segundos',
                timer: 10000,
                timerProgressBar: true,
                background: '#2d2a32',
                color: '#e0e0e0',
                didOpen: () => {
                    Swal.showLoading();
                    const b = Swal.getHtmlContainer().querySelector('b');
                    timerInterval = setInterval(() => {
                        b.textContent = (Swal.getTimerLeft() / 1000).toFixed(0);
                    }, 100);
                },
                willClose: () => {
                    clearInterval(timerInterval);
                }
            });

            fetch('/reenviar_codigo_confirmar_conta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
                .then(response => response.json())
                .then(data => {
                    Swal.close();

                    if (data.success) {
                        Swal.fire({
                            title: 'Código Reenviado!',
                            text: 'Um novo código foi enviado para seu e-mail',
                            icon: 'success',
                            confirmButtonColor: '#a76ab6',
                            background: '#2d2a32',
                            color: '#e0e0e0'
                        });
                    } else {
                        Swal.fire({
                            title: 'Erro',
                            text: data.message || 'Falha ao reenviar o código',
                            icon: 'error',
                            confirmButtonColor: '#a76ab6',
                            background: '#2d2a32',
                            color: '#e0e0e0'
                        });
                    }
                })
                .catch(() => {
                    Swal.close();
                    Swal.fire({
                        title: 'Erro',
                        text: 'Ocorreu um erro durante o processamento',
                        icon: 'error',
                        confirmButtonColor: '#a76ab6',
                        background: '#2d2a32',
                        color: '#e0e0e0'
                    });
                });
        }
    });
});

// Submissão do formulário de confirmação
document.getElementById("confirmForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const codigo = document.getElementById("codigo").value.trim();

    if (!codigo) {
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: 'Por favor, insira o código de confirmação',
            confirmButtonColor: '#a76ab6',
            background: '#2d2a32',
            color: '#e0e0e0'
        });
        return;
    }

    fetch("/confirmar_conta/part1", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ codigo })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Conta confirmada!',
                    text: 'Redirecionando...',
                    confirmButtonColor: '#a76ab6',
                    background: '#2d2a32',
                    color: '#e0e0e0',
                    timer: 2000,
                    showConfirmButton: false
                }).then(() => {
                    window.location.href = data.redirect;
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Erro',
                    text: data.message,
                    confirmButtonColor: '#a76ab6',
                    background: '#2d2a32',
                    color: '#e0e0e0'
                });
            }
        })
        .catch(() => {
            Swal.fire({
                icon: 'error',
                title: 'Erro',
                text: 'Erro ao verificar o código.',
                confirmButtonColor: '#a76ab6',
                background: '#2d2a32',
                color: '#e0e0e0'
            });
        });
});

// Inicia o contador se ele já estiver em andamento ao abrir a página
verificarContador();
