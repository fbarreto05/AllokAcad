document.addEventListener('DOMContentLoaded', function() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.animation = 'slideOutDown 0.4s ease-in forwards';
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.remove();
                    }
                }, 400);
            }
        }, 5000);
    });

    const ambientCards = document.querySelectorAll('.ambient-card');
    const modal = document.getElementById('join-ambient-modal');
    const modalContent = modal.querySelector('.modal-content');
    const btn = document.getElementById('join-ambient-button');
    const closeBtn = document.getElementsByClassName('close-modal')[0];
    const modalForm = modal.querySelector('form');
    const inputField = modal.querySelector('input[type="text"]');

    ambientCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
    
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        modal.style.display = 'block';
        setTimeout(() => {
            modalContent.style.opacity = '1';
            modalContent.style.transform = 'translateY(0)';
            inputField.focus();
        }, 10);
    });
    
    function closeModal() {
        modalContent.style.opacity = '0';
        modalContent.style.transform = 'translateY(-30px)';
        setTimeout(() => {
            modal.style.display = 'none';
            modalForm.reset();
        }, 300);
    }
    
    closeBtn.addEventListener('click', closeModal);
    
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            closeModal();
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeModal();
        }
    });
    
});