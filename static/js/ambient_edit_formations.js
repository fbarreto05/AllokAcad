document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.querySelector('.edit-formations-form');
    const nameInput = document.getElementById('name');
    const nameError = document.getElementById('nameError');

    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function clearError(element) {
        element.textContent = '';
        element.style.display = 'none';
    }

    nameInput.addEventListener('input', () => {
        clearError(nameError);
        nameInput.classList.remove('error');
    });

    editForm.addEventListener('submit', function(e) {
        clearError(nameError);
        
        let hasError = false;
        
        if (!nameInput.value.trim()) {
            showError(nameError, 'Por favor, insira o nome da formação');
            nameInput.classList.add('error');
            hasError = true;
        } else if (nameInput.value.trim().length > 40) {
            showError(nameError, 'O nome da formação deve ter no máximo 40 caracteres');
            nameInput.classList.add('error');
            hasError = true;
        }
        
        if (hasError) {
            e.preventDefault();
            nameInput.focus();
            return;
        }
    });
});