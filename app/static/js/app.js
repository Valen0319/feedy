const modalIds = ['portion-modal', 'camera-modal', 'schedule-modal'];

const openModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
};

const closeModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
};

document.querySelectorAll('[data-modal-target]').forEach((button) => {
    button.addEventListener('click', () => {
        const modalId = button.dataset.modalTarget;
        openModal(modalId);
    });
});

document.querySelectorAll('[data-close-modal]').forEach((button) => {
    button.addEventListener('click', () => {
        const modalId = button.dataset.closeModal;
        closeModal(modalId);
        if (modalId === 'camera-modal') {
            const videoEl = document.getElementById('camera-feed');
            const placeholder = document.querySelector('.camera-placeholder');
            if (videoEl) {
                videoEl.pause();
                videoEl.srcObject = null;
                videoEl.style.display = 'none';
            }
            if (placeholder) placeholder.style.display = 'flex';
        }
    });
});

modalIds.forEach((modalId) => {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.addEventListener('click', (event) => {
        if (event.target === modal) closeModal(modalId);
    });
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        modalIds.forEach(closeModal);
    }
});

document.getElementById('test-portion-button')?.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/portion/test', { method: 'POST' });
        const data = await response.json();
        if (response.ok) {
            alert(data.message || 'Porción de prueba ejecutada.');
        }
    } catch (error) {
        console.error('Error testing portion', error);
        alert('No fue posible probar la porción.');
    }
});

document.querySelectorAll('.delete-button').forEach((button) => {
    const resetButton = () => {
        button.classList.remove('is-confirming');
        button.innerHTML = `
      <span class="trash-icon">
        <span class="trash-lid"></span>
        <span class="trash-body"></span>
      </span>
    `;
        button.setAttribute('aria-label', 'Eliminar horario');
        button.title = 'Eliminar horario';
    };

    button.addEventListener('click', () => {
        const isConfirming = button.classList.contains('is-confirming');

        if (!isConfirming) {
            button.classList.add('is-confirming');
            button.innerHTML = 'Confirmar';
            button.setAttribute('aria-label', 'Confirmar eliminación');
            button.title = 'Confirmar eliminación';
            return;
        }

        const row = button.closest('tr');
        if (row) row.remove();
        resetButton();
    });

    button.addEventListener('dblclick', (event) => {
        event.preventDefault();
        resetButton();
    });
});

const deviceStatusText = document.getElementById('device-status-text');
const deviceStatusIndicator = document.getElementById('device-status-indicator');

const updateDeviceStatus = async () => {
    try {
        const response = await fetch('/api/device-status');
        const data = await response.json();
        const connected = Boolean(data.connected);

        deviceStatusText.textContent = connected ? 'Dispositivo conectado' : 'Dispositivo no conectado';
        deviceStatusIndicator.classList.toggle('status-indicator--offline', !connected);
    } catch (error) {
        deviceStatusText.textContent = 'Dispositivo no conectado';
        deviceStatusIndicator.classList.add('status-indicator--offline');
    }
};

updateDeviceStatus();
setInterval(updateDeviceStatus, 5000);

const cameraModal = document.getElementById('camera-modal');
const startLiveCamera = async () => {
    if (!cameraModal || !cameraModal.classList.contains('hidden')) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
                audio: false,
            });

            const videoEl = document.getElementById('camera-feed');
            const placeholder = document.querySelector('.camera-placeholder');
            if (videoEl) {
                videoEl.srcObject = stream;
                videoEl.style.display = 'block';
                videoEl.play();
            }
            if (placeholder) placeholder.style.display = 'none';
        } catch (error) {
            console.warn('Cámara no disponible en el navegador:', error);
        }
    }
};

const cameraTrigger = document.querySelector('[data-modal-target="camera-modal"]');
cameraTrigger?.addEventListener('click', startLiveCamera);
