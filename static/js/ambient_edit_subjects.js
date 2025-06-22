document.addEventListener('DOMContentLoaded', function() {

    const weightSliders = document.querySelectorAll('.weight-slider');
    
    weightSliders.forEach(slider => {
        const weightValueSpan = slider.parentNode.querySelector('.weight-value');
        
        if (weightValueSpan) {
            weightValueSpan.textContent = slider.value + '%';
        }
        
        slider.addEventListener('input', function() {
            if (weightValueSpan) {
                weightValueSpan.textContent = this.value + '%';
            }
        });
    });
    
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    checkboxes.forEach(checkbox => {
        const container = checkbox.closest('.item-with-weight');
        if (container) {
            const slider = container.querySelector('.weight-slider');
            
            function updateSliderState() {
                if (slider) {
                    slider.disabled = !checkbox.checked;
                }
            }
            
            updateSliderState();
            
            checkbox.addEventListener('change', updateSliderState);
        }
    });
    
    const formSections = document.querySelectorAll('.form-section');
    
    formSections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    const form = document.querySelector('.edit-subjects-form');
    const nameInput = document.querySelector('#name');
    
    if (form && nameInput) {
        form.addEventListener('submit', function(e) {
            if (nameInput.value.trim() === '') {
                e.preventDefault();
                nameInput.focus();
                nameInput.style.borderColor = '#dc3545';
                
                nameInput.addEventListener('input', function() {
                    this.style.borderColor = '';
                }, { once: true });
            }
        });
    }
    
    const messages = document.querySelectorAll('.messages .alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });
});
