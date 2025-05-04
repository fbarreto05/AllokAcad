document.addEventListener('DOMContentLoaded', function() {

    const ambientCards = document.querySelectorAll('.ambient-card');
    ambientCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
    
});