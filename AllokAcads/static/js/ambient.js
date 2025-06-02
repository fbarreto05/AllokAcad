document.addEventListener('DOMContentLoaded', function() {

    const ambientMenuToggle = document.getElementById('ambient-menu-toggle');
    const ambientNav = document.getElementById('ambient-nav');

    if (ambientMenuToggle && ambientNav) {
        ambientMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            ambientNav.classList.toggle('show');
        });
        
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && 
                ambientNav.classList.contains('show') && 
                !ambientNav.contains(e.target) && 
                !ambientMenuToggle.contains(e.target)) {
                ambientNav.classList.remove('show');
            }
        });
        
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768 && ambientNav.classList.contains('show')) {
                ambientNav.classList.remove('show');
            }
        });
    }
    
    const ambientNavItems = document.querySelectorAll('.ambient-nav-item');
    const currentPath = window.location.pathname;
    
    ambientNavItems.forEach(item => {
        if (item.getAttribute('href') === currentPath || 
            currentPath.includes(item.getAttribute('href'))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
});