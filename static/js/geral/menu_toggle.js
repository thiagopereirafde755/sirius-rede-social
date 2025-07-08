document.addEventListener('DOMContentLoaded', function() {
    // TOGGLE ESQUERDO
    const mobileMenuToggle = document.querySelector('.opcao-mobile1');
    const mobileMenu = document.querySelector('.aside-esquerdo-mobile');
    // TOGGLE DIREITO
    const toggleBtn = document.getElementById('toggleSidebarRight');
    const asideDireitoMobile = document.getElementById('asideDireitoMobile');
    
    if (mobileMenuToggle && mobileMenu) {
        const closeMenu = () => mobileMenu.classList.remove('active');
        const toggleMenu = (e) => {
            e.stopPropagation();
            // FECHA O DIREITO SE ESTIVER ABERTO
            if (asideDireitoMobile && asideDireitoMobile.classList.contains('active')) {
                asideDireitoMobile.classList.remove('active');
            }
            mobileMenu.classList.toggle('active');
        };
        mobileMenuToggle.addEventListener('click', toggleMenu);
        mobileMenu.querySelectorAll('.globalProfile').forEach(item => {
            item.addEventListener('click', closeMenu);
        });
        document.addEventListener('click', function(e) {
            if (mobileMenu.classList.contains('active') && 
                !mobileMenu.contains(e.target) && 
                e.target !== mobileMenuToggle) {
                closeMenu();
            }
        });
        mobileMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    if (toggleBtn && asideDireitoMobile) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            // FECHA O ESQUERDO SE ESTIVER ABERTO
            if (mobileMenu && mobileMenu.classList.contains('active')) {
                mobileMenu.classList.remove('active');
            }
            asideDireitoMobile.classList.add('active');
        });
        document.addEventListener('click', function(e) {
            if (asideDireitoMobile.classList.contains('active') &&
                !asideDireitoMobile.contains(e.target) &&
                e.target !== toggleBtn) {
                asideDireitoMobile.classList.remove('active');
            }
        });
        asideDireitoMobile.addEventListener('click', function(e) {
            if (e.target.closest('a')) {
                asideDireitoMobile.classList.remove('active');
            }
            e.stopPropagation();
        });
    }
});