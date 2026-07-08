document.addEventListener('DOMContentLoaded', function() {
    
    // Configurações globais do Chart.js
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.color = '#475569';
    
    // Inicialização das variáveis dos gráficos
    let radarChart = null;
    let barChart = null;
    let failureChart = null;
    let resourcesChart = null;
    
    // Parsing dos dados embutidos
    const filterOptionsData = JSON.parse(document.getElementById('filter-options-data').textContent || '{}');
    let metricsData = JSON.parse(document.getElementById('metrics-data').textContent || '{}');
    let failureData = JSON.parse(document.getElementById('failure-reasons-data').textContent || '{}');
    const operationalData = JSON.parse(document.getElementById('operational-metrics-data').textContent || '{}');
    
    const filterTypeSelect = document.getElementById('filter-type-select');
    const filterIdSelect = document.getElementById('filter-id-select');
    const updateBtn = document.getElementById('update-preferences-btn');
    const ambientSelect = document.getElementById('ambient-select');
    
    const generateBtn = document.getElementById('generate-insights-btn');
    const loadingDiv = document.getElementById('insights-loading');
    const contentDiv = document.getElementById('insights-content');
    
    const metricAvgQuality = document.getElementById('metric-avg-quality');
    const metricFailures = document.getElementById('metric-failures');
    
    // Labels bonitas para as métricas
    const metricLabels = {
        'turma_professor': 'Turma/Professor',
        'turma_horario': 'Turma/Horário',
        'turma_sala': 'Turma/Sala',
        'professor_horario': 'Prof./Horário',
        'professor_disciplina': 'Prof./Disciplina',
        'disciplina_sala': 'Disciplina/Sala',
        'disciplina_professor': 'Disciplina/Prof.'
    };
    
    // Atualiza opções do select secundário com base no tipo
    function updateFilterOptions() {
        const type = filterTypeSelect.value;
        filterIdSelect.innerHTML = '<option value="">Selecione...</option>';
        
        if (!type) {
            filterIdSelect.disabled = true;
            return;
        }
        
        filterIdSelect.disabled = false;
        
        let options = [];
        if (type === 'turma') options = filterOptionsData.turmas || [];
        else if (type === 'professor') options = filterOptionsData.professores || [];
        else if (type === 'sala') options = filterOptionsData.salas || [];
        else if (type === 'disciplina') options = filterOptionsData.disciplinas || [];
        
        options.forEach(opt => {
            const el = document.createElement('option');
            el.value = opt.id;
            el.textContent = opt.name;
            filterIdSelect.appendChild(el);
        });
    }
    
    filterTypeSelect.addEventListener('change', updateFilterOptions);
    
    // Atualiza indicadores numéricos
    function updateIndicators(metrics, failures) {
        // Média de qualidade
        let total = 0, count = 0;
        for (const val of Object.values(metrics)) {
            total += val;
            count++;
        }
        const avg = count > 0 ? (total / count).toFixed(1) : 0;
        metricAvgQuality.textContent = `${avg}%`;
        
        // Total de falhas
        let totalFailures = 0;
        for (const val of Object.values(failures)) {
            totalFailures += val;
        }
        metricFailures.textContent = totalFailures;
    }
    
    // Inicializa e atualiza o gráfico Radar
    function renderRadarChart(data) {
        const ctx = document.getElementById('preferencesRadarChart').getContext('2d');
        
        const labels = Object.keys(data).map(k => metricLabels[k]);
        const values = Object.values(data);
        
        if (radarChart) {
            radarChart.data.datasets[0].data = values;
            radarChart.update();
            return;
        }
        
        radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Qualidade de Atendimento (%)',
                    data: values,
                    backgroundColor: 'rgba(67, 97, 238, 0.2)',
                    borderColor: 'rgba(67, 97, 238, 1)',
                    pointBackgroundColor: 'rgba(67, 97, 238, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(67, 97, 238, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' },
                        pointLabels: {
                            font: { size: 12, weight: 'bold' }
                        },
                        min: 0,
                        max: 100,
                        ticks: { stepSize: 20 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
    
    // Inicializa e atualiza o gráfico de Barras
    function renderBarChart(data) {
        const ctx = document.getElementById('preferencesBarChart').getContext('2d');
        
        const labels = Object.keys(data).map(k => metricLabels[k]);
        const values = Object.values(data);
        
        // Cores baseadas no valor
        const bgColors = values.map(v => v >= 80 ? 'rgba(16, 185, 129, 0.7)' : (v >= 50 ? 'rgba(245, 158, 11, 0.7)' : 'rgba(239, 68, 68, 0.7)'));
        
        if (barChart) {
            barChart.data.datasets[0].data = values;
            barChart.data.datasets[0].backgroundColor = bgColors;
            barChart.update();
            return;
        }
        
        barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Atendimento (%)',
                    data: values,
                    backgroundColor: bgColors,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {
                    x: { min: 0, max: 100 }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // Inicializa e atualiza o gráfico de Motivos de Falha (Donut)
    function renderFailureChart(data) {
        const ctx = document.getElementById('failureReasonsChart').getContext('2d');
        
        let labels = Object.keys(data);
        const values = Object.values(data);
        
        const total = values.reduce((sum, val) => sum + val, 0);
        if (total > 0) {
            labels = labels.map((label, index) => {
                const percentage = Math.round((values[index] / total) * 100);
                return `${label} - ${percentage}%`;
            });
        }
        
        if (failureChart) {
            failureChart.data.labels = labels;
            failureChart.data.datasets[0].data = values;
            failureChart.update();
            return;
        }
        
        failureChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: [
                        '#ef4444', '#f97316', '#eab308', '#84cc16', 
                        '#06b6d4', '#3b82f6', '#8b5cf6', '#d946ef'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' }
                }
            }
        });
    }

    // Gráfico de adequação de recursos (Barras simples)
    function renderResourcesChart(opData) {
        const ctx = document.getElementById('resourcesChart').getContext('2d');
        
        if (resourcesChart) return; // Não atualiza pois estes dados não mudam com o filtro
        
        resourcesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Professores', 'Salas', 'Atividades (Demanda)'],
                datasets: [{
                    label: 'Quantidade',
                    data: [opData.professors, opData.classrooms, opData.activities],
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b'],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }
    
    // Atualiza dados via AJAX ao clicar em Atualizar
    updateBtn.addEventListener('click', function() {
        const ambient = ambientSelect.value;
        const filterType = filterTypeSelect.value;
        const filterId = filterIdSelect.value;
        
        if (filterType && !filterId) {
            alert('Por favor, selecione um item específico para filtrar.');
            return;
        }
        
        const originalText = updateBtn.innerHTML;
        updateBtn.innerHTML = 'Atualizando...';
        updateBtn.disabled = true;
        
        fetch(`/dashboard/api/update-preferences-data/?ambient=${ambient}&filter_type=${filterType}&filter_id=${filterId}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                
                metricsData = data.metrics;
                failureData = data.failure_reasons;
                
                renderRadarChart(metricsData);
                renderBarChart(metricsData);
                renderFailureChart(failureData);
                updateIndicators(metricsData, failureData);
            })
            .catch(err => {
                console.error(err);
                alert('Erro ao buscar dados.');
            })
            .finally(() => {
                updateBtn.innerHTML = originalText;
                updateBtn.disabled = false;
            });
    });
    
    // Geração de Insights via IA
    generateBtn.addEventListener('click', function() {
        const ambient = ambientSelect.value;
        const filterType = filterTypeSelect.value;
        const filterId = filterIdSelect.value;
        
        generateBtn.disabled = true;
        loadingDiv.classList.remove('hidden');
        contentDiv.innerHTML = '';
        
        fetch('/dashboard/api/generate-insights/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                ambient_id: ambient,
                filter_type: filterType,
                filter_id: filterId
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) throw new Error(data.response);
            
            // Renderiza o markdown
            contentDiv.innerHTML = marked.parse(data.response);
        })
        .catch(err => {
            contentDiv.innerHTML = `<p class="text-muted" style="color: red;">Erro ao gerar insight: ${err.message}</p>`;
        })
        .finally(() => {
            generateBtn.disabled = false;
            loadingDiv.classList.add('hidden');
        });
    });
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Inicialização ao carregar a página
    updateIndicators(metricsData, failureData);
    renderRadarChart(metricsData);
    renderBarChart(metricsData);
    renderFailureChart(failureData);
    renderResourcesChart(operationalData);
});
