/**
 * Controla apenas a navegação horizontal do ambiente
 * Sem interferir na sidebar principal
 */
document.addEventListener('DOMContentLoaded', function() {
    // Elementos da navegação horizontal do ambiente
    const ambientMenuToggle = document.getElementById('ambient-menu-toggle');
    const ambientNav = document.getElementById('ambient-nav');
    
    // Controle de abertura/fechamento da navegação horizontal em modo mobile
    if (ambientMenuToggle && ambientNav) {
        ambientMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            ambientNav.classList.toggle('show');
        });
        
        // Fechar a navegação ao clicar fora dela
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && 
                ambientNav.classList.contains('show') && 
                !ambientNav.contains(e.target) && 
                !ambientMenuToggle.contains(e.target)) {
                ambientNav.classList.remove('show');
            }
        });
        
        // Fechar ao redimensionar
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768 && ambientNav.classList.contains('show')) {
                ambientNav.classList.remove('show');
            }
        });
    }
    
    // Navegação entre abas do ambiente
    const ambientNavItems = document.querySelectorAll('.ambient-nav-item');
    const ambientSections = document.querySelectorAll('.ambient-section');
    
    ambientNavItems.forEach(item => {
        const targetId = item.getAttribute('data-target');
        
        if (targetId) {
            item.addEventListener('click', function(e) {
                if (item.classList.contains('exit-item') || targetId === 'external') {
                    return; // Não prevenir comportamento padrão para links externos
                }
                
                e.preventDefault();
                
                // Remover classe active de todos os itens
                ambientNavItems.forEach(navItem => {
                    navItem.classList.remove('active');
                });
                
                // Adicionar classe active ao item clicado
                this.classList.add('active');
                
                // Esconder todas as seções
                ambientSections.forEach(section => {
                    section.classList.remove('active');
                });
                
                // Mostrar a seção alvo
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
                
                // Fechar o menu em modo mobile
                if (window.innerWidth <= 768 && ambientNav) {
                    ambientNav.classList.remove('show');
                }
            });
        }
    });
});