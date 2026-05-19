const socket = io();
let cpuChart, memoryChart, diskChart, statsChart;
let cpuHistory = [], memoryHistory = [];
const maxHistoryPoints = 30;
let currentAlertFilter = 'all';

// الاتصال بالسيرفر
socket.on('connect', function() {
    console.log('✅ Connected to server');
    updateStatus('متصل ✅');
    loadProcesses('cpu');
    loadServices();
    loadAlerts();
    loadThresholds();
});

socket.on('disconnect', function() {
    console.log('❌ Disconnected from server');
    updateStatus('مقطوع ❌');
});

socket.on('system_data', function(data) {
    updateDashboard(data);
    if (data.alerts && data.alerts.length > 0) {
        data.alerts.forEach(alert => addAlertToUI(alert));
    }
    if (data.unread_alerts) {
        document.getElementById('alert-badge').textContent = data.unread_alerts;
    }
});

// ==================== Utils ====================

function updateStatus(status) {
    const statusEl = document.getElementById('status');
    if (statusEl) statusEl.textContent = status;
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');

    if (sectionId === 'statistics') loadStats(24);
    if (sectionId === 'settings') loadThresholds();
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
}

// ==================== Charts ====================

function initCharts() {
    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    cpuChart = new Chart(cpuCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'CPU %',
                data: [],
                borderColor: '#e94560',
                backgroundColor: 'rgba(233, 69, 96, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#eaeaea' } } },
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { color: '#aaa' }, grid: { color: '#333' } },
                x: { ticks: { color: '#aaa' }, grid: { color: '#333' } }
            }
        }
    });

    const memoryCtx = document.getElementById('memoryChart').getContext('2d');
    memoryChart = new Chart(memoryCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Memory %',
                data: [],
                borderColor: '#f39c12',
                backgroundColor: 'rgba(243, 156, 18, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#eaeaea' } } },
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { color: '#aaa' }, grid: { color: '#333' } },
                x: { ticks: { color: '#aaa' }, grid: { color: '#333' } }
            }
        }
    });

    const diskCtx = document.getElementById('diskChart').getContext('2d');
    diskChart = new Chart(diskCtx, {
        type: 'doughnut',
        data: {
            labels: ['مستخدم', 'متاح'],
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#2ecc71', '#1a1a2e'],
                borderColor: '#16213e',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#eaeaea' } } }
        }
    });
}

function updateLineChart(chart, data) {
    chart.data.labels = data.map((_, i) => i);
    chart.data.datasets[0].data = data;
    chart.update('none');
}

// ==================== Dashboard ====================

function updateDashboard(data) {
    const cpuValue = data.cpu.percent;
    document.getElementById('cpu-value').textContent = cpuValue.toFixed(1) + '%';
    cpuHistory.push(cpuValue);
    if (cpuHistory.length > maxHistoryPoints) cpuHistory.shift();
    updateLineChart(cpuChart, cpuHistory);

    const memoryValue = data.memory.percent;
    document.getElementById('memory-value').textContent = memoryValue.toFixed(1) + '%';
    memoryHistory.push(memoryValue);
    if (memoryHistory.length > maxHistoryPoints) memoryHistory.shift();
    updateLineChart(memoryChart, memoryHistory);

    const diskValue = data.disk.percent;
    document.getElementById('disk-value').textContent = diskValue.toFixed(1) + '%';
    diskChart.data.datasets[0].data = [diskValue, 100 - diskValue];
    diskChart.update();

    const sentMB = (data.network.bytes_sent / (1024 ** 2)).toFixed(2);
    const recvMB = (data.network.bytes_recv / (1024 ** 2)).toFixed(2);
    document.getElementById('network-sent').textContent = sentMB + ' MB';
    document.getElementById('network-recv').textContent = recvMB + ' MB';

    updateUptime(data.uptime);
    document.getElementById('process-count').textContent = data.process_count;
    updateCardColors(cpuValue, memoryValue, diskValue);
}

