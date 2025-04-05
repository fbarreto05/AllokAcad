document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const identifierInput = document.getElementById('identifier');
    const passwordInput = document.getElementById('password');
    const identifierError = document.getElementById('identifierError');
    const passwordError = document.getElementById('passwordError');

    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function clearError(element) {
        element.textContent = '';
        element.style.display = 'none';
    }

    identifierInput.addEventListener('input', () => {
        clearError(identifierError);
        identifierInput.classList.remove('error');
    });

    passwordInput.addEventListener('input', () => {
        clearError(passwordError);
        passwordInput.classList.remove('error');
    });

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        clearError(identifierError);
        clearError(passwordError);
        
        let hasError = false;
        
        if (!identifierInput.value.trim()) {
            showError(identifierError, 'Por favor, insira seu identificador');
            identifierInput.classList.add('error');
            hasError = true;
        }
        
        if (!passwordInput.value.trim()) {
            showError(passwordError, 'Por favor, insira sua senha');
            passwordInput.classList.add('error');
            hasError = true;
        }
        
        if (hasError) return;

        try {
            const response = await fetch('/AllokAcad/login_validate', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    'id': identifierInput.value.trim(),
                    'password': passwordInput.value
                })
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                window.location.href = '/AllokAcad/login';
            }

        } catch (error) {
            showError(identifierError, 'Erro ao conectar ao servidor. Tente novamente.');
        }
    });
});