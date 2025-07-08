document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.querySelector('.logoSearch form');
    const searchButton = searchForm.querySelector('.search-btn');
    const searchButtonIcon = searchButton.querySelector('i');
    const searchInput = searchForm.querySelector('input[type="search"]');

    searchButton.addEventListener('click', function (e) {
        if (window.innerWidth < 576) {
            if (!searchForm.classList.contains('show')) {
                e.preventDefault();
                searchForm.classList.add('show');
                searchButtonIcon.classList.replace('bx-search', 'bx-x');
                searchInput.focus();
            } else if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchForm.classList.remove('show');
                searchButtonIcon.classList.replace('bx-x', 'bx-search');
            } 
        }
    });
});
