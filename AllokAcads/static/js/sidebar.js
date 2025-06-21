document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    if (menuToggle && sidebar && sidebarOverlay) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
            
            if (sidebar.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;
    
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        const linkText = link.textContent.trim().toLowerCase();
        
        if (href && href !== '#') {
            let isActive = false;
            
            if (currentPath === href) {
                isActive = true;
            }
            else if (linkText.includes('início') && currentPath === '/home') {
                isActive = true;
            }
            else if (linkText.includes('perfil') && currentPath.startsWith('/home/profile')) {
                isActive = true;
            }
            else if (linkText.includes('dashboard') && currentPath.startsWith('/dashboard')) {
                isActive = true;
            }
            else if (linkText.includes('configurações') && (currentPath.startsWith('/config') || currentPath.startsWith('/settings'))) {
                isActive = true;
            }
            
            if (isActive) {
                link.classList.add('active');
            }
        }
    });
});