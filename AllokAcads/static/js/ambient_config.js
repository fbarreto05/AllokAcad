document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    
    const fileInput = document.getElementById('picture');
    const fileNameDisplay = document.querySelector('.file-name');
    const form = document.querySelector('.config-form');
    const saveButton = document.getElementById('submit');
    
    const formOpening = document.getElementById('form_opening');
    const formClosing = document.getElementById('form_closing');
    const altOpening = document.getElementById('alt_solicitations_opening');
    const altClosing = document.getElementById('alt_solicitations_closing');
    
    const minDay = document.getElementById('min_actv_in_a_day');
    const maxDay = document.getElementById('max_actv_in_a_day');
    const minCicle = document.getElementById('min_actv_in_a_cicle');
    const maxCicle = document.getElementById('max_actv_in_a_cicle');
    
    let formChanged = false;
    const originalValues = {};
    
    function captureOriginalValues() {
        const formElements = form.querySelectorAll('input, textarea, select');
        formElements.forEach(element => {
            if (element.type === 'file') {
                originalValues[element.name] = '';
            } else {
                originalValues[element.name] = element.value;
            }
        });
    }
    
    function checkForChanges() {
        let hasChanges = false;
        const formElements = form.querySelectorAll('input, textarea, select');
        
        formElements.forEach(element => {
            if (element.type === 'file') {
                if (element.files.length > 0) {
                    hasChanges = true;
                }
            } else {
                if (element.value !== originalValues[element.name]) {
                    hasChanges = true;
                }
            }
        });
        
        formChanged = hasChanges;
        updateButtonState();
    }
    
    function updateButtonState() {
        if (saveButton) {
            if (formChanged) {
                saveButton.style.backgroundColor = '#4361ee';
                saveButton.style.cursor = 'pointer';
                saveButton.style.opacity = '1';
            } else {
                saveButton.style.backgroundColor = '#9ca3af';
                saveButton.style.cursor = 'not-allowed';
                saveButton.style.opacity = '0.7';
            }
        }
    }
    
    function initializeDateInputs() {
        [formOpening, formClosing, altOpening, altClosing].forEach(input => {
            if (input) {
                input.min = today;
                
                if (input.value && input.value < today) {
                    input.value = '';
                }
            }
        });
    }
    
    function showError(element, message) {
        const formGroup = element.closest('.form-group');
        if (formGroup) {
            formGroup.classList.add('error');
            
            const existingError = formGroup.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            
            const errorElement = document.createElement('span');
            errorElement.className = 'error-message';
            errorElement.textContent = message;
            element.insertAdjacentElement('afterend', errorElement);
        }
    }
    
    function clearError(element) {
        const formGroup = element.closest('.form-group');
        if (formGroup) {
            formGroup.classList.remove('error');
            const errorMessage = formGroup.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.remove();
            }
        }
    }
    
    function validateDateField(input, comparisonDate, comparisonType, errorMessage) {
        if (!input.value) return true;
        
        const inputDate = new Date(input.value);
        const compareDate = new Date(comparisonDate);
        
        let isValid = true;
        
        switch (comparisonType) {
            case 'after':
                isValid = inputDate > compareDate;
                break;
            case 'afterOrEqual':
                isValid = inputDate >= compareDate;
                break;
            case 'before':
                isValid = inputDate < compareDate;
                break;
            case 'beforeOrEqual':
                isValid = inputDate <= compareDate;
                break;
        }
        
        if (!isValid) {
            showError(input, errorMessage);
            return false;
        } else {
            clearError(input);
            return true;
        }
    }
    
    function validateNumberField(input, minValue, maxValue, comparisonInput, comparisonType, errorMessage) {
        if (!input.value) return true; 
        
        const value = parseInt(input.value);
        let isValid = true;
        
        if (minValue !== null && value < minValue) {
            isValid = false;
        }
        if (maxValue !== null && value > maxValue) {
            isValid = false;
        }
        
        if (comparisonInput && comparisonInput.value) {
            const comparisonValue = parseInt(comparisonInput.value);
            
            switch (comparisonType) {
                case 'greater':
                    isValid = value > comparisonValue;
                    break;
                case 'greaterOrEqual':
                    isValid = value >= comparisonValue;
                    break;
                case 'less':
                    isValid = value < comparisonValue;
                    break;
                case 'lessOrEqual':
                    isValid = value <= comparisonValue;
                    break;
            }
        }
        
        if (!isValid) {
            showError(input, errorMessage);
            return false;
        } else {
            clearError(input);
            return true;
        }
    }
    
    function setupValidationEvents() {
        if (fileInput && fileNameDisplay) {
            fileInput.addEventListener('change', function() {
                if (this.files && this.files[0]) {
                    const file = this.files[0];
                    const maxSize = 5 * 1024 * 1024;
                    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                    
                    if (file.size > maxSize) {
                        showError(this, 'O arquivo deve ter no máximo 5MB.');
                        this.value = '';
                        fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
                        return;
                    }
                    
                    if (!allowedTypes.includes(file.type)) {
                        showError(this, 'Apenas arquivos JPG, PNG e GIF são permitidos.');
                        this.value = '';
                        fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
                        return;
                    }
                    
                    clearError(this);
                    fileNameDisplay.textContent = file.name;
                } else {
                    fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
                }
            });
        }
        
        if (formOpening) {
            formOpening.addEventListener('change', function() {
                validateDateField(this, today, 'afterOrEqual', 'A data de abertura não pode ser anterior à data atual.');
                
                if (formClosing.value) {
                    formClosing.dispatchEvent(new Event('change'));
                }
            });
        }
        
        if (formClosing) {
            formClosing.addEventListener('change', function() {
                let isValid = true;
                
                isValid = validateDateField(this, today, 'afterOrEqual', 'A data de fechamento não pode ser anterior à data atual.') && isValid;
                
                if (formOpening.value) {
                    isValid = validateDateField(this, formOpening.value, 'afterOrEqual', 'A data de fechamento deve ser posterior ou igual à data de abertura do formulário.') && isValid;
                }
                
                return isValid;
            });
        }
        
        if (altOpening) {
            altOpening.addEventListener('change', function() {
                validateDateField(this, today, 'afterOrEqual', 'A data de abertura para contestação não pode ser anterior à data atual.');
                
                if (altClosing.value) {
                    altClosing.dispatchEvent(new Event('change'));
                }
            });
        }
        
        if (altClosing) {
            altClosing.addEventListener('change', function() {
                let isValid = true;
                
                isValid = validateDateField(this, today, 'afterOrEqual', 'A data de fechamento não pode ser anterior à data atual.') && isValid;
                
                if (altOpening.value) {
                    isValid = validateDateField(this, altOpening.value, 'afterOrEqual', 'A data de fechamento deve ser posterior ou igual à data de abertura para contestação.') && isValid;
                }
                
                return isValid;
            });
        }
        
        if (minDay) {
            minDay.addEventListener('change', function() {
                validateNumberField(this, 0, null, null, null, 'O mínimo de atividades por dia deve ser pelo menos 0.');
                
                if (maxDay.value) {
                    maxDay.dispatchEvent(new Event('change'));
                }
            });
        }
        
        if (maxDay) {
            maxDay.addEventListener('change', function() {
                validateNumberField(this, 1, null, minDay, 'greaterOrEqual', 'O máximo de atividades por dia deve ser maior ou igual ao mínimo.');
            });
        }
        
        if (minCicle) {
            minCicle.addEventListener('change', function() {
                validateNumberField(this, 0, null, null, null, 'O mínimo de atividades por ciclo deve ser pelo menos 0.');
                
                if (maxCicle.value) {
                    maxCicle.dispatchEvent(new Event('change'));
                }
            });
        }
        
        if (maxCicle) {
            maxCicle.addEventListener('change', function() {
                validateNumberField(this, 1, null, minCicle, 'greaterOrEqual', 'O máximo de atividades por ciclo deve ser maior ou igual ao mínimo.');
            });
        }
    }

    function showToast(message, type = 'info') {
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-icon">
                ${type === 'success' ? `
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                ` : type === 'error' ? `
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                ` : `
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                `}
            </div>
            <div class="toast-content">
                <span class="toast-message">${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.style.animation = 'slideOutDown 0.4s ease-in forwards'; setTimeout(() => this.parentElement.remove(), 400);">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        `;
        
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
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
        modalOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            backdrop-filter: blur(4px);
            opacity: 0;
            animation: fadeIn 0.3s ease-out forwards;
        `;
        
        modalOverlay.innerHTML = `
            <div class="confirmation-modal" style="
                background: white;
                border-radius: 16px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                max-width: 480px;
                width: 90%;
                max-height: 90vh;
                overflow: hidden;
                transform: scale(0.95);
                transition: transform 0.3s ease, opacity 0.3s ease;
            ">
                <div class="confirmation-modal-header" style="
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 2rem 2rem 1rem 2rem;
                ">
                    <div class="confirmation-modal-icon" style="
                        flex-shrink: 0;
                        width: 48px;
                        height: 48px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        background-color: ${type === 'warning' ? '#fef3c7' : '#fef2f2'};
                        color: ${type === 'warning' ? '#d97706' : '#dc2626'};
                    ">
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
                    <h3 class="confirmation-modal-title" style="
                        font-size: 1.25rem;
                        font-weight: 600;
                        color: #1f2937;
                        margin: 0;
                    ">${title}</h3>
                </div>
                <div class="confirmation-modal-body" style="
                    padding: 0 2rem 1.5rem 2rem;
                ">
                    <p class="confirmation-modal-message" style="
                        font-size: 1rem;
                        color: #374151;
                        margin: 0 0 0.75rem 0;
                        line-height: 1.5;
                    ">${message}</p>
                    ${details ? `<p class="confirmation-modal-details" style="
                        font-size: 0.875rem;
                        color: #6b7280;
                        margin: 0;
                        line-height: 1.4;
                        font-style: italic;
                    ">${details}</p>` : ''}
                </div>
                <div class="confirmation-modal-actions" style="
                    display: flex;
                    gap: 0.75rem;
                    padding: 1.5rem 2rem 2rem 2rem;
                    justify-content: flex-end;
                    border-top: 1px solid #f3f4f6;
                ">
                    <button type="button" class="confirmation-modal-cancel" style="
                        padding: 0.625rem 1.25rem;
                        border-radius: 8px;
                        font-size: 0.9rem;
                        font-weight: 500;
                        border: 1px solid #d1d5db;
                        background-color: #f9fafb;
                        color: #4b5563;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        min-width: 80px;
                    ">Cancelar</button>
                    <button type="button" class="confirmation-modal-confirm" style="
                        padding: 0.625rem 1.25rem;
                        border-radius: 8px;
                        font-size: 0.9rem;
                        font-weight: 500;
                        border: none;
                        background-color: ${type === 'warning' ? '#d97706' : '#dc2626'};
                        color: white;
                        cursor: pointer;
                        transition: all 0.2s ease;
                        min-width: 80px;
                    ">Confirmar</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modalOverlay);
        
        const cancelBtn = modalOverlay.querySelector('.confirmation-modal-cancel');
        const confirmBtn = modalOverlay.querySelector('.confirmation-modal-confirm');
        const modal = modalOverlay.querySelector('.confirmation-modal');
        
        setTimeout(() => {
            modal.style.transform = 'scale(1)';
            modal.style.opacity = '1';
        }, 10);
        
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
        
        cancelBtn.addEventListener('mouseenter', () => {
            cancelBtn.style.backgroundColor = '#f3f4f6';
            cancelBtn.style.borderColor = '#9ca3af';
        });
        cancelBtn.addEventListener('mouseleave', () => {
            cancelBtn.style.backgroundColor = '#f9fafb';
            cancelBtn.style.borderColor = '#d1d5db';
        });
        
        confirmBtn.addEventListener('mouseenter', () => {
            confirmBtn.style.backgroundColor = type === 'warning' ? '#b45309' : '#b91c1c';
        });
        confirmBtn.addEventListener('mouseleave', () => {
            confirmBtn.style.backgroundColor = type === 'warning' ? '#d97706' : '#dc2626';
        });
    }
    
    function validateForm() {
        let isValid = true;
        const errors = [];
        
        if (formOpening.value && formOpening.value < today) {
            isValid = false;
            errors.push('Data de abertura do formulário inválida');
        }
        
        if (formClosing.value) {
            if (formClosing.value < today) {
                isValid = false;
                errors.push('Data de fechamento do formulário inválida');
            }
            if (formOpening.value && formClosing.value < formOpening.value) {
                isValid = false;
                errors.push('Data de fechamento deve ser posterior à abertura');
            }
        }
        
        if (altOpening.value && altOpening.value < today) {
            isValid = false;
            errors.push('Data de abertura para contestação inválida');
        }
        
        if (altClosing.value) {
            if (altClosing.value < today) {
                isValid = false;
                errors.push('Data de fechamento para contestação inválida');
            }
            if (altOpening.value && altClosing.value < altOpening.value) {
                isValid = false;
                errors.push('Data de fechamento para contestação deve ser posterior à abertura');
            }
        }
        
        if (minDay.value && maxDay.value && parseInt(maxDay.value) < parseInt(minDay.value)) {
            isValid = false;
            errors.push('Máximo de atividades por dia deve ser maior ou igual ao mínimo');
        }
        
        if (minCicle.value && maxCicle.value && parseInt(maxCicle.value) < parseInt(minCicle.value)) {
            isValid = false;
            errors.push('Máximo de atividades por ciclo deve ser maior ou igual ao mínimo');
        }
        
        return { isValid, errors };
    }
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const validation = validateForm();
            
            if (!validation.isValid) {
                showToast(`Corrija os seguintes erros: ${validation.errors.join(', ')}`, 'error');
                return;
            }
            
            showConfirmModal(
                'Confirmar Alterações',
                'Tem certeza que deseja salvar as alterações nas configurações do ambiente?',
                'As configurações serão aplicadas imediatamente e afetarão todos os membros do ambiente.',
                'warning',                () => {
                    saveButton.disabled = true;
                    saveButton.classList.add('loading');
                    saveButton.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 12a9 9 0 11-6.219-8.56"/>
                        </svg>
                        Salvando...
                    `;
                    
                    const formData = new FormData(form);
                    
                    fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            showToast('Configurações salvas com sucesso!', 'success');
                            captureOriginalValues();
                            formChanged = false;
                            updateButtonState();
                        } else {
                            throw new Error('Erro ao salvar');
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                        showToast('Erro ao salvar configurações. Tente novamente.', 'error');
                    })
                    .finally(() => {
                        saveButton.disabled = false;
                        saveButton.classList.remove('loading');
                        saveButton.innerHTML = `
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                                <polyline points="17 21 17 13 7 13 7 21"></polyline>
                                <polyline points="7 3 7 8 15 8"></polyline>
                            </svg>
                            Salvar Alterações
                        `;
                    });
                }
            );
        });
    }    initializeDateInputs();
    setupValidationEvents();
    
    if (form) {
        captureOriginalValues();
        updateButtonState(); 
        
        const formElements = form.querySelectorAll('input, textarea, select');
        formElements.forEach(element => {
            element.addEventListener('input', checkForChanges);
            element.addEventListener('change', checkForChanges);
        });
    }
    
    if (!document.querySelector('#ambient-config-styles')) {
        const styles = document.createElement('style');
        styles.id = 'ambient-config-styles';
        styles.textContent = `
            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            }
            
            .toast {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 16px 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
                margin-bottom: 12px;
                border-left: 4px solid #4361ee;
                animation: slideInDown 0.4s ease-out;
                min-width: 300px;
            }
            
            .toast-success {
                border-left-color: #10b981;
            }
            
            .toast-error {
                border-left-color: #ef4444;
            }
            
            .toast-warning {
                border-left-color: #f59e0b;
            }
            
            .toast-icon {
                flex-shrink: 0;
                width: 20px;
                height: 20px;
                color: #4361ee;
            }
            
            .toast-success .toast-icon {
                color: #10b981;
            }
            
            .toast-error .toast-icon {
                color: #ef4444;
            }
            
            .toast-warning .toast-icon {
                color: #f59e0b;
            }
            
            .toast-content {
                flex: 1;
            }
            
            .toast-message {
                font-size: 0.9rem;
                color: #374151;
                font-weight: 500;
            }
            
            .toast-close {
                background: none;
                border: none;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                color: #9ca3af;
                transition: all 0.2s ease;
                flex-shrink: 0;
            }
            
            .toast-close:hover {
                background-color: #f3f4f6;
                color: #6b7280;
            }
            
            @keyframes slideInDown {
                from {
                    opacity: 0;
                    transform: translateY(-100px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes slideOutDown {
                from {
                    opacity: 1;
                    transform: translateY(0);
                }
                to {
                    opacity: 0;
                    transform: translateY(-100px);
                }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    console.log('Sistema de configuração de ambiente inicializado com sucesso!');
    
    window.openDeleteModal = function() {
        openConfirmationModal('deleteModal');
    };
    
    window.closeDeleteModal = function() {
        closeConfirmationModal('deleteModal');
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