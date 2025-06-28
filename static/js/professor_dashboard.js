document.addEventListener('DOMContentLoaded', function () {
    const ambientSelect = document.getElementById('ambient-select');
    const updateButton = document.getElementById('update-button');

    updateButton.addEventListener('click', () => {
        const ambientId = ambientSelect.value;
        updateDashboardData(ambientId);
    });

    async function updateDashboardData(ambientId) {
        const indicators = [
            '#indicator-avg-interval .indicator-value',
            '#indicator-avg-classes .indicator-value',
            '#indicator-num-professors .indicator-value',
            '#indicator-timetable-quality .indicator-value'
        ];
        
        indicators.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                element.textContent = '...';
                element.classList.add('loading');
            }
        });

        const url = new URL('/dashboard/api/update-dashboard-data/', window.location.origin);

        if (ambientId) {
            url.searchParams.append('ambient', ambientId);
        }

        try {
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error('Erro na requisição');
            }
            
            const newData = await response.json();

            const updates = [
                { selector: '#indicator-avg-interval .indicator-value', value: newData.indicators.average_class_interval },
                { selector: '#indicator-avg-classes .indicator-value', value: newData.indicators.average_classes },
                { selector: '#indicator-num-professors .indicator-value', value: newData.indicators.number_of_professors },
                { selector: '#indicator-timetable-quality .indicator-value', value: newData.indicators.timetable_quality }
            ];

            updates.forEach(update => {
                const element = document.querySelector(update.selector);
                if (element) {
                    element.textContent = update.value;
                    element.classList.remove('loading');
                }
            });
            if (newData.scatterData) {
                window.updateScatterChart(newData.scatterData);
            }
            if (newData.pieData) {
                window.updatePieChart(newData.pieData);
            }

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
        }
    }
});

