document.addEventListener('DOMContentLoaded', function() {
  const banner = document.getElementById('cookie-banner');
  const overlay = document.getElementById('cookie-overlay');
  const acceptBtn = document.getElementById('accept-cookies-btn');
  const body = document.body;
  const html = document.documentElement;

  function abrirBanner() {
    banner.style.display = 'block';
    overlay.style.display = 'block';
    body.classList.add('no-scroll');
    html.classList.add('no-scroll');
  }

  function fecharBanner() {
    banner.style.display = 'none';
    overlay.style.display = 'none';
    body.classList.remove('no-scroll');
    html.classList.remove('no-scroll');
  }

  if (!localStorage.getItem('cookiesAccepted')) {
    abrirBanner();
  }

  acceptBtn.addEventListener('click', function() {
    localStorage.setItem('cookiesAccepted', 'true');
    fecharBanner();
  });
});
