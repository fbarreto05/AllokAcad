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
    function removeLoginError() {
        const existingLoginError = document.querySelector('.form-error');
        if (existingLoginError) {
            existingLoginError.remove();
        }
    }

    identifierInput.addEventListener('input', () => {
        clearError(identifierError);
        identifierInput.classList.remove('error');
        removeLoginError();
    });

    passwordInput.addEventListener('input', () => {
        clearError(passwordError);
        passwordInput.classList.remove('error');
        removeLoginError();
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
    }    function validateForm() {
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

        return isValid;    }
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('error') === 'login_failed') {
        const errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        errorElement.textContent = 'Identificador ou senha incorretos. Tente novamente.';
        
        const formContainer = document.querySelector('.form-container');
        if (formContainer && loginForm) {
            formContainer.insertBefore(errorElement, loginForm);
        }
    }

    const newUserId = urlParams.get('new_user');
    if (newUserId === 'true') {
        const userData = {
            userid: urlParams.get('userid'),
            name: urlParams.get('name'),
            email: urlParams.get('email'),
            birthdate: urlParams.get('birthdate')
        };
        showWelcomeModal(userData);
    }

    if (urlParams.has('error') || urlParams.has('new_user')) {
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
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
                window.location.href = '/';
            }        } catch (error) {
            showError(identifierError, 'Erro ao conectar ao servidor. Tente novamente.');
        }    });

    function showWelcomeModal(userData) {
        const modal = document.getElementById('welcomeModal');
        const userIdElement = document.getElementById('welcomeUserId');
        const userNameElement = document.getElementById('welcomeUserName');
        const userEmailElement = document.getElementById('welcomeUserEmail');
        const userBirthdateElement = document.getElementById('welcomeUserBirthdate');
        
        userIdElement.textContent = userData.userid;
        userNameElement.textContent = userData.name || 'Não informado';
        userEmailElement.textContent = userData.email || 'Não informado';
        userBirthdateElement.textContent = userData.birthdate || 'Não informado';
        
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        const copyBtn = document.getElementById('copyUserIdBtn');
        copyBtn.addEventListener('click', function() {
            copyToClipboard(userData.userid);
        });
        
        const understoodBtn = document.getElementById('understoodBtn');
        understoodBtn.addEventListener('click', function() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            
            const identifierInput = document.getElementById('identifier');
            if (identifierInput) {
                identifierInput.value = userData.userid;
                identifierInput.focus();
            }
        });
    }

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            const copyBtn = document.getElementById('copyUserIdBtn');
            const originalContent = copyBtn.innerHTML;
            
            copyBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <path d="m9 11 3 3L22 4"></path>
                </svg>
                Copiado!
            `;
            copyBtn.style.background = '#10b981';
            
            setTimeout(() => {
                copyBtn.innerHTML = originalContent;
                copyBtn.style.background = '#4361ee';
            }, 2000);
        }).catch(() => {
            
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            showSimpleToast('ID copiado para a área de transferência!');
        });
    }

    function showSimpleToast(message) {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10001;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInDown 0.3s ease-out;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutUp 0.3s ease-in forwards';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }, 3000);
    }
});