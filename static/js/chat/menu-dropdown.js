function toggleDropdown(button) {
  // Fecha todos os outros menus primeiro
  document.querySelectorAll('.dropdown-menu').forEach(menu => {
      if (menu !== button.nextElementSibling) {
          menu.style.display = 'none';
      }
  });
  
  // Alterna o menu atual
  const menu = button.nextElementSibling;
  menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

document.addEventListener('click', function(e) {
  if (!e.target.matches('.options-btn')) {
      document.querySelectorAll('.dropdown-menu').forEach(menu => {
          menu.style.display = 'none';
      });
  }
});

    // Adicione ao final do seu HTML ou em um arquivo JS importado
function toggleHeaderDropdown(event) {
    event.stopPropagation();
    var menu = document.getElementById('headerDropdownMenu');
    menu.classList.toggle('show');

    // Fecha dropdown ao clicar fora
    document.addEventListener('click', function handler(e) {
        if (!menu.contains(e.target) && !event.target.contains(e.target)) {
            menu.classList.remove('show');
            document.removeEventListener('click', handler);
        }
    });
}