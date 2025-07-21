let audioEnabled = false;

function liberarAudio() {
    audioEnabled = true;
    window.removeEventListener('click', liberarAudio);
}

window.addEventListener('click', liberarAudio);

function tocarAudioNotificacao() {
    if (!audioEnabled) return;
    let audio = document.getElementById('badge-audio');
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(() => {});
    }
}

let lastCounts = {};

function atualizarBadges() {
    fetch('/api/nao_vistas')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelectorAll('.contact-item').forEach(function(item) {
                    let contatoId = item.querySelector('a').href.match(/(\d+)$/);
                    if (!contatoId) return;
                    contatoId = contatoId[1];
                    let badge = item.querySelector('.badge-nao-vistas');
                    let count = data.counts[contatoId] || 0;
                    let usernameBadge = item.querySelector('.username-badge');

                    if (lastCounts[contatoId] !== undefined && count > lastCounts[contatoId]) {
                        tocarAudioNotificacao();
                    }
                    lastCounts[contatoId] = count;

                    if (count > 0) {
                        if (badge) {
                            badge.textContent = count;
                        } else if (usernameBadge) {
                            let badgeEl = document.createElement('span');
                            badgeEl.className = 'badge-nao-vistas';
                            badgeEl.textContent = count;
                            usernameBadge.appendChild(badgeEl);
                        }
                    } else if (badge) {
                        badge.remove();
                    }
                });
            }
        });
}
setInterval(atualizarBadges, 2000);
window.addEventListener('DOMContentLoaded', atualizarBadges);