document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("infoAmizad");
    if (!btn) return;

    btn.addEventListener("click", (e) => {
        e.preventDefault();                   // impede navegação do <a>

        // ─── pega a data que veio do atributo data-amizade ───
        const dataAmizadeStr = btn.dataset.amizade || window.DATA_AMIZADE;

        if (!dataAmizadeStr) {
            Swal.fire("Erro",
                      "Não foi possível calcular o tempo de amizade.",
                      "error");
            return;
        }

        const dataAmizade = new Date(dataAmizadeStr);
        if (isNaN(dataAmizade)) {
            Swal.fire("Erro", "Data inválida.", "error");
            return;
        }

        const diff  = Date.now() - dataAmizade.getTime();
        const dias  = Math.floor(diff / 8.64e7);     // 1000 × 60 × 60 × 24
        const anos  = Math.floor(dias / 365);
        const meses = Math.floor((dias % 365) / 30);
        const diasR = (dias % 365) % 30;

        let tempo = "";
        if (anos)  tempo += `${anos} ano${anos  > 1 ? "s" : ""} `;
        if (meses) tempo += `${meses} mês${meses > 1 ? "es" : ""} `;
        if (diasR) tempo += `${diasR} dia${diasR > 1 ? "s" : ""}`;
        if (!tempo) tempo = "0 dia";

        Swal.fire({
            icon: "info",
            title: "Tempo de amizade",
            html: `Vocês são amigos há <strong>${tempo.trim()}</strong>.`,
            confirmButtonText: "Legal!"
        });
    });
});
