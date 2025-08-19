// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    const userId = window.USER_ID;
    if (!userId) return;

    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsPath = `${wsScheme}://${window.location.host}/ws/notifications/`;
    const socket = new WebSocket(wsPath);

    socket.onopen = () => console.log("✅ WebSocket подключён");

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        // 1. Обработка уведомлений (🔔)
        if (data.type === "notification" && data.message) {
            showBrowserNotification(data.message);
            showWebNotification(data.message);
        }

        // 2. Обработка обновлений задач (создание, удаление, изменение)
        if (data.type === "task_update") {
            const task = data.task;
            const tbody = document.getElementById("tasks-table-body");
            if (!tbody) return; // Если таблицы нет — выходим

            if (data.action === "created") {
                addTaskToList(task);
            } else if (data.action === "deleted") {
                removeTaskFromList(task.id);
            } else if (data.action === "updated") {
                updateTaskInList(task);
            }
        }
    };

    socket.onclose = () => {
        console.log("❌ WebSocket закрыт, переподключение...");
        setTimeout(() => window.location.reload(), 5000);
    };

    socket.onerror = (e) => console.error("WebSocket ошибка:", e);
});

// --- Функции для уведомлений ---

function showBrowserNotification(message) {
    if (Notification.permission === 'granted') {
        new Notification('🔔 Уведомление', {
            body: message,
            icon: '/static/favicon.ico'
        });
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification('🔔 Уведомление', { body: message });
            }
        });
    }
}

function showWebNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'custom-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">🔔</div>
            <div class="notification-text">${message}</div>
            <button class="notification-close">&times;</button>
        </div>
    `;
    document.body.appendChild(notification);

    notification.querySelector('.notification-close').onclick = () => {
        notification.remove();
    };

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 6000);
}

// --- Функции для обновления списка задач ---

function addTaskToList(task) {
    const tbody = document.getElementById("tasks-table-body");
    const row = document.createElement("tr");
    row.dataset.taskId = task.id;

    const statusBadge = getStatusBadge(task.status);
    const priorityBadge = getPriorityBadge(task.priority);

    row.innerHTML = `
        <td>${task.title}</td>
        <td><span class="badge ${statusBadge.class}">${statusBadge.text}</span></td>
        <td><span class="badge ${priorityBadge.class}">${priorityBadge.text}</span></td>
        <td>${task.due_date ? new Date(task.due_date).toLocaleString() : "—"}</td>
        <td>
            <a href="/${task.id}/update" class="btn btn-sm btn-outline-primary">Редакт.</a>
            <a href="/${task.id}/delete" class="btn btn-sm btn-outline-danger">Удалить</a>
        </td>
    `;

    tbody.prepend(row);

    // Удаляем "Нет задач"
    const noTasks = document.querySelector('.text-center.text-muted');
    if (noTasks) noTasks.remove();
}

function removeTaskFromList(taskId) {
    const row = document.querySelector(`tr[data-task-id="${taskId}"]`);
    if (row) row.remove();

    const tbody = document.getElementById("tasks-table-body");
    if (tbody && tbody.children.length === 0) {
        const container = document.querySelector('.card.p-4');
        const empty = document.createElement('div');
        empty.className = 'text-center text-muted py-5';
        empty.innerHTML = `
            <i class="fas fa-inbox fa-2x mb-3 text-secondary"></i>
            <p class="lead mb-3">Нет задач</p>
            <a href="/create" class="btn btn-outline-primary">
                <i class="fas fa-plus-circle me-1"></i> Создать первую
            </a>
        `;
        container.appendChild(empty);
    }
}

function updateTaskInList(task) {
    const row = document.querySelector(`tr[data-task-id="${task.id}"]`);
    if (!row) return;

    row.querySelector('td:nth-child(1)').textContent = task.title;

    const statusCell = row.querySelector('td:nth-child(2) .badge');
    const statusBadge = getStatusBadge(task.status);
    statusCell.textContent = statusBadge.text;
    statusCell.className = `badge ${statusBadge.class}`;

    const priorityCell = row.querySelector('td:nth-child(3) .badge');
    const priorityBadge = getPriorityBadge(task.priority);
    priorityCell.textContent = priorityBadge.text;
    priorityCell.className = `badge ${priorityBadge.class}`;

    row.querySelector('td:nth-child(4)').textContent = task.due_date
        ? new Date(task.due_date).toLocaleString()
        : "—";
}

// --- Вспомогательные функции ---

function getStatusBadge(status) {
    const map = {
        'todo': { text: 'To Do', class: 'bg-secondary' },
        'in_progress': { text: 'В работе', class: 'bg-warning text-dark' },
        'done': { text: 'Готово', class: 'bg-success' }
    };
    return map[status] || map['todo'];
}

function getPriorityBadge(priority) {
    const map = {
        'high': { text: 'Высокий', class: 'bg-danger' },
        'medium': { text: 'Средний', class: 'bg-info text-dark' },
        'low': { text: 'Низкий', class: 'bg-light text-dark border' }
    };
    return map[priority] || map['low'];
}