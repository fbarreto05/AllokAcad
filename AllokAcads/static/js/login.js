document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const identifierInput = document.getElementById('identifier');
    const passwordInput = document.getElementById('password');
    const identifierError = document.getElementById('identifierError');
    const passwordError = document.getElementById('passwordError');
    const togglePassword = document.querySelector('.toggle-password');
    const eyeIcon = document.querySelector('.eye-icon');
    const eyeOffIcon = document.querySelector('.eye-off-icon');

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

    if (togglePassword) {
        togglePassword.addEventListener('click', function() {

            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            if (type === 'password') {
                eyeIcon.style.display = 'block';
                eyeOffIcon.style.display = 'none';
            } else {
                eyeIcon.style.display = 'none';
                eyeOffIcon.style.display = 'block';
            }
            
            passwordInput.focus();
        });
    }

    function validateForm() {
        let isValid = true;

        if (!identifierInput.value.trim()) {
            identifierError.textContent = 'O identificador é obrigatório';
            identifierInput.classList.add('error');
            isValid = false;
        } else {
            identifierError.textContent = '';
            identifierInput.classList.remove('error');
        }

        if (!passwordInput.value) {
            passwordError.textContent = 'A senha é obrigatória';
            passwordInput.classList.add('error');
            isValid = false;
        } else {
            passwordError.textContent = '';
            passwordInput.classList.remove('error');
        }

        return isValid;
    }

    identifierInput.addEventListener('input', function() {
        identifierError.textContent = '';
        identifierInput.classList.remove('error');
    });

    passwordInput.addEventListener('input', function() {
        passwordError.textContent = '';
        passwordInput.classList.remove('error');
    });

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault(); 
            }
        });
    }

    if (window.location.href.includes('/login') && document.referrer.includes('/login')) {

        const errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        errorElement.textContent = 'Identificador ou senha incorretos. Tente novamente.';
        
        const formContainer = document.querySelector('.form-container');
        if (formContainer && loginForm) {
            formContainer.insertBefore(errorElement, loginForm);
        }
    }

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
            const response = await fetch('/login_validate', { 
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
                window.location.href = '/login';
            }

        } catch (error) {
            showError(identifierError, 'Erro ao conectar ao servidor. Tente novamente.');
        }
    });
});