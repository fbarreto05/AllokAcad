document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('picture');
    const fileNameDisplay = document.querySelector('.file-name');
    
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
            }
        });
    }
    
    const formOpening = document.getElementById('form_opening');
    const formClosing = document.getElementById('form_closing');
    const altOpening = document.getElementById('alt_solicitations_opening');
    const altClosing = document.getElementById('alt_solicitations_closing');
    
    if (formClosing) {
        formClosing.addEventListener('change', function() {
            if (formOpening.value && new Date(this.value) < new Date(formOpening.value)) {
                alert('A data de fechamento do formulário não pode ser anterior à data de abertura.');
                this.value = formOpening.value;
            }
        });
    }
    
    if (altClosing) {
        altClosing.addEventListener('change', function() {
            if (altOpening.value && new Date(this.value) < new Date(altOpening.value)) {
                alert('A data de fechamento para contestação não pode ser anterior à data de abertura.');
                this.value = altOpening.value;
            }
        });
    }
    
    const minDay = document.getElementById('min_actv_in_a_day');
    const maxDay = document.getElementById('max_actv_in_a_day');
    const minCicle = document.getElementById('min_actv_in_a_cicle');
    const maxCicle = document.getElementById('max_actv_in_a_cicle');
    
    if (maxDay) {
        maxDay.addEventListener('change', function() {
            if (parseInt(this.value) < parseInt(minDay.value)) {
                alert('O máximo de atividades por dia não pode ser menor que o mínimo.');
                this.value = minDay.value;
            }
        });
    }
    
    if (maxCicle) {
        maxCicle.addEventListener('change', function() {
            if (parseInt(this.value) < parseInt(minCicle.value)) {
                alert('O máximo de atividades por ciclo não pode ser menor que o mínimo.');
                this.value = minCicle.value;
            }
        });
    }
    
    const form = document.querySelector('.config-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const confirmed = confirm('Tem certeza que deseja salvar as alterações nas configurações do ambiente?');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    }
});