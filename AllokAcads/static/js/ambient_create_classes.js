document.addEventListener('DOMContentLoaded', function() {

    const weightSliders = document.querySelectorAll('.weight-slider');
    weightSliders.forEach(slider => {
        const valueSpan = slider.nextElementSibling;
        
        valueSpan.textContent = slider.value + '%';
        
        slider.addEventListener('input', function() {
            valueSpan.textContent = this.value + '%';
        });
    });
    
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        const container = checkbox.closest('.item-with-weight, .subject-item');
        if (container) {
            const relatedInputs = container.querySelectorAll('input[type="range"], input[type="number"]');
            
            checkbox.addEventListener('change', function() {
                relatedInputs.forEach(input => {
                    input.disabled = !this.checked;
                    if (!this.checked) {
                        if (input.type === 'range') {
                            input.value = 100;
                            const valueSpan = input.nextElementSibling;
                            if (valueSpan) {
                                valueSpan.textContent = '100%';
                            }
                        } else if (input.type === 'number') {
                            input.value = '';
                        }
                    }
                });
            });
            
            relatedInputs.forEach(input => {
                input.disabled = !checkbox.checked;
            });
        }
    });
});
