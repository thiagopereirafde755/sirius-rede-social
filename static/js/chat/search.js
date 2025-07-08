document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-contact');
    const noContactsMessage = document.getElementById('no-contacts-message');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const search = this.value.toLowerCase();
            let found = false;
            document.querySelectorAll('.contacts-list .contact-item').forEach(function(item) {
                const name = item.querySelector('span').textContent.toLowerCase();
                const isMatch = name.includes(search);
                item.style.display = isMatch ? '' : 'none';
                if (isMatch) found = true;
            });
            if (noContactsMessage) {
                noContactsMessage.style.display = found ? 'none' : '';
            }
        });
    }
});