window.onload = function() {
    let navType = "navigate"; 

    if (performance.getEntriesByType) {
        const perfEntries = performance.getEntriesByType("navigation");
        if (perfEntries.length > 0) {
            navType = perfEntries[0].type;
        }
    } else if (performance.navigation) {
        const nav = performance.navigation.type;
        navType = nav === 1 ? "reload" : (nav === 2 ? "back_forward" : "navigate");
    }

    const loading = document.getElementById('loadingScreen');
    const jaCarregou = sessionStorage.getItem('page_loaded_before');

    // **Nova verificação para pular o loading só uma vez**
    const pularLoadingUmaVez = sessionStorage.getItem('pular_loading_uma_vez') === 'true';

    function mostrarLoading() {
        loading.style.display = 'flex';
        document.body.style.overflow = 'hidden'; 
        setTimeout(() => {
            loading.style.display = 'none';
            document.body.style.overflow = 'auto'; 
        }, 1500);
    }

    if (pularLoadingUmaVez) {
        // Se a flag estiver setada, pula o loading uma vez e remove a flag
        sessionStorage.removeItem('pular_loading_uma_vez');
        loading.style.display = 'none';
        document.body.style.overflow = 'auto';
        return; 
    }

    if (!jaCarregou) {
        // Primeira vez que entra na página - mostra loading
        mostrarLoading();
        sessionStorage.setItem('page_loaded_before', 'true');

    } else if (navType === 'reload') {
        // Recarregou a página - mostra loading
        mostrarLoading();

    } else {
        // Navegação normal via link - não mostra loading
        loading.style.display = 'none';
        document.body.style.overflow = 'auto'; 
    }
};
