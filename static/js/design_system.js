// Design System - Interações e comportamentos

// Gerenciamento de temas baseado em personas
class ThemeManager {
    constructor() {
        this.themes = {
            student: 'theme-student',
            accessible: 'theme-accessible',
            admin: 'theme-admin'
        };
        this.currentTheme = localStorage.getItem('userTheme') || 'student';
        this.applyTheme();
    }

    applyTheme() {
        document.body.classList.remove(...Object.values(this.themes));
        document.body.classList.add(this.themes[this.currentTheme]);
        localStorage.setItem('userTheme', this.currentTheme);
    }

    switchTheme(themeName) {
        if (this.themes[themeName]) {
            this.currentTheme = themeName;
            this.applyTheme();
        }
    }
}

// Gerenciador de feedback para usuários
class FeedbackManager {
    static show(message, type = 'info', duration = 5000) {
        const feedbackContainer = document.getElementById('feedback-container') || this.createFeedbackContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show feedback-message`;
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        
        feedbackContainer.appendChild(alert);
        
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }, duration);
    }

    static createFeedbackContainer() {
        const container = document.createElement('div');
        container.id = 'feedback-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
        return container;
    }
}

// Melhorias na busca por CEP
class EnhancedSearch {
    constructor() {
        this.setupCEPMask();
        this.setupGeolocation();
        this.setupMapInteractions();
    }

    setupCEPMask() {
        const cepInput = document.getElementById('cep');
        if (cepInput) {
            cepInput.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 8) value = value.substr(0, 8);
                if (value.length > 5) {
                    value = value.substr(0, 5) + '-' + value.substr(5);
                }
                e.target.value = value;
            });
        }
    }

    setupGeolocation() {
        const geoButton = document.getElementById('use-location');
        if (geoButton && 'geolocation' in navigator) {
            geoButton.addEventListener('click', () => {
                FeedbackManager.show('Obtendo sua localização...', 'info');
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        this.reverseGeocode(position.coords.latitude, position.coords.longitude);
                    },
                    (error) => {
                        FeedbackManager.show('Erro ao obter localização. Por favor, digite o CEP.', 'danger');
                    }
                );
            });
        }
    }

    setupMapInteractions() {
        const map = document.getElementById('mapa');
        if (map && window.L) {
            // Adiciona controles de zoom acessíveis
            const zoomControls = document.createElement('div');
            zoomControls.className = 'map-custom-controls';
            zoomControls.innerHTML = `
                <button class="btn btn-light" aria-label="Aumentar zoom">
                    <i class="fas fa-plus"></i>
                </button>
                <button class="btn btn-light" aria-label="Diminuir zoom">
                    <i class="fas fa-minus"></i>
                </button>
            `;
            map.appendChild(zoomControls);
        }
    }

    async reverseGeocode(lat, lon) {
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
            const data = await response.json();
            if (data.address && data.address.postcode) {
                document.getElementById('cep').value = data.address.postcode.replace(/\D/g, '');
                FeedbackManager.show('Localização obtida com sucesso!', 'success');
            }
        } catch (error) {
            FeedbackManager.show('Erro ao obter CEP da localização.', 'danger');
        }
    }
}

// Loading states
class LoadingManager {
    static show(element, text = 'Carregando...') {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="loading-indicator"></div>
                <span>${text}</span>
            </div>
        `;
        element.appendChild(loading);
    }

    static hide(element) {
        const loading = element.querySelector('.loading-overlay');
        if (loading) {
            loading.remove();
        }
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Inicializa gerenciadores
    window.themeManager = new ThemeManager();
    window.enhancedSearch = new EnhancedSearch();

    // Setup de elementos interativos
    setupInteractiveElements();
});

function setupInteractiveElements() {
    // Tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));

    // Popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => new bootstrap.Popover(popover));

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                FeedbackManager.show('Por favor, preencha todos os campos obrigatórios.', 'warning');
            }
            form.classList.add('was-validated');
        });
    });
}

// Service Worker para PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker registrado com sucesso.');
            })
            .catch(error => {
                console.log('Erro no registro do ServiceWorker:', error);
            });
    });
}