function updateUptime(uptime) {
    const seconds = uptime.total_seconds;
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    document.getElementById('uptime-value').textContent = `${days}d ${hours}h ${minutes}m ${secs}s`;
}

function updateCardColors(cpu, memory, disk) {
    const cpuCard = document.querySelector('[data-metric="cpu"]');
    const memoryCard = document.querySelector('[data-metric="memory"]');
    const diskCard = document.querySelector('[data-metric="disk"]');

    if (cpuCard) cpuCard.style.borderColor = cpu > 80 ? '#e74c3c' : cpu > 50 ? '#f39c12' : '#0f3460';
    if (memoryCard) memoryCard.style.borderColor = memory > 80 ? '#e74c3c' : memory > 50 ? '#f39c12' : '#0f3460';
    if (diskCard) diskCard.style.borderColor = disk > 80 ? '#e74c3c' : disk > 50 ? '#f39c12' : '#0f3460';
}

// ==================== Alerts ====================

function loadAlerts() {
    fetch('/api/alerts?limit=100')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('alerts-list');
            if (data.alerts.length === 0) {
                container.innerHTML = '<p>لا توجد تنبيهات</p>';
                return;
            }
            container.innerHTML = data.alerts.map(alert => `
                <div class="alert-item alert-${alert.level}">
                    <div class="alert-header">
                        <strong>${alert.title}</strong>
                        <span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString('ar-SA')}</span>
                    </div>
                    <div class="alert-message">${alert.message}</div>
                </div>
            `).join('');
        });
}

function addAlertToUI(alert) {
    const container = document.getElementById('alerts-list');
    if (container.innerHTML.includes('لا توجد تنبيهات')) {
        container.innerHTML = '';
    }
    const alertEl = document.createElement('div');
    alertEl.className = `alert-item alert-${alert.level}`;
    alertEl.innerHTML = `
        <div class="alert-header">
            <strong>${alert.title}</strong>
            <span class="alert-time">الآن</span>
        </div>
        <div class="alert-message">${alert.message}</div>
    `;
    container.insertBefore(alertEl, container.firstChild);
}

function filterAlerts(level) {
    currentAlertFilter = level;
    loadAlerts();
}

function clearAlerts() {
    document.getElementById('alerts-list').innerHTML = '<p>لا توجد تنبيهات</p>';
}

// ==================== Processes ====================

function loadProcesses(sortBy = 'cpu') {
    fetch(`/api/processes/top?n=15&sort_by=${sortBy}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('processes-list');
            if (data.processes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5">لا توجد عمليات</td></tr>';
                return;
            }
            tbody.innerHTML = data.processes.map(p => `
                <tr>
                    <td>${p.pid}</td>
                    <td>${p.name}</td>
                    <td>${p.cpu_percent.toFixed(1)}%</td>
                    <td>${p.memory_percent.toFixed(1)}%</td>
                    <td><button class="btn btn-danger btn-small" onclick="killProcess(${p.pid})">❌</button></td>
                </tr>
            `).join('');
        });
}

function killProcess(pid) {
    if (confirm(`هل أنت متأكد من إيقاف العملية ${pid}؟`)) {
        fetch(`/api/process/${pid}/kill`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                loadProcesses();
            });
    }
}

// ==================== Services ====================

function loadServices() {
    fetch('/api/services/all')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('services-list');
            if (data.services.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4">لا توجد خدمات</td></tr>';
                return;
            }
            tbody.innerHTML = data.services.slice(0, 20).map(s => `
                <tr>
                    <td>${s.name}</td>
                    <td>${s.status}</td>
                    <td>${s.active === 'running' ? '🟢' : '🔴'}</td>
                    <td>
                        <button class="btn btn-success btn-small" onclick="serviceAction('${s.name}', 'start')">▶️</button>
                        <button class="btn btn-danger btn-small" onclick="serviceAction('${s.name}', 'stop')">⏹️</button>
                        <button class="btn btn-warning btn-small" onclick="serviceAction('${s.name}', 'restart')">🔄</button>
                    </td>
                </tr>
            `).join('');
        });
}

function serviceAction(serviceName, action) {
    fetch(`/api/service/${serviceName}/${action}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            loadServices();
        });
}

