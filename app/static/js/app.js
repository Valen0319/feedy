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

const showDeleteControls = (button) => {
    const cell = button.closest('td');
    if (!cell) return;

    const actions = document.createElement('div');
    actions.className = 'delete-actions';

    const confirmButton = document.createElement('button');
    confirmButton.type = 'button';
    confirmButton.className = 'delete-action delete-action--confirm';
    confirmButton.textContent = 'Confirmar';

    const cancelButton = document.createElement('button');
    cancelButton.type = 'button';
    cancelButton.className = 'delete-action delete-action--cancel';
    cancelButton.textContent = 'Cancelar';

    confirmButton.addEventListener('click', async () => {
        const scheduleId = button.dataset.id;
        if (!scheduleId) return;

        const response = await fetch(`/api/schedules/${scheduleId}`, { method: 'DELETE' });
        if (response.ok) {
            await loadSchedules();
        }
    });

    cancelButton.addEventListener('click', () => {
        const restoreButton = document.createElement('button');
        restoreButton.type = 'button';
        restoreButton.className = 'delete-button';
        restoreButton.textContent = 'Eliminar';
        restoreButton.dataset.id = button.dataset.id;
        restoreButton.setAttribute('aria-label', 'Eliminar horario');
        restoreButton.addEventListener('click', () => showDeleteControls(restoreButton));

        cell.innerHTML = '';
        cell.appendChild(restoreButton);
    });

    actions.append(confirmButton, cancelButton);
    cell.innerHTML = '';
    cell.appendChild(actions);
};

const renderSchedules = (items = []) => {
    const tableBody = document.getElementById('schedule-table-body');
    if (!tableBody) return;

    if (!items.length) {
        tableBody.innerHTML = '<tr><td colspan="3">Sin horarios cargados</td></tr>';
        return;
    }

    tableBody.innerHTML = items.map((item) => `
        <tr>
            <td>${item.portion}</td>
            <td>${item.time}</td>
            <td>
                <button class="delete-button" type="button" data-id="${item.id}" aria-label="Eliminar horario ${item.time}">
                    Eliminar
                </button>
            </td>
        </tr>
    `).join('');

    tableBody.querySelectorAll('.delete-button').forEach((button) => {
        button.addEventListener('click', () => showDeleteControls(button));
    });
};

const loadSchedules = async () => {
    try {
        const response = await fetch('/api/schedules');
        const data = await response.json();
        renderSchedules(data.items || []);
    } catch (error) {
        console.error('Error loading schedules', error);
        renderSchedules([]);
    }
};

const loadPortion = async () => {
    try {
        const response = await fetch('/api/portion');
        const data = await response.json();
        const input = document.getElementById('portion-time');
        if (input) input.value = data.milliseconds ?? 1200;
    } catch (error) {
        console.error('Error loading portion', error);
    }
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
                videoEl.removeAttribute('src');
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
    const input = document.getElementById('portion-time');
    const milliseconds = Number(input?.value || 1200);

    try {
        const response = await fetch('/api/portion/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ milliseconds }),
        });
        const data = await response.json();
        if (response.ok) {
            alert(data.message || 'Porción de prueba ejecutada.');
        }
    } catch (error) {
        console.error('Error testing portion', error);
        alert('No fue posible probar la porción.');
    }
});

document.querySelector('#portion-modal .primary-button')?.addEventListener('click', async () => {
    const input = document.getElementById('portion-time');
    const milliseconds = Number(input?.value || 1200);

    try {
        const response = await fetch('/api/portion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ milliseconds }),
        });

        if (response.ok) {
            closeModal('portion-modal');
        }
    } catch (error) {
        console.error('Error saving portion', error);
    }
});

document.querySelector('#schedule-modal .primary-button')?.addEventListener('click', async () => {
    const schedulePortion = document.getElementById('schedule-portion');
    const scheduleHour = document.getElementById('schedule-hour');
    const scheduleMinute = document.getElementById('schedule-minute');

    const hourValue = String(scheduleHour?.value ?? '10').padStart(2, '0');
    const minuteValue = String(scheduleMinute?.value ?? '00').padStart(2, '0');

    const payload = {
        portion: Number(schedulePortion?.value || 1),
        time: `${hourValue}:${minuteValue}`,
    };

    try {
        const response = await fetch('/api/schedules', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (response.ok) {
            closeModal('schedule-modal');
            await loadSchedules();
            if (schedulePortion) schedulePortion.value = '1';
            if (scheduleHour) scheduleHour.value = '10';
            if (scheduleMinute) scheduleMinute.value = '00';
        }
    } catch (error) {
        console.error('Error saving schedule', error);
    }
});

const deviceStatusText = document.getElementById('device-status-text');
const deviceStatusIndicator = document.getElementById('device-status-indicator');

const updateDeviceStatus = async () => {
    try {
        const response = await fetch('/api/device-status');
        const data = await response.json();
        const connected = Boolean(data.connected);

        if (deviceStatusText) {
            deviceStatusText.textContent = connected ? 'Dispositivo conectado' : 'Dispositivo no conectado';
        }

        if (deviceStatusIndicator) {
            deviceStatusIndicator.classList.toggle('status-indicator--offline', !connected);
        }
    } catch (error) {
        if (deviceStatusText) {
            deviceStatusText.textContent = 'Dispositivo no conectado';
        }
        if (deviceStatusIndicator) {
            deviceStatusIndicator.classList.add('status-indicator--offline');
        }
    }
};

const cameraModal = document.getElementById('camera-modal');
const startLiveCamera = async () => {
    if (!cameraModal || !cameraModal.classList.contains('hidden')) {
        const videoEl = document.getElementById('camera-feed');
        const placeholder = document.querySelector('.camera-placeholder');

        if (!videoEl) return;

        try {
            videoEl.src = '/video_feed';
            videoEl.load();
            videoEl.style.display = 'block';
            if (placeholder) placeholder.style.display = 'none';
            await videoEl.play();
        } catch (error) {
            console.warn('No fue posible iniciar el stream de la cámara de la Raspberry:', error);
        }
    }
};

const cameraTrigger = document.querySelector('[data-modal-target="camera-modal"]');
cameraTrigger?.addEventListener('click', startLiveCamera);

window.addEventListener('DOMContentLoaded', async () => {
    await loadSchedules();
    await loadPortion();
    updateDeviceStatus();
    setInterval(updateDeviceStatus, 5000);
});
