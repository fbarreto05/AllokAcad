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

    const form = document.querySelector('.position-form');
    const selectElement = document.getElementById('admtype');
    const saveButton = document.getElementById('saveButton');

    function validateForm() {
        const isValid = selectElement.value !== '' && selectElement.value !== null;
        
        if (saveButton) {
            saveButton.disabled = !isValid;
        }
        
        return isValid;
    }

    if (selectElement) {
        validateForm();
        
        selectElement.addEventListener('change', function() {
            validateForm();
            
            if (this.value) {
                this.style.borderColor = '#10b981';
                this.style.backgroundColor = '#f0fdf4';
            } else {
                this.style.borderColor = '#e5e7eb';
                this.style.backgroundColor = '#ffffff';
            }
        });
    }    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                showToast('Por favor, selecione um cargo antes de continuar.', 'warning');
                return;
            }

            e.preventDefault(); 
            
            const selectedOption = selectElement.options[selectElement.selectedIndex];
            const cargoName = selectedOption.text.replace(' (Cargo atual)', '');
            
            showConfirmModal(
                'Confirmar Alteração de Cargo',
                `Tem certeza que deseja alterar o cargo do membro para "${cargoName}"?`,
                'Esta ação não pode ser desfeita e o membro será notificado sobre a alteração.',
                'warning',
                () => {
                    saveButton.disabled = true;
                    saveButton.innerHTML = `
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 12a9 9 0 11-6.219-8.56"/>
                        </svg>
                        Alterando...
                    `;
                    saveButton.style.pointerEvents = 'none';
                    
                    form.submit();
                }
            );
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

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const confirmModal = document.querySelector('.modal-overlay');
            if (confirmModal && confirmModal.style.display !== 'none') {
                return;
            }
            
            if (confirm('Deseja cancelar a alteração de cargo e voltar?')) {
                window.history.back();
            }
        }
        
        if (e.key === 'Enter' && e.target === selectElement) {
            e.preventDefault();
            if (validateForm()) {
                form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            }
        }
    });

    const buttons = document.querySelectorAll('.cancel-button, .save-button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
        });
        
        button.addEventListener('mouseleave', function() {
            if (!this.disabled) {
                this.style.transform = 'translateY(0)';
            }
        });
    });

    let formChanged = false;
    if (selectElement) {
        const originalValue = selectElement.value;
        
        selectElement.addEventListener('change', function() {
            formChanged = this.value !== originalValue;
        });
    }

    window.addEventListener('beforeunload', function(e) {
        if (formChanged && !saveButton.disabled) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    if (form) {
        form.addEventListener('submit', function() {
            formChanged = false;
        });
    }
});

function showToast(message, type = 'info') {
    const event = new CustomEvent('showToast', {
        detail: { message, type }
    });
    document.dispatchEvent(event);
}

function showConfirmModal(title, message, details, type = 'warning', onConfirm = null, onCancel = null) {

    const existingModal = document.querySelector('.confirmation-modal-overlay');
    if (existingModal) {
        existingModal.remove();
    }

    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'confirmation-modal-overlay';
    modalOverlay.innerHTML = `
        <div class="confirmation-modal">
            <div class="confirmation-modal-header">
                <div class="confirmation-modal-icon confirmation-modal-icon-${type}">
                    ${type === 'warning' ? `
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                            <path d="M12 9v4"/>
                            <path d="m12 17 .01 0"/>
                        </svg>
                    ` : `
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M12 8v8"/>
                            <path d="m8 12 4 4 4-4"/>
                        </svg>
                    `}
                </div>
                <h3 class="confirmation-modal-title">${title}</h3>
            </div>
            <div class="confirmation-modal-body">
                <p class="confirmation-modal-message">${message}</p>
                ${details ? `<p class="confirmation-modal-details">${details}</p>` : ''}
            </div>
            <div class="confirmation-modal-actions">
                <button type="button" class="confirmation-modal-cancel">Cancelar</button>
                <button type="button" class="confirmation-modal-confirm confirmation-modal-confirm-${type}">Confirmar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modalOverlay);

    const cancelBtn = modalOverlay.querySelector('.confirmation-modal-cancel');
    const confirmBtn = modalOverlay.querySelector('.confirmation-modal-confirm');

    function closeModal() {
        modalOverlay.style.animation = 'fadeOut 0.3s ease-out forwards';
        setTimeout(() => {
            if (modalOverlay.parentElement) {
                modalOverlay.remove();
            }
        }, 300);
    }

    cancelBtn.addEventListener('click', () => {
        closeModal();
        if (onCancel) onCancel();
    });

    confirmBtn.addEventListener('click', () => {
        closeModal();
        if (onConfirm) onConfirm();
    });

    function handleKeyDown(e) {
        if (e.key === 'Escape') {
            closeModal();
            if (onCancel) onCancel();
            document.removeEventListener('keydown', handleKeyDown);
        }
    }
    document.addEventListener('keydown', handleKeyDown);

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            closeModal();
            if (onCancel) onCancel();
        }
    });

    setTimeout(() => {
        modalOverlay.style.animation = 'fadeIn 0.3s ease-out forwards';
    }, 10);
}