document.addEventListener('DOMContentLoaded', function() {

    const ambientMenuToggle = document.getElementById('ambient-menu-toggle');
    const ambientNav = document.getElementById('ambient-nav');

    if (ambientMenuToggle && ambientNav) {
        ambientMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            ambientNav.classList.toggle('show');
        });
        
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && 
                ambientNav.classList.contains('show') && 
                !ambientNav.contains(e.target) && 
                !ambientMenuToggle.contains(e.target)) {
                ambientNav.classList.remove('show');
            }
        });
        
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768 && ambientNav.classList.contains('show')) {
                ambientNav.classList.remove('show');
            }
        });
    }
    
    const ambientNavItems = document.querySelectorAll('.ambient-nav-item');
    const currentPath = window.location.pathname;
    
    ambientNavItems.forEach(item => {
        if (item.getAttribute('href') === currentPath || 
            currentPath.includes(item.getAttribute('href'))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
});

class LoadingModal {
    constructor() {
        this.modal = null;
        this.titleEl = null;
        this.messageEl = null;
        this.progressBar = null;
        this.messageInterval = null;
        this.progressInterval = null;
        this.currentProgress = 0;
        this.init();
    }

    init() {
        if (!document.getElementById('loading-popup')) {
            this.createModal();
        }
        this.modal = document.getElementById('loading-popup');
        this.titleEl = document.getElementById('loading-title');
        this.messageEl = document.getElementById('loading-message');
        this.progressBar = document.querySelector('.loading-progress-bar');
    }

    createModal() {
        const modalHTML = `
            <div id="loading-popup" class="loading-popup">
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <h3 id="loading-title" class="loading-title">Atribuição em andamento</h3>
                    <p id="loading-message" class="loading-message">Iniciando processo...</p>
                    <div class="loading-progress">
                        <div class="loading-progress-bar"></div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    show(title = 'Atribuição em andamento', message = 'Iniciando processo...') {
        this.modal.classList.add('show');
        this.titleEl.textContent = title;
        this.messageEl.innerHTML = message;
        this.currentProgress = 0;
        this.updateProgress(0);
        this.startDynamicMessages();
        this.simulateProgress();
    }

    hide() {
        this.modal.classList.remove('show');
        this.stopDynamicMessages();
        this.stopProgress();
    }

    updateTitle(title) {
        if (this.titleEl) {
            this.titleEl.textContent = title;
        }
    }

    updateMessage(message) {
        if (this.messageEl) {
            this.messageEl.innerHTML = message;
        }
    }

    updateProgress(percent) {
        if (this.progressBar) {
            this.progressBar.style.width = percent + '%';
        }
    }

    startDynamicMessages() {
        const messages = [
            'Analisando turmas e disciplinas...',
            'Processando preferências dos professores...',
            'Otimizando distribuição de salas...',
            'Verificando conflitos de horários...',
            'Aplicando regras de negócio...',
            'Quase lá! Finalizando atribuições...',
            'Salvando resultados...'
        ];
        
        let messageIndex = 0;
        this.updateMessage(messages[0]);
        
        this.messageInterval = setInterval(() => {
            messageIndex = (messageIndex + 1) % messages.length;
            this.updateMessage(messages[messageIndex]);
        }, 3000);
    }

    stopDynamicMessages() {
        if (this.messageInterval) {
            clearInterval(this.messageInterval);
            this.messageInterval = null;
        }
    }

    simulateProgress() {
        let progress = 0;
        const steps = [15, 30, 45, 60, 75, 85, 95];
        let stepIndex = 0;
        
        this.progressInterval = setInterval(() => {
            if (stepIndex < steps.length) {
                progress = steps[stepIndex];
                this.updateProgress(progress);
                stepIndex++;
            } else {
                // Simulate final completion
                if (progress < 100) {
                    progress += Math.random() * 2;
                    progress = Math.min(progress, 99);
                    this.updateProgress(progress);
                }
            }
        }, 2000);
    }

    stopProgress() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    showSuccess(title = 'Atribuição concluída!', message = 'A atribuição foi realizada com sucesso.', duration = 2500) {
        this.stopDynamicMessages();
        this.stopProgress();
        this.updateTitle(title);
        this.updateMessage(message);
        this.updateProgress(100);
        
        setTimeout(() => {
            this.hide();
        }, duration);
    }

    showError(title = 'Erro na atribuição', message = 'Ocorreu um erro durante o processo. Tente novamente.', duration = 3000) {
        this.stopDynamicMessages();
        this.stopProgress();
        this.updateTitle(title);
        this.updateMessage(message);
        
        setTimeout(() => {
            this.hide();
        }, duration);
    }
}

const loadingModal = new LoadingModal();

document.addEventListener('DOMContentLoaded', function() {
    const runAtribuitionBtn = document.getElementById('run-atribuition-btn');
    const runAlocationBtn = document.getElementById('run-alocation-btn');
    
    if (runAtribuitionBtn) {
        runAtribuitionBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            loadingModal.show('Atribuição em andamento', 'Iniciando processo de atribuição...');
            
            sessionStorage.setItem('showAtribuicaoSuccess', '1');
            
            const url = runAtribuitionBtn.getAttribute('data-url');
            
            setTimeout(() => {
                window.location.href = url;
            }, 500);
        });
    }

    if (runAlocationBtn) {
        runAlocationBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const alocationModal = new LoadingModal();
            alocationModal.startDynamicMessages = function() {
                const messages = [
                    'Analisando disponibilidade de horários...',
                    'Processando preferências de horários...',
                    'Otimizando distribuição temporal...',
                    'Verificando conflitos de agenda...',
                    'Organizando grade de horários...',
                    'Quase lá! Finalizando alocação...',
                    'Salvando cronograma final...'
                ];
                
                let messageIndex = 0;
                this.updateMessage(messages[0]);
                
                this.messageInterval = setInterval(() => {
                    messageIndex = (messageIndex + 1) % messages.length;
                    this.updateMessage(messages[messageIndex]);
                }, 3000);
            };
            
            alocationModal.show('Alocação em andamento', 'Iniciando processo de alocação...');
            
            sessionStorage.setItem('showAlocationSuccess', '1');
            
            const url = runAlocationBtn.getAttribute('data-url');
            
            setTimeout(() => {
                window.location.href = url;
            }, 500);
        });
    }

    if (window.performance && window.performance.navigation && window.performance.navigation.type === 1) {
        if (sessionStorage.getItem('showAtribuicaoSuccess')) {
            setTimeout(() => {
                loadingModal.showSuccess('Atribuição concluída!', 'A atribuição foi realizada com sucesso.');
                sessionStorage.removeItem('showAtribuicaoSuccess');
            }, 300);
        }
        
        if (sessionStorage.getItem('showAlocationSuccess')) {
            setTimeout(() => {
                loadingModal.showSuccess('Alocação concluída!', 'A alocação foi realizada com sucesso.');
                sessionStorage.removeItem('showAlocationSuccess');
            }, 300);
        }
    }
});