document.addEventListener('DOMContentLoaded', function() {
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

    function setupDeleteConfirmation() {
        const deleteButtons = document.querySelectorAll('.delete-button');
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const subjectName = this.closest('.subject-card')
                    ?.querySelector('.subject-name')?.textContent || 'esta matéria';
                
                const deleteUrl = this.href;
                
                showConfirmModal(
                    'Confirmar Exclusão',
                    `Tem certeza que deseja excluir a matéria "${subjectName}"?`,
                    'Esta ação não pode ser desfeita. Todos os dados relacionados a esta matéria serão permanentemente removidos.',
                    'error',
                    () => {
                        window.location.href = deleteUrl;
                    },
                    () => {
                        // cancelado
                    }
                );
            });
        });
    }

    setupDeleteConfirmation();

    if (!document.querySelector('#ambient-subjects-styles')) {
        const styles = document.createElement('style');
        styles.id = 'ambient-subjects-styles';
        styles.textContent = `
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