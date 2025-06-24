document.addEventListener('DOMContentLoaded', function() {

    const form = document.querySelector('.preferences-form');
    const subjectCards = document.querySelectorAll('.subject-card');
    const subjectCheckboxes = document.querySelectorAll('input[name="prefered_subjects"]');
    const scheduleCheckboxes = document.querySelectorAll('input[name="available_schedules"]');
    const submitButton = document.querySelector('.submit-button');

    function updateSubjectCardState(card, checkbox) {
        const preferenceSelect = card.querySelector('.preference-select');
        
        if (checkbox.checked) {
            card.style.borderColor = '#4361ee';
            card.style.backgroundColor = '#f8fafc';
            card.style.transform = 'translateY(-2px)';
            card.style.boxShadow = '0 4px 12px rgba(67, 97, 238, 0.15)';
            if (preferenceSelect) {
                preferenceSelect.disabled = false;
                preferenceSelect.style.opacity = '1';
            }
        } else {
            card.style.borderColor = '#e2e8f0';
            card.style.backgroundColor = '#ffffff';
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
            if (preferenceSelect) {
                preferenceSelect.disabled = true;
                preferenceSelect.style.opacity = '0.5';
                preferenceSelect.value = '100'; 
            }
        }
    }

    subjectCards.forEach(card => {
        const checkbox = card.querySelector('input[name="prefered_subjects"]');
        const preferenceSelect = card.querySelector('.preference-select');
        
        if (checkbox) {
            updateSubjectCardState(card, checkbox);
            
            checkbox.addEventListener('change', function() {
                updateSubjectCardState(card, checkbox);
                updateSubmitButtonState();
            });
        }
        
        if (preferenceSelect) {
            preferenceSelect.addEventListener('change', function() {
                card.style.transition = 'all 0.3s ease';
                card.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    card.style.transform = checkbox.checked ? 'translateY(-2px)' : 'translateY(0)';
                }, 150);
            });
        }
    });

    function updateCounters() {
        const selectedSchedules = document.querySelectorAll('input[name="available_schedules"]:checked').length;
        const selectedSubjects = document.querySelectorAll('input[name="prefered_subjects"]:checked').length;
        
        const scheduleCounter = document.querySelector('.schedule-counter');
        const subjectCounter = document.querySelector('.subject-counter');
        
        if (scheduleCounter) {
            scheduleCounter.textContent = `${selectedSchedules} horários selecionados`;
        }
        
        if (subjectCounter) {
            subjectCounter.textContent = `${selectedSubjects} matérias selecionadas`;
        }
        
        return { selectedSchedules, selectedSubjects };
    }

    function updateSubmitButtonState() {
        const { selectedSchedules, selectedSubjects } = updateCounters();
        const hasSelections = selectedSchedules > 0 || selectedSubjects > 0;
        
        if (submitButton) {
            if (hasSelections) {
                submitButton.disabled = false;
                submitButton.style.opacity = '1';
                submitButton.style.cursor = 'pointer';
            } else {
                submitButton.disabled = true;
                submitButton.style.opacity = '0.6';
                submitButton.style.cursor = 'not-allowed';
            }
        }
    }

    scheduleCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSubmitButtonState();
            
            const cell = checkbox.closest('.schedule-selector-cell');
            if (cell) {
                if (checkbox.checked) {
                    cell.style.backgroundColor = '#f0f4ff';
                } else {
                    cell.style.backgroundColor = '#ffffff';
                }
            }
        });
    });

    function createSelectAllButton() {
        const scheduleSection = document.querySelector('.schedule-grid');
        if (scheduleSection && scheduleCheckboxes.length > 0) {
            const selectAllContainer = document.createElement('div');
            selectAllContainer.className = 'select-all-container';
            selectAllContainer.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
                padding: 0.75rem 1rem;
                background: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            `;
            
            const selectAllButton = document.createElement('button');
            selectAllButton.type = 'button';
            selectAllButton.textContent = 'Selecionar Todos os Horários';
            selectAllButton.className = 'select-all-btn';
            selectAllButton.style.cssText = `
                padding: 0.5rem 1rem;
                background: #4361ee;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 0.875rem;
                font-weight: 600;
                cursor: pointer;
                transition: background-color 0.2s ease;
            `;
            
            const clearAllButton = document.createElement('button');
            clearAllButton.type = 'button';
            clearAllButton.textContent = 'Limpar Seleção';
            clearAllButton.className = 'clear-all-btn';
            clearAllButton.style.cssText = `
                padding: 0.5rem 1rem;
                background: transparent;
                color: #64748b;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 0.875rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            `;
            
            selectAllButton.addEventListener('click', function() {
                scheduleCheckboxes.forEach(checkbox => {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change'));
                });
            });
            
            clearAllButton.addEventListener('click', function() {
                scheduleCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                    checkbox.dispatchEvent(new Event('change'));
                });
            });
            
            selectAllContainer.appendChild(selectAllButton);
            selectAllContainer.appendChild(clearAllButton);
            scheduleSection.insertBefore(selectAllContainer, scheduleSection.firstChild);
        }
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            const { selectedSchedules, selectedSubjects } = updateCounters();
            
            if (selectedSchedules === 0 && selectedSubjects === 0) {
                e.preventDefault();
                showNotification('Por favor, selecione pelo menos um horário ou uma matéria.', 'warning');
                return false;
            }
            
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="animate-spin">
                        <path d="M21 12a9 9 0 11-6.219-8.56"/>
                    </svg>
                    Salvando...
                `;
            }
        });
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
        
        const colors = {
            info: '#4361ee',
            warning: '#f59e0b',
            error: '#ef4444',
            success: '#10b981'
        };
        
        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }

    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        .animate-spin {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .select-all-btn:hover {
            background: #3651d5 !important;
        }
        
        .clear-all-btn:hover {
            background: #f8fafc !important;
            border-color: #cbd5e1 !important;
        }
    `;
    document.head.appendChild(style);

    createSelectAllButton();
    updateSubmitButtonState();
    
    function saveDraft() {
        const formData = new FormData(form);
        const draftData = {};
        
        for (let [key, value] of formData.entries()) {
            if (!draftData[key]) {
                draftData[key] = [];
            }
            draftData[key].push(value);
        }
        
        localStorage.setItem('ambient_form_draft', JSON.stringify(draftData));
    }
    
    if (form) {
        form.addEventListener('change', saveDraft);
    }
    
    console.log('Formulário de preferências inicializado com sucesso!');
});