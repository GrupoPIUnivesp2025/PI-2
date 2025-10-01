// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // Alt + 1: Página inicial
    if (e.altKey && e.key === '1') {
        window.location.href = '/';
    }
    // Alt + 2: Busca de polos
    if (e.altKey && e.key === '2') {
        window.location.href = '/busca/';
    }
    // Alt + 3: Lista de polos
    if (e.altKey && e.key === '3') {
        window.location.href = '/polos/';
    }
    // Alt + 0: Acessibilidade
    if (e.altKey && e.key === '0') {
        window.location.href = '/acessibilidade/';
    }
    // Alt + C: Alto contraste
    if (e.altKey && e.key === 'c') {
        toggleHighContrast();
    }
});

// Alto Contraste
function toggleHighContrast() {
    document.body.classList.toggle('high-contrast');
    
    // Salva a preferência do usuário
    const isHighContrast = document.body.classList.contains('high-contrast');
    localStorage.setItem('highContrast', isHighContrast);
    
    // Anuncia a mudança para leitores de tela
    announceToScreenReader(
        isHighContrast ? 'Modo alto contraste ativado' : 'Modo alto contraste desativado'
    );
}

// Restaura preferência de contraste do usuário
if (localStorage.getItem('highContrast') === 'true') {
    document.body.classList.add('high-contrast');
}

// Função para anunciar mensagens para leitores de tela
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'alert');
    announcement.setAttribute('aria-live', 'polite');
    announcement.classList.add('visually-hidden');
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

// Melhoria de acessibilidade para o mapa
function enhanceMapAccessibility() {
    const map = document.getElementById('mapa');
    if (!map) return;

    // Adiciona instruções de uso do mapa
    const mapInstructions = document.createElement('div');
    mapInstructions.id = 'map-instructions';
    mapInstructions.className = 'visually-hidden';
    mapInstructions.setAttribute('aria-live', 'polite');
    map.parentNode.insertBefore(mapInstructions, map);

    // Adiciona controles de zoom acessíveis
    const zoomControls = document.createElement('div');
    zoomControls.className = 'map-zoom-controls';
    zoomControls.innerHTML = `
        <button type="button" class="btn btn-secondary btn-sm mb-2" onclick="mapZoomIn()" aria-label="Aumentar zoom do mapa">
            <i class="fas fa-plus" aria-hidden="true"></i>
        </button>
        <button type="button" class="btn btn-secondary btn-sm" onclick="mapZoomOut()" aria-label="Diminuir zoom do mapa">
            <i class="fas fa-minus" aria-hidden="true"></i>
        </button>
    `;
    map.parentNode.insertBefore(zoomControls, map);
}

// Funções de zoom do mapa (a serem chamadas pelo Leaflet)
function mapZoomIn() {
    if (window.leafletMap) {
        window.leafletMap.zoomIn();
        announceToScreenReader('Zoom aumentado');
    }
}

function mapZoomOut() {
    if (window.leafletMap) {
        window.leafletMap.zoomOut();
        announceToScreenReader('Zoom diminuído');
    }
}

// Melhoria para formulários
function enhanceFormsAccessibility() {
    // Adiciona validação de CEP com feedback acessível
    const cepInput = document.getElementById('cep');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            const value = e.target.value.replace(/\D/g, '');
            if (value.length === 8) {
                const formatted = value.replace(/(\d{5})(\d{3})/, '$1-$2');
                e.target.value = formatted;
                announceToScreenReader('CEP formatado corretamente');
            }
        });
    }
}

// Controle de tamanho da fonte
function adjustFontSize(action) {
    const html = document.documentElement;
    const currentScale = parseFloat(getComputedStyle(html).getPropertyValue('--font-size-scale')) || 1;
    
    let newScale = currentScale;
    switch(action) {
        case 'increase':
            newScale = Math.min(currentScale + 0.1, 1.5);
            break;
        case 'decrease':
            newScale = Math.max(currentScale - 0.1, 0.8);
            break;
        case 'reset':
            newScale = 1;
            break;
    }
    
    html.style.setProperty('--font-size-scale', newScale);
    localStorage.setItem('fontScale', newScale);
    
    const message = action === 'reset' ? 
        'Tamanho da fonte restaurado' : 
        `Tamanho da fonte ${action === 'increase' ? 'aumentado' : 'diminuído'}`;
    announceToScreenReader(message);
}

// Atalhos de teclado para fonte
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey) {
        if (e.key === '+' || e.key === '=') {
            e.preventDefault();
            adjustFontSize('increase');
        } else if (e.key === '-') {
            e.preventDefault();
            adjustFontSize('decrease');
        } else if (e.key === '0') {
            e.preventDefault();
            adjustFontSize('reset');
        }
    }
});

// Restaurar preferências do usuário
function restoreUserPreferences() {
    // Restaurar escala da fonte
    const savedFontScale = localStorage.getItem('fontScale');
    if (savedFontScale) {
        document.documentElement.style.setProperty('--font-size-scale', savedFontScale);
    }
    
    // Restaurar alto contraste
    if (localStorage.getItem('highContrast') === 'true') {
        document.body.classList.add('high-contrast');
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    enhanceMapAccessibility();
    enhanceFormsAccessibility();
    restoreUserPreferences();
});
