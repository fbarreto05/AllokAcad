/**
 * Controla o comportamento da sidebar em todas as páginas
 */
document.addEventListener('DOMContentLoaded', function() {
    // Elementos da sidebar
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    // Controle de abertura/fechamento da sidebar
    if (menuToggle && sidebar && sidebarOverlay) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
            
            // Prevenir scroll da página quando o menu estiver aberto
            if (sidebar.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        // Fechar a sidebar ao clicar no overlay
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        // Fechar a sidebar ao pressionar ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        // Fechar a sidebar quando redimensionar para desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
    
    // Destacar item ativo no menu lateral com base na URL atual
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#' && currentPath.includes(href)) {
            link.classList.add('active');
        }
    });
});