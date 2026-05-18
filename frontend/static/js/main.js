// تهيئة Socket.IO
const socket = io();

// متغيرات الرسوم البيانية
let cpuChart, memoryChart, diskChart;
let cpuHistory = [];
let memoryHistory = [];
let maxHistoryPoints = 30;

// الاتصال بالسيرفر
socket.on('connect', function() {
    console.log('✅ Connected to server');
    updateStatus('متصل ✅');
    loadProcesses('cpu');
    loadServices();
});

socket.on('disconnect', function() {
    console.log('❌ Disconnected from server');
    updateStatus('مقطوع ❌');
});

// استقبال البيانات الحية من السيرفر
socket.on('system_data', function(data) {
    updateDashboard(data);
});

// تحديث حالة الاتصال
function updateStatus(status) {
    const statusEl = document.getElementById('status');
    if (statusEl) {
        statusEl.textContent = status;
    }
}

// عرض القسم المختار
function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));

    document.getElementById(sectionId).classList.add('active');

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');

    // تحميل البيانات عند الذهاب للقسم
    if (sectionId === 'system') {
        loadSystemInfo();
    }
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
                pointRadius: 3,
                pointBackgroundColor: '#e94560'
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
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#f39c12'
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

function updateLineChart(chart, data, label) {
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
    updateLineChart(cpuChart, cpuHistory, 'CPU');

    const memoryValue = data.memory.percent;
    document.getElementById('memory-value').textContent = memoryValue.toFixed(1) + '%';
    
    memoryHistory.push(memoryValue);
    if (memoryHistory.length > maxHistoryPoints) memoryHistory.shift();
    updateLineChart(memoryChart, memoryHistory, 'Memory');

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
    
    const formatted = `${days}d ${hours}h ${minutes}m ${secs}s`;
    document.getElementById('uptime-value').textContent = formatted;
}

function updateCardColors(cpu, memory, disk) {
    const cpuCard = document.querySelector('[data-metric="cpu"]');
    const memoryCard = document.querySelector('[data-metric="memory"]');
    const diskCard = document.querySelector('[data-metric="disk"]');

    if (cpuCard) cpuCard.style.borderColor = cpu > 80 ? '#e74c3c' : cpu > 50 ? '#f39c12' : '#0f3460';
    if (memoryCard) memoryCard.style.borderColor = memory > 80 ? '#e74c3c' : memory > 50 ? '#f39c12' : '#0f3460';
    if (diskCard) diskCard.style.borderColor = disk > 80 ? '#e74c3c' : disk > 50 ? '#f39c12' : '#0f3460';
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
                    <td>
                        <button class="btn btn-danger btn-small" onclick="killProcess(${p.pid})">❌ إيقاف</button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(err => console.error('Error loading processes:', err));
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
                    <td>${s.active === 'running' ? '🟢 شغال' : '🔴 متوقف'}</td>
                    <td>
                        <button class="btn btn-success btn-small" onclick="serviceAction('${s.name}', 'start')">▶️</button>
                        <button class="btn btn-danger btn-small" onclick="serviceAction('${s.name}', 'stop')">⏹️</button>
                        <button class="btn btn-warning btn-small" onclick="serviceAction('${s.name}', 'restart')">🔄</button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(err => console.error('Error loading services:', err));
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
        })
        .catch(err => console.error('Error loading logs:', err));
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

// ==================== System Info ====================

function loadSystemInfo() {
    fetch('/api/system-info')
        .then(res => res.json())
        .then(data => {
            const info = document.getElementById('system-info');
            info.innerHTML = `
                <div class="system-info-grid">
                    <div class="info-item">
                        <strong>CPU:</strong> ${data.cpu.count} cores @ ${data.cpu.frequency.toFixed(2)} GHz
                    </div>
                    <div class="info-item">
                        <strong>RAM:</strong> ${data.memory.total} GB (${data.memory.used} GB مستخدم)
                    </div>
                    <div class="info-item">
                        <strong>Disk:</strong> ${data.disk.total} GB (${data.disk.used} GB مستخدم)
                    </div>
                    <div class="info-item">
                        <strong>Uptime:</strong> ${data.uptime.formatted}
                    </div>
                    <div class="info-item">
                        <strong>Boot Time:</strong> ${data.uptime.boot_time}
                    </div>
                    <div class="info-item">
                        <strong>Processes:</strong> ${data.process_count} عملية نشطة
                    </div>
                </div>
            `;
        });
}

// تهيئة الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadProcesses();
});
