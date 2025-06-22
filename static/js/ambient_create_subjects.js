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
        const container = checkbox.closest('.item-with-weight');
        if (container) {
            const relatedSlider = container.querySelector('input[type="range"]');
            
            checkbox.addEventListener('change', function() {
                if (relatedSlider) {
                    relatedSlider.disabled = !this.checked;
                    if (!this.checked) {
                        relatedSlider.value = 100;
                        relatedSlider.nextElementSibling.textContent = '100%';
                    }
                }
            });
            
            if (relatedSlider) {
                relatedSlider.disabled = !checkbox.checked;
            }
        }
    });
});
