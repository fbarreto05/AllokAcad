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

    function renderScatterChart(scatterData) {
        const ctx = document.getElementById('professorScatterChart').getContext('2d');
        if (window.professorScatterChartInstance) {
            window.professorScatterChartInstance.destroy();
        }
        const data = {
            datasets: [{
                label: 'Eficiência do Dia',
                data: scatterData.map(item => ({x: item.professor, y: item.day_efficiency})),
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
            }]
        };
        window.professorScatterChartInstance = new Chart(ctx, {
            type: 'scatter',
            data: data,
            options: {
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw.x}: ${context.raw.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        title: { display: true, text: 'Professor' },
                        ticks: { autoSkip: false }
                    },
                    y: {
                        title: { display: true, text: 'Eficiência do Dia' },
                        min: 0, max: 1
                    }
                }
            }
        });
    }

    function renderPieChart(pieData) {
        const ctx = document.getElementById('professorPieChart').getContext('2d');
        if (window.professorPieChartInstance) {
            window.professorPieChartInstance.destroy();
        }
        window.professorPieChartInstance = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: pieData.labels,
                datasets: [{
                    data: pieData.values,
                    backgroundColor: [
                        '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF', '#8BC34A', '#E91E63', '#00BCD4'
                    ],
                }]
            },
            options: {
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    window.addEventListener('DOMContentLoaded', function() {
        const scatterDataScript = document.getElementById('professor-scatter-data');
        if (scatterDataScript) {
            const scatterData = JSON.parse(scatterDataScript.textContent);
            renderScatterChart(scatterData);
        }
        const pieDataScript = document.getElementById('professor-pie-data');
        if (pieDataScript) {
            const pieData = JSON.parse(pieDataScript.textContent);
            renderPieChart(pieData);
        }
    });

    window.updateScatterChart = function(scatterData) {
        renderScatterChart(scatterData);
    }

    window.updatePieChart = function(pieData) {
        renderPieChart(pieData);
    }
});