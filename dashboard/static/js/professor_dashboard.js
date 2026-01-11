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
                element.textContent = '--';
                element.classList.remove('loading', 'error');
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
            if (newData.polar_graph_data && typeof renderPolarChart === 'function') {
                const polarProfessorSelect = document.getElementById('polar-professor-select');
                if (polarProfessorSelect) {
                    renderPolarChart(newData.polar_graph_data, polarProfessorSelect.value);
                }
            }
            if (newData.line_graph_data && typeof renderProfessorLineChart === 'function') {
                renderProfessorLineChart(newData.line_graph_data);
            }
            if (newData.scatter_graph_data && typeof renderProfessorEfficiencyChart === 'function') {
                renderProfessorEfficiencyChart(newData.scatter_graph_data);
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
    function renderProfessorBarChart(professorData) {
        if (!professorData || professorData.length === 0) return;
        lastProfessorData = professorData;
        const ctx = document.getElementById('professorBarChart').getContext('2d');
        if (window.professorBarChartInstance) {
            window.professorBarChartInstance.destroy();
        }

        const getProfessor = item => item.professor__user__name || item.professor || item.nome_professor || 'Indefinido';
        const getSubject = item => item.subject__name || item.subject || item.nome_materia || 'Indefinido';

        const professors = [...new Set(professorData.map(getProfessor))];
        const subjects = [...new Set(professorData.map(getSubject))];

        const dataMap = {};
        professorData.forEach(item => {
            const subject = getSubject(item);
            const professor = getProfessor(item);
            if (!dataMap[subject]) dataMap[subject] = {};
            dataMap[subject][professor] = item.total_classes;
        });

        const datasets = subjects.map((subject, idx) => ({
            label: subject,
            data: professors.map(prof => dataMap[subject][prof] || 0),
            backgroundColor: `hsl(${(idx * 60) % 360}, 60%, 60%)`,
            borderColor: `hsl(${(idx * 60) % 360}, 60%, 40%)`,
            borderWidth: 1,
            stack: 'aulas'
        }));

        window.professorBarChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: professors,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Aulas por Professor' },
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
                scales: {
                    x: { stacked: true, grid: { display: false } },
                    y: {
                        beginAtZero: true,
                        stacked: true,
                        ticks: {
                            stepSize: 5,
                            callback: function(value) { return Number.isInteger(value) ? value : null; }
                        },
                        grid: { display: false }
                    }
                }
            }
        });
    }
    const professorBarDataScript = document.getElementById('professor-bar-data');
    if (professorBarDataScript) {
        try {
            const professorData = JSON.parse(professorBarDataScript.textContent);
            lastProfessorData = professorData;
            renderProfessorBarChart(professorData);
        } catch (e) {
            console.error('Erro ao carregar dados do gráfico de professores:', e);
        }
    }

    function renderPolarChart(polarData, selectedProfessor) {
        const ctx = document.getElementById('polarChart').getContext('2d');
        if (window.polarChartInstance) {
            window.polarChartInstance.destroy();
        }
        const weekDays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
        const filtered = Array.isArray(polarData) ? polarData.filter(item => {
            const name = item.professor__user__name || item.professor || item.nome_professor;
            return name === selectedProfessor;
        }) : [];
        const dataByDay = Array(7).fill(0);
        filtered.forEach(item => {
            if (item.day >= 0 && item.day < 7) {
                dataByDay[item.day] = Math.round(item.total_classes || item.total_periods || 0);
            }
        });
        window.polarChartInstance = new Chart(ctx, {
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
                    title: { display: true, text: 'Distribuição de Aulas por Dia da Semana' },
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

    const polarDataScript = document.getElementById('polar-graph-data');
    const polarProfessorSelect = document.getElementById('polar-professor-select');
    if (polarDataScript) {
        try {
            polarData = JSON.parse(polarDataScript.textContent);
            console.log('polarData:', polarData);
            if (polarProfessorSelect) {
                console.log('Professores disponíveis:', Array.from(polarProfessorSelect.options).map(o => o.value));
                console.log('Professor selecionado:', polarProfessorSelect.value);
            }
            if (polarProfessorSelect && Array.isArray(polarData) && polarData.length > 0) {
                renderPolarChart(polarData, polarProfessorSelect.value);
                polarProfessorSelect.addEventListener('change', function() {
                    renderPolarChart(polarData, this.value);
                });
            }
        } catch (e) {
            console.error('Erro ao carregar dados do gráfico polar:', e);
        }
    }

    function renderProfessorLineChart(lineData) {
        const ctx = document.getElementById('professorLineChart').getContext('2d');
        const parent = document.getElementById('professorLineChart').parentElement;
        if (parent) {
            document.getElementById('professorLineChart').width = parent.offsetWidth || 700;
            document.getElementById('professorLineChart').height = parent.offsetHeight || 400;
        }
        if (window.professorLineChartInstance) {
            window.professorLineChartInstance.destroy();
        }
        if (!Array.isArray(lineData) || lineData.length === 0) return;
        const labels = lineData.map(item => item.semester__name);
        const datasets = [
            {
                label: 'Períodos no Campus',
                data: lineData.map(item => item.avg_periods_on_campus),
                borderColor: '#42a5f5',
                backgroundColor: 'rgba(66,165,245,0.1)',
                fill: false,
                tension: 0.2
            },
            {
                label: 'Intervalos de Períodos',
                data: lineData.map(item => item.avg_periods_interval),
                borderColor: '#66bb6a',
                backgroundColor: 'rgba(102,187,106,0.1)',
                fill: false,
                tension: 0.2
            },
            {
                label: 'Nº de Períodos',
                data: lineData.map(item => item.avg_number_of_periods),
                borderColor: '#ffa726',
                backgroundColor: 'rgba(255,167,38,0.1)',
                fill: false,
                tension: 0.2
            },
            {
                label: 'Eficiência Diária',
                data: lineData.map(item => item.avg_day_efficiency),
                borderColor: '#ab47bc',
                backgroundColor: 'rgba(171,71,188,0.1)',
                fill: false,
                tension: 0.2
            }
        ];
        window.professorLineChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' },
                    title: { display: true, text: 'Evolução das Métricas dos Professores por Semestre' }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
    
    const professorLineDataScript = document.getElementById('professor-line-data');
    if (professorLineDataScript) {
        try {
            const lineData = JSON.parse(professorLineDataScript.textContent);
            renderProfessorLineChart(lineData);
        } catch (e) {
            console.error('Erro ao carregar dados do gráfico de linha:', e);
        }
    }
    
    function renderProfessorEfficiencyChart(professorData) {
        const ctx = document.getElementById('scatterChart').getContext('2d');
        const parent = document.getElementById('scatterChart').parentElement;
        if (parent) {
            document.getElementById('scatterChart').width = parent.offsetWidth || 700;
            document.getElementById('scatterChart').height = parent.offsetHeight || 400;
        }

        if (window.scatterChartInstance) {
            window.scatterChartInstance.destroy();
        }

        const dataPoints = professorData.map(item => ({
            x: item.total_classes,
            y: item.avg_day_efficiency, 
            professor: item.professor__user__name || 'Exemplo' 
        
        }));

        window.scatterChartInstance = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Eficiência', 
                    data: dataPoints,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    pointRadius: 6,
                    pointHoverRadius: 9
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false 
                    },
                    title: {
                        display: true,
                        text: 'Eficiência Média X Total de Aulas por Professor', 
                        font: {
                            size: 18
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                
                                const rawData = context.raw;
                                const professorName = rawData.professor;
                                const totalClasses = rawData.x;
                                const avgEfficiency = rawData.y;

                               
                                return `${professorName}: ${totalClasses} aulas, ${avgEfficiency.toFixed(2)}% de eficiência`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Total de Aulas', 
                            font: {
                                size: 14
                            }
                        },
                        ticks: {
                            stepSize: 5,
                            callback: function(value) {
                                return Number.isInteger(value) ? value : null;
                            }
                        },
                        min: 0
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Eficiência Média (%)', 
                            font: {
                                size: 14
                            }
                        },
                        min: 0,
                    }
                }
            }
        });
    }
    
    const professorScatterDataScript = document.getElementById('professor-scatter-data');
    if (professorScatterDataScript) {
        try {
            const scatterData = JSON.parse(professorScatterDataScript.textContent);
            renderProfessorEfficiencyChart(scatterData);
        } catch (e) {
            console.error('Erro ao carregar dados do gráfico de dispersão:', e);
        }
    }

    if (ambientSelect && ambientSelect.options.length > 0) {
        const firstAmbientId = ambientSelect.options[0].value;
        ambientSelect.value = firstAmbientId;
        updateDashboardData(firstAmbientId);
    }
});
