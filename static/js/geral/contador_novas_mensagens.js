    function atualizarBadgeChat() {
    $.ajax({
        url: "/api/nao_vistas",
        method: "GET",
        dataType: "json",
        cache: false,
        success: function(data) {
            if (data.success && data.counts) {
                let totalNaoVistas = 0;
                for (let id in data.counts) {
                    totalNaoVistas += data.counts[id];
                }
                if (totalNaoVistas > 0) {
                    $("#badge-chat-notify")
                      .text(totalNaoVistas > 99 ? "99+" : totalNaoVistas)
                      .show();
                } else {
                    $("#badge-chat-notify").hide();
                }
            } else {
                $("#badge-chat-notify").hide();
            }
        },
        error: function() {
            $("#badge-chat-notify").hide();
        }
    });
}

setInterval(atualizarBadgeChat, 3000);
atualizarBadgeChat();