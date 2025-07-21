window.onload = function() {
    window.scrollTo(0, 0);
    
    setTimeout(function() {
        window.scrollTo(0, 0);
    }, 100);
};

window.addEventListener('beforeunload', function() {
    window.scrollTo(0, 0);
});