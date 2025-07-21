function toggleDropdown(button) {
  document.querySelectorAll('.dropdown-menu').forEach(menu => {
      if (menu !== button.nextElementSibling) {
          menu.style.display = 'none';
      }
  });
  
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

function toggleHeaderDropdown(event) {
    event.stopPropagation();
    var menu = document.getElementById('headerDropdownMenu');
    menu.classList.toggle('show');

    document.addEventListener('click', function handler(e) {
        if (!menu.contains(e.target) && !event.target.contains(e.target)) {
            menu.classList.remove('show');
            document.removeEventListener('click', handler);
        }
    });
}