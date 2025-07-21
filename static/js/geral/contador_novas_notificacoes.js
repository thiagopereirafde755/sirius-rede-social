function atualizarBadgeNotificacao() {
    $.ajax({
        url: "/api/notificacoes_nao_lidas",
        method: "GET",
        dataType: "json",
        cache: false,
        success: function(data) {
            const $badge = $("#badge-notificacao-notify");

            if (data.success && typeof data.total !== "undefined") {
                const total = Number(data.total);

                if (total > 0) {
                    const textoBadge = total > 99 ? "99+" : String(total);
                    if ($badge.text() !== textoBadge) {
                        $badge.text(textoBadge);
                    }
                    $badge.show();
                } else {
                    $badge.hide();
                }
            } else {
                $badge.hide();
            }
        },
        error: function() {
            $("#badge-notificacao-notify").hide();
        }
    });
}

setInterval(atualizarBadgeNotificacao, 3000);
atualizarBadgeNotificacao();
