/* ---------- Variáveis globais ---------- */
let currentSearchTerm  = '';
let searchResults      = [];
let currentResultIndex = -1;

/* ---------- Inicialização ---------- */
document.addEventListener('DOMContentLoaded', () => {
    setupChatSearch();
    processMessageLinks();

    document.querySelectorAll('.contact-item a')
            .forEach(link => link.addEventListener('click', clearSearch));
});

/* ---------- Configura caixa de busca ---------- */
function setupChatSearch() {
    const openSearchBtn   = document.getElementById('open-chat-search');
    const closeSearchBtn  = document.getElementById('close-chat-search');
    const searchContainer = document.getElementById('chat-search-container');
    const searchInput     = document.getElementById('chat-search-input');

    if (!openSearchBtn || !searchContainer) return;

    openSearchBtn.addEventListener('click', () => {
        searchContainer.style.display = 'flex';
        searchInput.focus();
        openSearchBtn.style.display = 'none';
    });

    closeSearchBtn.addEventListener('click', () => {
        searchContainer.style.display = 'none';
        openSearchBtn.style.display = 'block';
        clearSearch();
    });

    searchInput.addEventListener('input', e => {
        currentSearchTerm = e.target.value.trim();
        currentSearchTerm ? searchMessages(currentSearchTerm)
                          : clearSearch();
    });
}

/* ---------- Busca nas mensagens (apenas conteúdo) ---------- */
function searchMessages(term) {
    const messages = document.querySelectorAll('.message:not(.mensagem-data)');
    searchResults = [];

    messages.forEach((message, idx) => {
        const content = message.querySelector('.content');
        const txtContent = content ? content.textContent.toLowerCase() : '';

        if (txtContent.includes(term.toLowerCase())) {
            searchResults.push({ element: message, index: idx });
        }
    });

    // Remove realces anteriores
    document.querySelectorAll('.message.highlighted')
            .forEach(msg => msg.classList.remove('highlighted'));

    document.querySelectorAll('[data-original-html]')
            .forEach(el => {
                el.innerHTML = el.dataset.originalHtml;
                delete el.dataset.originalHtml;
            });

    // Realça resultados encontrados
    searchResults.forEach(res => {
        res.element.classList.add('highlighted');
        const el = res.element.querySelector('.content');
        if (!el) return;

        if (!el.dataset.originalHtml) {
            el.dataset.originalHtml = el.innerHTML;
        } else {
            el.innerHTML = el.dataset.originalHtml;
        }

        el.innerHTML = el.innerHTML.replace(
            new RegExp(term, 'gi'),
            match => `<span class="search-highlight">${match}</span>`
        );
    });

    updateSearchCounter();
    if (searchResults.length > 0) {
        showSearchNavigation();
        currentResultIndex = -1;
    } else {
        hideSearchNavigation();
    }
}

/* ---------- Limpa a busca ---------- */
function clearSearch() {
    currentSearchTerm = '';
    searchResults = [];
    currentResultIndex = -1;

    // Remove destaque geral
    document.querySelectorAll('.message.highlighted')
            .forEach(msg => msg.classList.remove('highlighted'));

    // Remove destaque da mensagem atualmente selecionada
    document.querySelectorAll('.message.current-result')
            .forEach(msg => msg.classList.remove('current-result'));

    // Restaurar o HTML original
    document.querySelectorAll('[data-original-html]')
            .forEach(el => {
                el.innerHTML = el.dataset.originalHtml;
                delete el.dataset.originalHtml;
            });

    hideSearchCounter();
    hideSearchNavigation();
}

/* ---------- Contador de resultados ---------- */
function updateSearchCounter() {
    const counter = document.getElementById('search-result-counter') || createSearchCounter();
    counter.textContent = `${currentResultIndex + 1}/${searchResults.length}`;
    counter.style.display = searchResults.length ? 'block' : 'none';
}

function createSearchCounter() {
    const div = document.createElement('div');
    div.id = 'search-result-counter';
    div.className = 'search-result-counter';
    document.body.appendChild(div);
    return div;
}

function hideSearchCounter() {
    const counter = document.getElementById('search-result-counter');
    if (counter) counter.style.display = 'none';
}

/* ---------- Navegação pelos botões ---------- */
function showSearchNavigation() {
    (document.getElementById('search-navigation') || createSearchNavigation()).style.display = 'flex';
}

function hideSearchNavigation() {
    const nav = document.getElementById('search-navigation');
    if (nav) nav.style.display = 'none';
}

function createSearchNavigation() {
    const nav = document.createElement('div');
    nav.id = 'search-navigation';
    nav.className = 'search-navigation';

    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '<i class="bx bx-chevron-up"></i>';
    prevBtn.addEventListener('click', () => navigateSearchResults(-1));

    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '<i class="bx bx-chevron-down"></i>';
    nextBtn.addEventListener('click', () => navigateSearchResults(1));

    nav.append(prevBtn, nextBtn);
    document.body.appendChild(nav);
    return nav;
}

function navigateSearchResults(dir) {
    if (!searchResults.length) return;

    if (currentResultIndex >= 0)
        searchResults[currentResultIndex].element.classList.remove('current-result');

    currentResultIndex = (currentResultIndex + dir + searchResults.length) % searchResults.length;

    scrollToSearchResult(currentResultIndex);
    updateSearchCounter();
}

function scrollToSearchResult(idx) {
    if (idx < 0 || idx >= searchResults.length) return;
    const res = searchResults[idx];
    res.element.classList.add('current-result');
    res.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/* ---------- Linkify URLs ---------- */
function linkify(text) {
    if (!text) return text;
    const urlRegex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    return text.replace(urlRegex, url => {
        const max = 30;
        let display = url.length > max ? url.slice(0, max) + '…' : url;
        try { new URL(url); } catch { display = url.match(/:\/\/([^/]+)/)?.[1] || url; }
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="message-link">${display}</a>`;
    });
}

function processMessageLinks() {
    document.querySelectorAll('.message .content').forEach(content => {
        if (!content.querySelector('a')) {
            content.innerHTML = linkify(content.textContent);
        }
    });
}
