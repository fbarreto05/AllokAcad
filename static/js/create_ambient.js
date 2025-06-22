document.addEventListener('DOMContentLoaded', function() {
    const pictureInput = document.getElementById('picture');
    const preview = document.getElementById('preview');
    const nameInput = document.getElementById('name');
    const nameError = document.getElementById('nameError');
    const form = document.querySelector('.create-ambient-form');

    if (pictureInput && preview) {
        pictureInput.addEventListener('change', function() {

            while (preview.firstChild) {
                preview.removeChild(preview.firstChild);
            }

            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                if (!file.type.match('image.*')) {
                    preview.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#e63946" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="15" y1="9" x2="9" y2="15"></line>
                            <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>
                        <span>Formato não suportado. Por favor, selecione uma imagem.</span>
                    `;
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                }
                reader.readAsDataURL(file);
            } else {
                preview.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                    </svg>
                    <span>Clique para selecionar uma imagem</span>
                `;
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            if (!nameInput.value.trim()) {
                nameError.textContent = 'O nome do ambiente é obrigatório';
                nameInput.classList.add('error');
                isValid = false;
            } else if (nameInput.value.trim().length > 80) {
                nameError.textContent = 'O nome não pode ter mais de 80 caracteres';
                nameInput.classList.add('error');
                isValid = false;
            } else {
                nameError.textContent = '';
                nameInput.classList.remove('error');
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });

        nameInput.addEventListener('input', function() {
            nameError.textContent = '';
            nameInput.classList.remove('error');
        });
    }
});