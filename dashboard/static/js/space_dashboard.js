document.addEventListener('DOMContentLoaded', function () {
    const ambientSelect = document.getElementById('ambient-select');
    const semesterSelect = document.getElementById('semester-select');
    const updateButton = document.getElementById('update-button');

    if (updateButton) {
        updateButton.addEventListener('click', () => {
            const ambientId = ambientSelect?.value || '';
            const semesterId = semesterSelect?.value || '';
            updateDashboardData(ambientId, semesterId);
        });
    }

    async function updateDashboardData(ambientId, semesterId) {
        const indicators = [
            '#metric-total-spaces .metric-value',
            '#metric-occupied-spaces .metric-value',
            '#metric-occupation-rate .metric-value',
            '#metric-space-efficiency .metric-value'
        ];
        
        indicators.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                element.textContent = '...';
                element.classList.add('loading');
            }
        });

        const url = new URL('/dashboard/api/update-space-dashboard-data/', window.location.origin);
        if (ambientId) {
            url.searchParams.append('ambient', ambientId);
        }
        if (semesterId) {
            url.searchParams.append('semester', semesterId);
        }

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const newData = await response.json();
            const indicatorsData = newData.indicators || {};
            const updates = [
                { 
                    selector: '#metric-total-spaces .metric-value', 
                    value: indicatorsData.total_periods !== undefined ? indicatorsData.total_periods : '--' 
                },
                { 
                    selector: '#metric-occupied-spaces .metric-value', 
                    value: indicatorsData.occupied_spaces !== undefined ? indicatorsData.occupied_spaces : '--' 
                },
                { 
                    selector: '#metric-occupation-rate .metric-value', 
                    value: indicatorsData.occupation_rate !== undefined ? `${indicatorsData.occupation_rate}%` : '--' 
                },
                { 
                    selector: '#metric-space-efficiency .metric-value', 
                    value: indicatorsData.space_efficiency !== undefined ? `${indicatorsData.space_efficiency}%` : '--' 
                }
            ];
            updates.forEach(update => {
                const element = document.querySelector(update.selector);
                if (element) {
                    element.textContent = update.value;
                    element.classList.remove('loading');
                }
            });
            showUpdateFeedback('success', 'Dashboard atualizado com sucesso!');
        } catch (error) {
            console.error('Erro ao atualizar dashboard:', error);
            indicators.forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.textContent = 'Erro';
                    element.classList.remove('loading');
                    element.classList.add('error');
                }
            });
            showUpdateFeedback('error', 'Erro ao atualizar dashboard. Tente novamente.');
        }
    }

    function showUpdateFeedback(type, message) {
        const existingFeedback = document.querySelector('.update-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        const feedback = document.createElement('div');
        feedback.className = `update-feedback update-feedback--${type}`;
        feedback.textContent = message;
        feedback.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 500;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            animation: slideInRight 0.3s ease;
            ${type === 'success' 
                ? 'background: #10b981; color: white;' 
                : 'background: #ef4444; color: white;'
            }
        `;
        if (!document.querySelector('#feedback-styles')) {
            const style = document.createElement('style');
            style.id = 'feedback-styles';
            style.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        document.body.appendChild(feedback);
        setTimeout(() => {
            feedback.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (feedback.parentNode) {
                    feedback.remove();
                }
            }, 300);
        }, 3000);
    }

    const style = document.createElement('style');
    style.textContent = `
        .metric-value.error {
            color: rgba(255, 255, 255, 0.7) !important;
        }
    `;
    document.head.appendChild(style);
});