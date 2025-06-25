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
    });    const visitLinks = document.querySelectorAll('.visit-link');
    visitLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    const profileUserid = document.querySelector('.profile-userid');
    if (profileUserid) {
        profileUserid.style.cursor = 'pointer';
        profileUserid.title = 'Clique para copiar o ID';
        
        profileUserid.addEventListener('click', function() {
            const userid = this.textContent.replace('ID: ', '');
            navigator.clipboard.writeText(userid).then(() => {
                showToast('ID copiado para a área de transferência!', 'success');
            }).catch(() => {
                showToast('Erro ao copiar ID', 'error');
            });
        });
    }

    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <path d="m9 11 3 3L22 4"></path>
            </svg>`,
            error: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>`,
            warning: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>`,
            info: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>`
        };

        toast.innerHTML = `
            <div class="toast-icon">
                ${icons[type]}
            </div>
            <div class="toast-content">
                <span class="toast-message">${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.style.animation = 'slideOutDown 0.4s ease-in forwards'; setTimeout(() => this.parentElement.remove(), 400);">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;

        toastContainer.appendChild(toast);

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
    }

    const profileCard = document.querySelector('.profile-card');
    if (profileCard) {
        profileCard.style.opacity = '0';
        profileCard.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            profileCard.style.transition = 'all 0.6s ease-out';
            profileCard.style.opacity = '1';
            profileCard.style.transform = 'translateY(0)';
        }, 100);
    }
    const profileImage = document.querySelector('.profile-image img');
    if (profileImage) {
        profileImage.style.transition = 'transform 0.3s ease-out';
    }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const toasts = document.querySelectorAll('.toast');
            toasts.forEach(toast => {
                toast.style.animation = 'slideOutDown 0.4s ease-in forwards';
                setTimeout(() => {
                    if (toast.parentElement) {
                        toast.remove();
                    }
                }, 400);
            });
        }
    });

    console.log('Sistema de perfil inicializado com sucesso!');
    
    window.openDeleteProfileModal = function() {
        openConfirmationModal('deleteProfileModal');
    };
    
    window.closeDeleteProfileModal = function() {
        closeConfirmationModal('deleteProfileModal');
    };
    
    function openConfirmationModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            modal.focus();
        }
    }
    
    function closeConfirmationModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            const modalId = e.target.id;
            closeConfirmationModal(modalId);
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModals = document.querySelectorAll('.modal-overlay.active');
            activeModals.forEach(modal => {
                closeConfirmationModal(modal.id);
            });
        }
    });

    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-close') || e.target.closest('.modal-close')) {
            const modal = e.target.closest('.modal-overlay');
            if (modal) {
                closeConfirmationModal(modal.id);
            }
        }
    });
});

function openDeleteProfileModal() {
    const modal = document.getElementById('deleteProfileModal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeDeleteProfileModal() {
    const modal = document.getElementById('deleteProfileModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}