// ==================== Logs ====================

function loadLogs(logType) {
    fetch(`/api/logs/${logType}?lines=50`)
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('logs-content');
            if (data.error) {
                content.innerHTML = `<p class="error">خطأ: ${data.error}</p>`;
                return;
            }
            content.innerHTML = `
                <div class="log-header">📜 ${logType.toUpperCase()} - آخر ${data.count} سطر</div>
                <pre class="log-content">${data.lines.join('\n')}</pre>
            `;
        });
}

function loadFailedLogins() {
    fetch('/api/logs/failed-logins')
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('logs-content');
            content.innerHTML = `
                <div class="log-header">🔐 محاولات تسجيل دخول فاشلة - ${data.count} محاولة</div>
                <pre class="log-content">${data.failed_attempts.join('\n')}</pre>
            `;
        });
}

// ==================== Statistics ====================

function loadStats(hours) {
    fetch(`/api/stats/history?hours=${hours}`)
        .then(res => res.json())
        .then(data => {
            const stats = data.stats || [];
            
            const cpuData = stats.map(s => s.cpu);
            const memoryData = stats.map(s => s.memory);
            const diskData = stats.map(s => s.disk);
            
            if (!statsChart) {
                const ctx = document.getElementById('statsChart').getContext('2d');
                statsChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: stats.map((s, i) => i),
                        datasets: [
                            {
                                label: 'CPU %',
                                data: cpuData,
                                borderColor: '#e94560',
                                backgroundColor: 'rgba(233, 69, 96, 0.1)',
                                tension: 0.4
                            },
                            {
                                label: 'Memory %',
                                data: memoryData,
                                borderColor: '#f39c12',
                                backgroundColor: 'rgba(243, 156, 18, 0.1)',
                                tension: 0.4
                            },
                            {
                                label: 'Disk %',
                                data: diskData,
                                borderColor: '#2ecc71',
                                backgroundColor: 'rgba(46, 204, 113, 0.1)',
                                tension: 0.4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { labels: { color: '#eaeaea' } } },
                        scales: {
                            y: { ticks: { color: '#aaa' }, grid: { color: '#333' } },
                            x: { ticks: { color: '#aaa' }, grid: { color: '#333' } }
                        }
                    }
                });
            } else {
                statsChart.data.labels = stats.map((s, i) => i);
                statsChart.data.datasets[0].data = cpuData;
                statsChart.data.datasets[1].data = memoryData;
                statsChart.data.datasets[2].data = diskData;
                statsChart.update();
            }
        });
}

// ==================== Settings ====================

function loadThresholds() {
    fetch('/api/alerts/thresholds')
        .then(res => res.json())
        .then(data => {
            const t = data.thresholds;
            document.getElementById('cpu-warning').value = t.cpu_warning;
            document.getElementById('cpu-critical').value = t.cpu_critical;
            document.getElementById('memory-warning').value = t.memory_warning;
            document.getElementById('memory-critical').value = t.memory_critical;
            document.getElementById('disk-warning').value = t.disk_warning;
            document.getElementById('disk-critical').value = t.disk_critical;
        });
}

function saveSetting(metric, level) {
    const value = document.getElementById(`${metric}-${level}`).value;
    fetch('/api/alerts/thresholds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metric, level, value: parseInt(value) })
    })
    .then(res => res.json())
    .then(data => alert(data.success ? 'تم الحفظ' : 'خطأ'));
}

// تهيئة الصفحة
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
    }
    initCharts();
    loadProcesses();
});
