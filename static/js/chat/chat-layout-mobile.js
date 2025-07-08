// Controles mobile
document.addEventListener('DOMContentLoaded', function() {
    const contactsSidebar = document.getElementById('contacts-sidebar');
    const chatArea = document.getElementById('chat-area');
    const backButton = document.getElementById('back-button');
    const aside = document.querySelector('.aside');
    
    function checkMobileLayout() {
        const isMobile = window.innerWidth <= 1080;
        
        if (isMobile) {
            // Configuração inicial para mobile
            if (window.location.pathname.includes('/chat/')) {
                contactsSidebar.classList.add('hidden');
                chatArea.classList.add('active');
                aside.style.display = 'none';
            } else {
                contactsSidebar.classList.remove('hidden');
                chatArea.classList.remove('active');
                aside.style.display = 'flex';
            }
        } else {
            // Restaura o layout para desktop
            contactsSidebar.classList.remove('hidden');
            chatArea.classList.remove('active');
            aside.style.display = 'flex';
            
            // Se estiver em uma conversa, mostra ambos os painéis
            if (window.location.pathname.includes('/chat/')) {
                chatArea.classList.add('active');
            }
        }
    }
    
    // Verificar o layout inicial
    checkMobileLayout();
    
    // Verificar quando a janela for redimensionada
    window.addEventListener('resize', checkMobileLayout);
    
    // Função para lidar com a navegação
    function handleNavigation() {
        const isMobile = window.innerWidth <= 1080;
        
        if (isMobile) {
            if (window.location.pathname.includes('/chat/')) {
                contactsSidebar.classList.add('hidden');
                chatArea.classList.add('active');
                aside.style.display = 'none';
            } else {
                contactsSidebar.classList.remove('hidden');
                chatArea.classList.remove('active');
                aside.style.display = 'flex';
            }
        } else {
            // Desktop - mostra ambos se estiver em um chat
            if (window.location.pathname.includes('/chat/')) {
                contactsSidebar.classList.remove('hidden');
                chatArea.classList.add('active');
            } else {
                chatArea.classList.remove('active');
            }
        }
    }
    
    // Evento para links de contato (funciona em mobile e desktop)
    document.querySelectorAll('.contact-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const destinatarioId = this.getAttribute('data-destinatario-id');
            const destinatarioUsername = this.getAttribute('data-destinatario-username');
            const destinatarioFoto = this.getAttribute('data-destinatario-foto');
            
            // Atualiza o chat area
            const chatHeaderLink = chatArea.querySelector('h2 a');
            const chatHeaderImg = chatHeaderLink.querySelector('img');
            chatHeaderImg.src = destinatarioFoto;
            chatHeaderImg.alt = destinatarioUsername;
            chatHeaderLink.textContent = destinatarioUsername;
            chatHeaderLink.href = `/info_user/${destinatarioId}`;
            
            // Atualiza o campo hidden do formulário
            const destinatarioInput = document.querySelector('input[name="destinatario_id"]');
            if (destinatarioInput) {
                destinatarioInput.value = destinatarioId;
            }
            
            // Atualiza a URL
            history.pushState(null, null, `/chat/${destinatarioId}`);
            
            // Ajusta a visualização baseado no tamanho da tela
            handleNavigation();
            
            // Carrega as mensagens
            atualizarMensagens();
        });
    });
    
    backButton.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/chat';
    });
    
    // Lidar com o botão voltar do navegador
    window.addEventListener('popstate', function() {
        handleNavigation();
    });
});

