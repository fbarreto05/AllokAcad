document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const saveButton = document.getElementById('submit');
    
    const registerInput = document.getElementById('register');
    const timeInCampusInput = document.getElementById('time_in_campus');
    const timeInInstitutionInput = document.getElementById('time_in_institution');
    const careerLevelInput = document.getElementById('career_level');
    
    let formChanged = false;
    const originalValues = {};
    
    function captureOriginalValues() {
        originalValues.register = registerInput?.value || '';
        originalValues.time_in_campus = timeInCampusInput?.value || '';
        originalValues.time_in_institution = timeInInstitutionInput?.value || '';
        originalValues.career_level = careerLevelInput?.value || '';
        
        const formationCheckboxes = document.querySelectorAll('input[name="member_formations"]');
        originalValues.formations = [];
        formationCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                originalValues.formations.push(checkbox.value);
            }
        });
        
        const experienceInputs = document.querySelectorAll('input[type="number"][name*="experience_time"]');
        experienceInputs.forEach(input => {
            originalValues[input.name] = input.value || '';
        });
    }
    
    function updateSaveButtonState() {
        if (saveButton) {
            if (formChanged) {
                saveButton.disabled = false;
                saveButton.style.opacity = '1';
                saveButton.style.cursor = 'pointer';
            } else {
                saveButton.disabled = true;
                saveButton.style.opacity = '0.6';
                saveButton.style.cursor = 'not-allowed';
            }
        }
    }
    
    function checkForChanges() {
        const currentValues = {
            register: registerInput?.value || '',
            time_in_campus: timeInCampusInput?.value || '',
            time_in_institution: timeInInstitutionInput?.value || '',
            career_level: careerLevelInput?.value || ''
        };
        
        const formationCheckboxes = document.querySelectorAll('input[name="member_formations"]');
        currentValues.formations = [];
        formationCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                currentValues.formations.push(checkbox.value);
            }
        });
        
        const experienceInputs = document.querySelectorAll('input[type="number"][name*="experience_time"]');
        experienceInputs.forEach(input => {
            currentValues[input.name] = input.value || '';
        });
        
        formChanged = false;
        
        for (const key in originalValues) {
            if (key === 'formations') {
                if (JSON.stringify(currentValues.formations.sort()) !== JSON.stringify(originalValues.formations.sort())) {
                    formChanged = true;
                    break;
                }
            } else {
                if (currentValues[key] !== originalValues[key]) {
                    formChanged = true;
                    break;
                }
            }
        }
        
        updateSaveButtonState();
    }
    
    function setupFormChangeTracking() {
        const inputsToMonitor = [
            registerInput, timeInCampusInput, timeInInstitutionInput, careerLevelInput
        ];
        
        const formationCheckboxes = document.querySelectorAll('input[name="member_formations"]');
        formationCheckboxes.forEach(checkbox => inputsToMonitor.push(checkbox));
        
        const experienceInputs = document.querySelectorAll('input[type="number"][name*="experience_time"]');
        experienceInputs.forEach(input => inputsToMonitor.push(input));
        
        inputsToMonitor.forEach(input => {
            if (input) {
                input.addEventListener('input', checkForChanges);
                input.addEventListener('change', checkForChanges);
            }
        });
    }
    
    function showToast(message, type = 'info') {
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const iconSvg = type === 'success' ? 
            `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="9,11 12,14 22,4"/>
            </svg>` :
            type === 'error' ?
            `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>` :
            `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                <path d="M12 9v4"/>
                <path d="m12 17 .01 0"/>
            </svg>`;
          toast.innerHTML = `
            <div class="toast-icon">
                ${iconSvg}
            </div>
            <div class="toast-content">
                <span class="toast-message">${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        `;
        
        toast.style.animation = 'slideInDown 0.4s ease-out forwards';
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
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!formChanged) {
                showToast('Nenhuma alteração foi feita para salvar.', 'warning');
                return;
            }
              showConfirmModal(
                'Confirmar Alterações',
                'Tem certeza que deseja salvar as alterações no seu perfil?',
                'As informações do seu perfil profissional serão atualizadas.',
                'warning',
                () => {
                    const originalContent = saveButton.innerHTML;
                    saveButton.disabled = true;
                    saveButton.classList.add('loading');
                    saveButton.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 12a9 9 0 11-6.219-8.56"/>
                        </svg>
                        Salvando...
                    `;
                    
                    const formData = new FormData(form);
                    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
                    
                    fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            return response.json().catch(() => {
                                return { success: true, message: 'Perfil atualizado com sucesso!' };
                            });
                        } else {
                            throw new Error(`Erro ${response.status}: ${response.statusText}`);
                        }
                    })
                    .then(data => {
                        if (data.success !== false) {
                            formChanged = false;
                            showToast(data.message || 'Perfil atualizado com sucesso!', 'success');
                            
                            setTimeout(() => {
                                if (data.redirect_url) {
                                    window.location.href = data.redirect_url;
                                } else {
                                    window.location.reload();
                                }
                            }, 1500);
                        } else {
                            throw new Error(data.message || 'Erro desconhecido');
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao salvar:', error);
                        showToast('Erro ao salvar o perfil. Tente novamente.', 'error');
                        
                        saveButton.disabled = false;
                        saveButton.classList.remove('loading');
                        saveButton.innerHTML = originalContent;
                        updateSaveButtonState();
                    });
                },
                () => {
                    // cancelado
                }
            );
        });
    }
    
    window.addEventListener('beforeunload', function(e) {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = 'Você tem alterações não salvas. Deseja realmente sair?';
        }
    });
    
    captureOriginalValues();
    setupFormChangeTracking();
    updateSaveButtonState();
    
    if (!document.querySelector('#ambient-profile-edit-styles')) {
        const styles = document.createElement('style');
        styles.id = 'ambient-profile-edit-styles';
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
                    transform: translateY(-100%);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutDown {
                from {
                    transform: translateY(0);
                    opacity: 1;
                }
                to {
                    transform: translateY(-100%);
                    opacity: 0;
                }
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }
            
            @keyframes fadeOut {
                from {
                    opacity: 1;
                }
                to {
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(styles);
    }
});