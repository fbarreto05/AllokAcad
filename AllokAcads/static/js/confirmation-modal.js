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

document.addEventListener('DOMContentLoaded', function() {

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

function createConfirmationModal(options) {
    const {
        id,
        title = 'Confirmar Ação',
        message,
        warningText,
        warningList = [],
        confirmText = 'Confirmar',
        cancelText = 'Cancelar',
        confirmUrl,
        onConfirm,
        type = 'warning'
    } = options;

    const modalHTML = `
        <div id="${id}" class="modal-overlay">
            <div class="modal-content ${type}">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="warning-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                    </div>
                    <p><strong>${message}</strong></p>
                    ${warningText ? `<p class="warning-text">${warningText}</p>` : ''}
                    ${warningList.length > 0 ? `
                        <ul class="warning-list">
                            ${warningList.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
                <div class="modal-actions">
                    <button class="cancel-button" onclick="closeConfirmationModal('${id}')">${cancelText}</button>
                    ${confirmUrl ? 
                        `<a href="${confirmUrl}" class="delete-confirm-button">${confirmText}</a>` :
                        `<button class="delete-confirm-button" onclick="${onConfirm}; closeConfirmationModal('${id}')">${confirmText}</button>`
                    }
                </div>
            </div>
        </div>
    `;

    if (!document.getElementById(id)) {
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    return id;
}

function openDeleteModal() {
    openConfirmationModal('deleteModal');
}

function closeDeleteModal() {
    closeConfirmationModal('deleteModal');
}
