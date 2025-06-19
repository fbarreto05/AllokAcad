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

    const form = document.getElementById('profileForm');
    const pictureInput = document.getElementById('picture');
    const currentPhoto = document.getElementById('currentPhoto');
    const nameInput = document.getElementById('name');
    const descriptionInput = document.getElementById('description');
    const saveButton = document.getElementById('saveButton');

    let formChanged = false;
    const originalValues = {
        name: nameInput.value,
        description: descriptionInput.value
    };    if (pictureInput) {
        pictureInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    showToast('A imagem deve ter no máximo 5MB', 'error');
                    this.value = '';
                    return;
                }

                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    showToast('Formato de imagem inválido. Use JPG, PNG ou GIF', 'error');
                    this.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    if (currentPhoto.tagName === 'IMG') {
                        currentPhoto.src = e.target.result;
                    } else {
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        img.alt = 'Preview da nova foto';
                        img.style.width = '100%';
                        img.style.height = '100%';
                        img.style.objectFit = 'cover';
                        currentPhoto.innerHTML = '';
                        currentPhoto.appendChild(img);
                    }
                    formChanged = true;
                    showToast('Preview da nova foto carregado com sucesso!', 'info');
                };
                reader.readAsDataURL(file);
            }
        });
    }

        nameInput.addEventListener('input', function() {
        formChanged = this.value !== originalValues.name;
        validateForm();
    });

    descriptionInput.addEventListener('input', function() {
        formChanged = this.value !== originalValues.description;
        validateForm();
    });

    function validateForm() {
        const isNameValid = nameInput.value.trim().length >= 2;
        
        if (saveButton) {
            saveButton.disabled = !isNameValid;
        }

        if (nameInput.value.trim().length > 0 && nameInput.value.trim().length < 2) {
            nameInput.style.borderColor = '#ef4444';
            nameInput.style.backgroundColor = '#fef2f2';
        } else if (isNameValid) {
            nameInput.style.borderColor = '#10b981';
            nameInput.style.backgroundColor = '#f0fdf4';
        } else {
            nameInput.style.borderColor = '#e5e7eb';
            nameInput.style.backgroundColor = '#ffffff';
        }

        return isNameValid;
    }

    validateForm();    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (!validateForm()) {
                showToast('Por favor, preencha todos os campos obrigatórios corretamente.', 'warning');
                return;
            }

            showConfirmModal(
                'Confirmar Alterações',
                'Deseja salvar as alterações feitas no seu perfil?',
                'As informações serão atualizadas imediatamente.',
                'warning',
                () => {
                    saveButton.disabled = true;
                    saveButton.innerHTML = `
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 12a9 9 0 11-6.219-8.56"/>
                        </svg>
                        Salvando...
                    `;
                    saveButton.style.pointerEvents = 'none';
                    
                    formChanged = false;
                    
                    form.submit();
                }
            );
        });
    }

    window.addEventListener('beforeunload', function(e) {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    if (descriptionInput) {
        const maxLength = 500;
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.fontSize = '0.875rem';
        counter.style.color = '#6b7280';
        counter.style.textAlign = 'right';
        counter.style.marginTop = '0.25rem';
        
        descriptionInput.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - descriptionInput.value.length;
            counter.textContent = `${descriptionInput.value.length}/${maxLength}`;
            
            if (remaining < 50) {
                counter.style.color = '#ef4444';
            } else if (remaining < 100) {
                counter.style.color = '#f59e0b';
            } else {
                counter.style.color = '#6b7280';
            }
        }
        
        descriptionInput.addEventListener('input', updateCounter);
        updateCounter();
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
    const editCard = document.querySelector('.edit-card');
    if (editCard) {
        editCard.style.opacity = '0';
        editCard.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            editCard.style.transition = 'all 0.6s ease-out';
            editCard.style.opacity = '1';
            editCard.style.transform = 'translateY(0)';
        }, 100);
    }
});