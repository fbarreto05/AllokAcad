document.addEventListener('DOMContentLoaded', function () {
    const ambientSelect = document.getElementById('ambient-select');
    const updateButton = document.getElementById('update-button');
    const toggleMedianLine = document.getElementById('toggle-median-line');

    let lastProfessorData = null;
    let lastMedianValue = null;

    updateButton.addEventListener('click', () => {
        const ambientId = ambientSelect.value;
        updateDashboardData(ambientId);
    });
    
    ambientSelect.addEventListener('change', () => {
        const ambientId = ambientSelect.value;
        updateDashboardData(ambientId);
    });

    if (toggleMedianLine) {
        toggleMedianLine.addEventListener('change', () => {
           
            renderProfessorBarChart(lastProfessorData, lastMedianValue, toggleMedianLine.checked);
        });
    }

    async function updateDashboardData(ambientId) {
        const indicators = [
            '#metric-avg-interval .metric-value',
            '#metric-avg-classes .metric-value',
            '#metric-num-professors .metric-value',
            '#metric-timetable-quality .metric-value'
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
                { selector: '#metric-avg-interval .metric-value', value: newData.indicators.average_class_interval },
                { selector: '#metric-avg-classes .metric-value', value: newData.indicators.average_classes },
                { selector: '#metric-num-professors .metric-value', value: newData.indicators.number_of_professors },
                { selector: '#metric-timetable-quality .metric-value', value: newData.indicators.timetable_quality }
            ];
            updates.forEach(update => {
                const element = document.querySelector(update.selector);
                if (element) {
                    element.textContent = update.value !== null && update.value !== undefined ? update.value : '--';
                    element.classList.remove('loading');
                }
            });

            if (newData.bar_graph_data) {
                lastProfessorData = newData.bar_graph_data;
                lastMedianValue = newData.median_professor_periods;
                renderProfessorBarChart(lastProfessorData, lastMedianValue, toggleMedianLine ? toggleMedianLine.checked : true);
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

    function renderProfessorBarChart(professorData, medianValue, showMedianLine = true) {
        if (!professorData) return;
        lastProfessorData = professorData;
        lastMedianValue = medianValue;
        const ctx = document.getElementById('professorBarChart').getContext('2d');
        if (window.professorBarChartInstance) {
            window.professorBarChartInstance.destroy();
        }
        const labels = professorData.map(item => item.professor__user__name);
        const data = professorData.map(item => item.periods_list);
      
        let annotationConfig = {};
        if (typeof medianValue === 'undefined') {
            const professorMedianDataScript = document.getElementById('professor-median-data');
            if (professorMedianDataScript) {
                try {
                    medianValue = JSON.parse(professorMedianDataScript.textContent);
                } catch (e) {
                    medianValue = null;
                }
            }
        }
        if (showMedianLine && medianValue !== null && medianValue !== undefined) {
            annotationConfig = {
                annotation: {
                    annotations: {
                        medianLine: {
                            type: 'line',
                            yMin: medianValue,
                            yMax: medianValue,
                            borderColor: 'red',
                            borderWidth: 2,
                            label: {
                                content: 'Mediana',
                                enabled: true,
                                position: 'end',
                                color: 'red',
                                backgroundColor: 'white',
                                font: { weight: 'bold' }
                            }
                        }
                    }
                }
            };
        }
        
        window.professorBarChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Média de Aulas por Professor',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Média de Aulas por Professor' },
                    ...annotationConfig
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

 
    const professorBarDataScript = document.getElementById('professor-bar-data');
    const professorMedianDataScript = document.getElementById('professor-median-data');

    if (professorBarDataScript) {
        try {
            const professorData = JSON.parse(professorBarDataScript.textContent);
            let medianValue = null;
            if (professorMedianDataScript) {
                medianValue = JSON.parse(professorMedianDataScript.textContent);
            }
            lastProfessorData = professorData;
            lastMedianValue = medianValue;
            renderProfessorBarChart(professorData, medianValue, toggleMedianLine ? toggleMedianLine.checked : true);
        } catch (e) {
            console.error('Erro ao carregar dados do gráfico de professores:', e);
        }
    }

    const heatmapDataScript = document.getElementById('professor-heatmap-data');
    let heatmapData = [];
    if (heatmapDataScript) {
        try {
           
            heatmapData = JSON.parse(heatmapDataScript.textContent);
        } catch (e) {
            heatmapData = [];
        }
    }
    
    const dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"];
    const periodos = [1,2,3,4,5,6]; 
    if (document.getElementById('professorHeatmap')) {
        const ctxHeatmap = document.getElementById('professorHeatmap').getContext('2d');
        new Chart(ctxHeatmap, {
            type: 'matrix',
            data: {
                datasets: [{
                    label: 'Aulas por Dia/Período',
                    data: heatmapData,
                    backgroundColor: function(ctx) {
                        const value = ctx.dataset.data[ctx.dataIndex].v;
                        if (value === 0) return '#e0e0e0';
                        if (value === 1) return '#90caf9';
                        if (value === 2) return '#42a5f5';
                        if (value === 3) return '#1976d2';
                        return '#0d47a1';
                    },
                    width: ({chart}) => (chart.chartArea || {}).width / dias.length - 2,
                    height: ({chart}) => (chart.chartArea || {}).height / periodos.length - 2,
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Heatmap de Horários' },
                    tooltip: {
                        callbacks: {
                            title: (items) => {
                                const item = items[0];
                                return dias[item.raw.x] + ' - Período ' + periodos[item.raw.y];
                            },
                            label: (item) => `Aulas: ${item.raw.v}`
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        labels: dias,
                        offset: true,
                        grid: { display: false },
                        title: { display: true, text: 'Dia da Semana' }
                    },
                    y: {
                        type: 'category',
                        labels: periodos,
                        offset: true,
                        grid: { display: false },
                        title: { display: true, text: 'Período' }
                    }
                }
            }
        });
    }
});