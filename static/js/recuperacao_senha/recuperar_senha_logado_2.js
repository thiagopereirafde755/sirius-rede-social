const TEMPO_ESPERA = 60;             
const CHAVE_STORAGE = "tempoReenvioCodigo";

const btn        = document.getElementById("reenviarCodigo");
const timerSpan  = document.getElementById("timer");
const REENVIAR_URL = window.REENVIAR_URL;  

function iniciarTimer(segundosRestantes) {
    btn.disabled = true;
    const intervalo = setInterval(() => {
        segundosRestantes--;
        timerSpan.textContent = segundosRestantes + "s";

        if (segundosRestantes <= 0) {
            clearInterval(intervalo);
            btn.disabled = false;
            timerSpan.textContent = "";
            localStorage.removeItem(CHAVE_STORAGE);
        }
    }, 1000);
}

export function reenviarCodigo() {       
    Swal.fire({
        title: 'Reenviando código...',
        text:  'Por favor, aguarde.',
        allowOutsideClick: false,
        allowEscapeKey:   false,
        didOpen: () => {
            Swal.showLoading();

            fetch(REENVIAR_URL, {
                method:  "POST",
                headers: { "Content-Type": "application/json" }
            })
            .then(res => {
                if (!res.ok) throw new Error("Erro ao reenviar código");
                return res.text();
            })
            .then(() => {
                Swal.close();
                Swal.fire('Sucesso!', 'Código reenviado para seu e‑mail.', 'success');
                const dataExpiracao = Date.now() + TEMPO_ESPERA * 1000;
                localStorage.setItem(CHAVE_STORAGE, dataExpiracao);
                iniciarTimer(TEMPO_ESPERA);
            })
            .catch(() => {
                Swal.close();
                Swal.fire('Erro', 'Não foi possível reenviar o código. Tente novamente.', 'error');
                btn.disabled = false;
                timerSpan.textContent = "";
                localStorage.removeItem(CHAVE_STORAGE);
            });
        }
    });
}

window.addEventListener("DOMContentLoaded", () => {
    const expiracao = localStorage.getItem(CHAVE_STORAGE);
    if (expiracao) {
        const tempoRestante = Math.floor((+expiracao - Date.now()) / 1000);
        if (tempoRestante > 0) iniciarTimer(tempoRestante);
        else localStorage.removeItem(CHAVE_STORAGE);
    }

    if (btn) btn.addEventListener("click", reenviarCodigo);
});
