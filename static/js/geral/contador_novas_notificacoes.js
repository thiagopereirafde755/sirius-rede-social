 function atualizarBadgeNotificacao() {
    $.ajax({
        url: "/api/notificacoes_nao_lidas",
        method: "GET",
        dataType: "json",
        cache: false,
        success: function(data) {
            if (data.success && typeof data.nao_lidas !== "undefined") {
                let totalNaoLidas = data.nao_lidas;
                if (totalNaoLidas > 0) {
                    $("#badge-notificacao-notify")
                      .text(totalNaoLidas > 99 ? "99+" : totalNaoLidas)
                      .show();
                } else {
                    $("#badge-notificacao-notify").hide();
                }
            } else {
                $("#badge-notificacao-notify").hide();
            }
        },
        error: function() {
            $("#badge-notificacao-notify").hide();
        }
    });
}

setInterval(atualizarBadgeNotificacao, 3000);
atualizarBadgeNotificacao();