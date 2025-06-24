document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('form');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const birthdateInput = document.getElementById('birthdate');
    const nameError = document.getElementById('nameError');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const birthdateError = document.getElementById('birthdateError');    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function clearError(element) {
        element.textContent = '';
        element.style.display = 'none';
    }

    function showSuccessMessage(message) {
        const existingSuccess = document.querySelector('.success-message');
        if (existingSuccess) {
            existingSuccess.remove();
        }

        const successElement = document.createElement('div');
        successElement.className = 'success-message';
        successElement.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            ${message}
        `;

        const formContainer = document.querySelector('.form-container');
        const form = document.querySelector('form');
        formContainer.insertBefore(successElement, form);

        setTimeout(() => {
            if (successElement && successElement.parentNode) {
                successElement.remove();
            }
        }, 3000);
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
        } else if (nameInput.value.trim().length < 5) {
            showError(nameError, 'O nome deve ter pelo menos 5 caracteres');
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

        const submitButton = document.querySelector('.register-button');
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<svg width="16" height="16" fill="currentColor" class="loading-spinner" viewBox="0 0 16 16"><path d="M8 3.5a.5.5 0 0 1 .5.5v3.793l2.146-2.147a.5.5 0 0 1 .708.708L8.707 8.5H12.5a.5.5 0 0 1 0 1H8.707l2.647 2.646a.5.5 0 0 1-.708.708L8.5 10.707V14.5a.5.5 0 0 1-1 0v-3.793L5.354 12.854a.5.5 0 1 1-.708-.708L7.293 9.5H3.5a.5.5 0 0 1 0-1h3.793L5.146 6.354a.5.5 0 1 1 .708-.708L7.5 7.293V3.5a.5.5 0 0 1 .5-.5z"/></svg> Criando conta...';
        submitButton.disabled = true;

        try {
            const formData = new FormData(registerForm);
            const response = await fetch('/register_validate', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: formData
            });            if (response.redirected || response.url.includes('/?new_user=')) {
                showSuccessMessage('Conta criada com sucesso! Redirecionando para o login...');
                
                setTimeout(() => {
                    window.location.href = response.url || '/';
                }, 2000);
            } else if (response.ok) {
                showSuccessMessage('Conta criada com sucesso! Redirecionando para o login...');
                
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
                showError(nameError, 'Erro ao criar conta. Tente novamente.');
            }

        } catch (error) {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
            showError(nameError, 'Erro ao conectar ao servidor. Tente novamente.');
        }
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});