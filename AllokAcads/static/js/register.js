document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('form');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const birthdateInput = document.getElementById('birthdate');
    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const birthdateError = document.getElementById('birthdateError');

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

    emailInput.addEventListener('input', () => {
        clearError(emailError);
        emailInput.classList.remove('error');
    });

    passwordInput.addEventListener('input', () => {
        clearError(passwordError);
        passwordInput.classList.remove('error');
    });

    birthdateInput.addEventListener('input', () => {
        clearError(birthdateError);
        birthdateInput.classList.remove('error');
    });

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        clearError(nameError);
        clearError(emailError);
        clearError(passwordError);
        clearError(birthdateError);
        
        let hasError = false;
        
        if (!nameInput.value.trim()) {
            showError(nameError, 'Por favor, insira seu nome completo');
            nameInput.classList.add('error');
            hasError = true;
        }
        
        if (!emailInput.value.trim()) {
            showError(emailError, 'Por favor, insira seu e-mail');
            emailInput.classList.add('error');
            hasError = true;
        } else if (!isValidEmail(emailInput.value)) {
            showError(emailError, 'Por favor, insira um e-mail válido');
            emailInput.classList.add('error');
            hasError = true;
        }
        
        if (!passwordInput.value.trim()) {
            showError(passwordError, 'Por favor, insira sua senha');
            passwordInput.classList.add('error');
            hasError = true;
        } else if (passwordInput.value.length < 6) {
            showError(passwordError, 'A senha deve ter pelo menos 6 caracteres');
            passwordInput.classList.add('error');
            hasError = true;
        }
        
        if (!birthdateInput.value) {
            showError(birthdateError, 'Por favor, insira sua data de nascimento');
            birthdateInput.classList.add('error');
            hasError = true;
        }
        
        if (hasError) return;

        try {
            const formData = new FormData(registerForm);
            const response = await fetch('/AllokAcad/register_validate', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                window.location.href = '/AllokAcad/register';
            }

        } catch (error) {
            showError(nameError, 'Erro ao conectar ao servidor. Tente novamente.');
        }
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});

