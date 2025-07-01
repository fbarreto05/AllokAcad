document.addEventListener('DOMContentLoaded', function () {
    const ambientSelect = document.getElementById('ambient-select');
    const semesterSelect = document.getElementById('semester-select');
    const updateButton = document.getElementById('update-button');

    
    if (semesterSelect) {
        semesterSelect.addEventListener('change', () => {
            const ambientId = ambientSelect?.value || '';
            const semesterId = semesterSelect?.value || '';
            updateDashboardData(ambientId, semesterId);
        });
    }
    if (ambientSelect) {
        ambientSelect.addEventListener('change', () => {
            const ambientId = ambientSelect?.value || '';
            const semesterId = semesterSelect?.value || '';
            updateDashboardData(ambientId, semesterId);
        });
    }
    if (updateButton) {
        updateButton.addEventListener('click', () => {
            const ambientId = ambientSelect?.value || '';
            const semesterId = semesterSelect?.value || '';
            updateDashboardData(ambientId, semesterId);
        });
    }

    
    const initialAmbient = ambientSelect?.value || '';
    const initialSemester = semesterSelect?.value || '';
    updateDashboardData(initialAmbient, initialSemester);

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

            updateCharts(newData);
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

    function updateCharts(newData) {

        const spaceOccupationData = newData.bar_graph_data || [];
        renderBarChart('spaceOccupationChart', spaceOccupationData, 'Ocupação por Tipo de Espaço', 'Espaços', 'Total de Períodos');

        const hourlyUsageData = newData.polar_graph_data || [];
        populatePolarSpaceDropdown(hourlyUsageData);
        const selectedSpace = document.getElementById('polar-space-select')?.value || null;
        renderPolarChart('spacePolarChart', hourlyUsageData, 'Utilização por Dia', selectedSpace);

        const capacityDemandData = newData.scatter_graph_data || [];
        renderScatterChart('capacityDemandChart', capacityDemandData, 'Capacidade vs Demanda');
 
        const efficiencyData = newData.line_graph_data || [];
        renderLineChart('efficiencyChart', efficiencyData, 'Eficiência dos Espaços');
    }

    function populatePolarSpaceDropdown(data) {
        const polarDropdown = document.getElementById('polar-space-select');
        if (!polarDropdown) return;

        const uniqueSpaces = Array.from(new Set(
            data.map(item => item.classroom__name || item.classroom || item.nome_espaco)
                .filter(name => name && name.trim() !== '')
        )).sort();

        const currentValue = polarDropdown.value;
        
        while (polarDropdown.children.length > 1) {
            polarDropdown.removeChild(polarDropdown.lastChild);
        }

        uniqueSpaces.forEach(space => {
            const option = document.createElement('option');
            option.value = space;
            option.textContent = space;
            polarDropdown.appendChild(option);
        });

        if (currentValue && uniqueSpaces.includes(currentValue)) {
            polarDropdown.value = currentValue;
        }
    }

    let barChart, polarChart, scatterChart, lineChart;

    function renderBarChart(canvasId, data, title, labelX, labelY) {
        const canvas = document.getElementById(canvasId);
        canvas.width = canvas.parentElement.offsetWidth || 700;
        canvas.height = 400;
        const ctx = canvas.getContext('2d');
        if (barChart) barChart.destroy();
        const grouped = {};
        data.forEach(item => {
            const classroom = item.classroom__name || 'Outro';
            const subject = item.subject__name || 'Outro';
            if (!grouped[subject]) grouped[subject] = {};
            grouped[subject][classroom] = item.total_classes || 0;
        });
        const classrooms = Array.from(new Set(data.map(item => item.classroom__name || 'Outro')));
        const subjects = Object.keys(grouped);
        const datasets = subjects.map((subject, idx) => ({
            label: subject,
            data: classrooms.map(classroom => grouped[subject][classroom] || 0),
            backgroundColor: `hsl(${(idx * 60) % 360}, 70%, 60%)`,
            stack: 'Stack 0'
        }));
        barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: classrooms,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: title
                    },
                    legend: {
                        position: 'top',
                        labels: { boxWidth: 24, font: { size: 14 } }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                const subject = context.dataset.label;
                                const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
                                return `${subject}: ${Math.round(value)}`;
                            },
                            footer: function(context) {
                                const total = context.reduce((sum, item) => sum + (item.parsed.y || 0), 0);
                                return `Total: ${Math.round(total)}`;
                            }
                        }
                    }
                },
                layout: {
                    padding: 24
                },
                scales: {
                    x: { title: { display: true, text: labelX }, stacked: true, ticks: { font: { size: 14 } } },
                    y: { 
                        title: { display: true, text: labelY }, 
                        beginAtZero: true, 
                        stacked: true, 
                        ticks: { 
                            font: { size: 14 },
                            stepSize: 5,
                            callback: function(value) { return Number.isInteger(value) ? value : null; }
                        }
                    }
                }
            }
        });
    }

    function renderPolarChart(canvasId, data, title, selectedSpace) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        if (polarChart) polarChart.destroy();
        
        const weekDays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
        const dataByDay = Array(7).fill(0);
        let filtered = data;
        
    
        if (selectedSpace && selectedSpace.trim() !== '') {
            filtered = Array.isArray(data) ? data.filter(item => {
                const spaceName = item.classroom__name || item.classroom || item.nome_espaco;
                return spaceName === selectedSpace;
            }) : [];
        }
        
        if (Array.isArray(filtered)) {
            filtered.forEach(item => {
                if (item.day >= 0 && item.day < 7) {
                    dataByDay[item.day] = Math.round(item.total_classes || item.value || 0);
                }
            });
        }

        const chartTitle = selectedSpace && selectedSpace.trim() !== '' 
            ? `${title} - ${selectedSpace}` 
            : `${title} - Todas as Salas`;

        polarChart = new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: weekDays,
                datasets: [{
                    label: 'Aulas por Dia',
                    data: dataByDay,
                    backgroundColor: [
                        '#42a5f5', '#66bb6a', '#ffa726', '#ab47bc', '#ec407a', '#ff7043', '#26a69a'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: chartTitle },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = (typeof context.parsed === 'number') ? context.parsed : (typeof context.raw === 'number' ? context.raw : 0);
                                return `${context.label}: ${value} aulas`;
                            }
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 2,
                            callback: function(value) { return Number.isInteger(value) ? value : null; }
                        }
                    }
                }
            }
        });
    }

    function renderScatterChart(canvasId, data, title) {
        const canvas = document.getElementById(canvasId);
        const parent = canvas.parentElement;
        if (parent) {
            canvas.width = parent.offsetWidth || 700;
            canvas.height = parent.offsetHeight || 400;
        }
        const ctx = canvas.getContext('2d');
        if (scatterChart) scatterChart.destroy();
        scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: title,
                    data: data.map(item => ({ x: item.capacity || 0, y: item.demand || 0 })),
                    backgroundColor: 'rgba(59, 130, 246, 0.6)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: title
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Capacidade' } },
                    y: { title: { display: true, text: 'Demanda' } }
                }
            }
        });
    }

    function renderLineChart(canvasId, data, title) {
        const canvas = document.getElementById(canvasId);
        const parent = canvas.parentElement;
        if (parent) {
            canvas.width = parent.offsetWidth || 700;
            canvas.height = parent.offsetHeight || 400;
        }
        const ctx = canvas.getContext('2d');
        if (lineChart) lineChart.destroy();
        lineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.semester || item.label || ''),
                datasets: [{
                    label: title,
                    data: data.map(item => item.efficiency || item.value || 0),
                    fill: false,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: title
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Semestre' } },
                    y: { title: { display: true, text: 'Eficiência (%)' }, beginAtZero: true }
                }
            }
        });
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