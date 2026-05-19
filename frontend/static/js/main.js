const socket = io();
let cpuChart, memoryChart, diskChart, statsChart;
let cpuHistory = [], memoryHistory = [];
const maxHistoryPoints = 30;

// ==================== Utils ====================
function updateStatus(status) {
    const statusEl = document.getElementById('status');
    if (statusEl) statusEl.textContent = status;
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(s => s.classList.remove('active'));
    const activeSection = document.getElementById(sectionId);
    if (activeSection) activeSection.classList.add('active');

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');

    if (sectionId === 'network') {
        if (typeof scanWiFi === 'function') scanWiFi();
        if (typeof loadDevices === 'function') loadDevices();
    }
    if (sectionId === 'statistics' && typeof loadStats === 'function') loadStats(24);
    if (sectionId === 'settings' && typeof loadThresholds === 'function') loadThresholds();
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
}

// ==================== Socket Events ====================
socket.on('connect', function() {
    console.log('✅ Connected');
    updateStatus('متصل ✅');
    if (typeof loadProcesses === 'function') loadProcesses('cpu');
    if (typeof loadServices === 'function') loadServices();
    if (typeof loadAlerts === 'function') loadAlerts();
    if (typeof loadThresholds === 'function') loadThresholds();
});

socket.on('disconnect', function() {
    updateStatus('مقطوع ❌');
});

socket.on('system_data', function(data) {
    updateDashboard(data);
    if (data.alerts && data.alerts.length > 0 && typeof addAlertToUI === 'function') {
        data.alerts.forEach(alert => addAlertToUI(alert));
    }
    if (data.unread_alerts) {
        const badge = document.getElementById('alert-badge');
        if (badge) badge.textContent = data.unread_alerts;
    }
});

// ==================== Dashboard ====================
function initCharts() {
    const cpuCtx = document.getElementById('cpuChart')?.getContext('2d');
    if (cpuCtx) {
        cpuChart = new Chart(cpuCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'CPU %', data: [], borderColor: '#e94560', backgroundColor: 'rgba(233,69,96,0.1)', borderWidth: 2, fill: true, tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#eaeaea' } } }, scales: { y: { beginAtZero: true, max: 100, ticks: { color: '#aaa' }, grid: { color: '#333' } }, x: { ticks: { color: '#aaa' }, grid: { color: '#333' } } } }
        });
    }
    const memoryCtx = document.getElementById('memoryChart')?.getContext('2d');
    if (memoryCtx) {
        memoryChart = new Chart(memoryCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Memory %', data: [], borderColor: '#f39c12', backgroundColor: 'rgba(243,156,18,0.1)', borderWidth: 2, fill: true, tension: 0.4 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#eaeaea' } } }, scales: { y: { beginAtZero: true, max: 100, ticks: { color: '#aaa' }, grid: { color: '#333' } }, x: { ticks: { color: '#aaa' }, grid: { color: '#333' } } } }
        });
    }
    const diskCtx = document.getElementById('diskChart')?.getContext('2d');
    if (diskCtx) {
        diskChart = new Chart(diskCtx, {
            type: 'doughnut',
            data: { labels: ['مستخدم', 'متاح'], datasets: [{ data: [0, 100], backgroundColor: ['#2ecc71', '#1a1a2e'], borderColor: '#16213e', borderWidth: 2 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#eaeaea' } } } }
        });
    }
}

function updateLineChart(chart, data) {
    if (!chart) return;
    chart.data.labels = data.map((_, i) => i);
    chart.data.datasets[0].data = data;
    chart.update('none');
}

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
    if (diskChart) {
        diskChart.data.datasets[0].data = [diskValue, 100 - diskValue];
        diskChart.update();
    }

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

// ==================== Network Functions ====================
function scanWiFi() {
    const tbody = document.getElementById('wifi-list');
    if (tbody) tbody.innerHTML = '<tr><td colspan="4">جاري المسح...</td></tr>';
    fetch('/api/network/wifi/scan')
        .then(res => res.json())
        .then(data => {
            if (!tbody) return;
            if (!data.networks.length) {
                tbody.innerHTML = '<tr><td colspan="4">لا توجد شبكات</td></tr>';
                return;
            }
            tbody.innerHTML = data.networks.map(n => `
                <tr>
                    <td>${n.ssid}</td>
                    <td><div class="signal-bar"><div class="signal-fill" style="width: ${n.signal}%"></div></div> ${n.signal}%</td>
                    <td>${n.security}</td>
                    <td>${n.channel}</td>
                </tr>
            `).join('');
        })
        .catch(err => console.error(err));
}

function loadDevices() {
    const tbody = document.getElementById('devices-list');
    if (tbody) tbody.innerHTML = '<tr><td colspan="4">جاري التحميل...</td></tr>';
    fetch('/api/network/devices/arp')
        .then(res => res.json())
        .then(data => {
            if (!tbody) return;
            if (!data.devices.length) {
                tbody.innerHTML = '<tr><td colspan="4">لا توجد أجهزة</td></tr>';
                return;
            }
            tbody.innerHTML = data.devices.map(d => `
                <tr>
                    <td><span class="ip-badge">${d.ip}</span></td>
                    <td>${d.mac}</td>
                    <td>${d.vendor}</td>
                    <td><button class="btn btn-small btn-primary" onclick="pingHost('${d.ip}')">Ping</button></td>
                </tr>
            `).join('');
        });
}

function pingHost(ip = null) {
    const ipInput = ip || document.getElementById('ping-ip')?.value;
    if (!ipInput) return alert('أدخل IP');
    const resultDiv = document.getElementById('ping-result');
    if (resultDiv) resultDiv.innerHTML = '<p class="loading">جاري...</p>';
    fetch('/api/network/ping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: ipInput })
    })
    .then(res => res.json())
    .then(data => {
        if (resultDiv) {
            if (data.error) resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
            else resultDiv.innerHTML = `<div class="result-box success"><p>✅ ${data.ip} متصل | Min:${data.min}ms Avg:${data.avg}ms Max:${data.max}ms</p></div>`;
        }
    });
}

function dnsLookup() {
    const domain = document.getElementById('dns-domain')?.value;
    if (!domain) return alert('أدخل دومين');
    const resultDiv = document.getElementById('dns-result');
    if (resultDiv) resultDiv.innerHTML = '<p class="loading">جاري...</p>';
    fetch('/api/network/dns/lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain })
    })
    .then(res => res.json())
    .then(data => {
        if (resultDiv) {
            if (data.error) resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
            else resultDiv.innerHTML = `<div class="result-box success"><p>${data.domain} → <span class="ip-badge">${data.ip}</span></p></div>`;
        }
    });
}

function quickPortScan(ip = null) {
    const ipInput = ip || document.getElementById('port-ip')?.value;
    if (!ipInput) return alert('أدخل IP');
    const resultDiv = document.getElementById('port-result');
    if (resultDiv) resultDiv.innerHTML = '<p class="loading">جاري الفحص...</p>';
    fetch('/api/network/ports/quick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: ipInput })
    })
    .then(res => res.json())
    .then(data => {
        if (resultDiv) {
            if (data.error) resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
            else resultDiv.innerHTML = `<div class="result-box"><p>المنافذ المفتوحة: ${data.open_ports.join(', ') || 'لا شيء'}</p></div>`;
        }
    });
}

function pingSweep() {
    const network = document.getElementById('sweep-network')?.value;
    if (!network) return alert('أدخل الشبكة مثال 192.168.1.0/24');
    const resultDiv = document.getElementById('sweep-result');
    if (resultDiv) resultDiv.innerHTML = '<p class="loading">جاري المسح... قد يستغرق دقائق</p>';
    fetch('/api/network/ping-sweep', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ network })
    })
    .then(res => res.json())
    .then(data => {
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="result-box success"><p>${data.online_hosts.length} جهاز متصل</p><div class="hosts-list">${data.online_hosts.map(h => `<div class="host-item">${h.ip} <button class="btn btn-small" onclick="pingHost('${h.ip}')">Ping</button></div>`).join('')}</div></div>`;
        }
    });
}

function showNetworkTab(tab) {
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(t => t.classList.remove('active'));
    const activeTab = document.getElementById(tab + '-tab');
    if (activeTab) activeTab.classList.add('active');
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(b => b.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
}

// ==================== Alerts ====================
function loadAlerts() {
    fetch('/api/alerts?limit=100')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('alerts-list');
            if (!container) return;
            if (!data.alerts.length) {
                container.innerHTML = '<p>لا توجد تنبيهات</p>';
                return;
            }
            container.innerHTML = data.alerts.map(alert => `
                <div class="alert-item alert-${alert.level}">
                    <div class="alert-header"><strong>${alert.title}</strong><span class="alert-time">${new Date(alert.timestamp).toLocaleTimeString()}</span></div>
                    <div class="alert-message">${alert.message}</div>
                </div>
            `).join('');
        });
}

function addAlertToUI(alert) {
    const container = document.getElementById('alerts-list');
    if (!container) return;
    if (container.innerHTML.includes('لا توجد تنبيهات')) container.innerHTML = '';
    const alertEl = document.createElement('div');
    alertEl.className = `alert-item alert-${alert.level}`;
    alertEl.innerHTML = `<div class="alert-header"><strong>${alert.title}</strong><span class="alert-time">الآن</span></div><div class="alert-message">${alert.message}</div>`;
    container.insertBefore(alertEl, container.firstChild);
}

function filterAlerts(level) { loadAlerts(); }
function clearAlerts() {
    const container = document.getElementById('alerts-list');
    if (container) container.innerHTML = '<p>لا توجد تنبيهات</p>';
}

// ==================== Processes ====================
function loadProcesses(sortBy = 'cpu') {
    fetch(`/api/processes/top?n=15&sort_by=${sortBy}`)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('processes-list');
            if (!tbody) return;
            if (!data.processes.length) {
                tbody.innerHTML = '<tr><td colspan="5">لا توجد عمليات</td></tr>';
                return;
            }
            tbody.innerHTML = data.processes.map(p => `
                <tr><td>${p.pid}</td><td>${p.name}</td><td>${p.cpu_percent.toFixed(1)}%</td><td>${p.memory_percent.toFixed(1)}%</td><td><button class="btn btn-danger btn-small" onclick="killProcess(${p.pid})">❌</button></td></tr>
            `).join('');
        });
}

function killProcess(pid) {
    if (!confirm('هل أنت متأكد؟')) return;
    fetch(`/api/process/${pid}/kill`, { method: 'POST' })
        .then(res => res.json())
        .then(data => { alert(data.message); loadProcesses(); });
}

// ==================== Services ====================
function loadServices() {
    fetch('/api/services/all')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('services-list');
            if (!tbody) return;
            if (!data.services.length) {
                tbody.innerHTML = '<tr><td colspan="4">لا توجد خدمات</td></tr>';
                return;
            }
            tbody.innerHTML = data.services.slice(0, 20).map(s => `
                <tr><td>${s.name}</td><td>${s.status}</td><td>${s.active === 'running' ? '🟢' : '🔴'}</td><td><button class="btn btn-success btn-small" onclick="serviceAction('${s.name}', 'start')">▶️</button> <button class="btn btn-danger btn-small" onclick="serviceAction('${s.name}', 'stop')">⏹️</button> <button class="btn btn-warning btn-small" onclick="serviceAction('${s.name}', 'restart')">🔄</button></td></tr>
            `).join('');
        });
}

function serviceAction(serviceName, action) {
    fetch(`/api/service/${serviceName}/${action}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => { alert(data.message); loadServices(); });
}

// ==================== Logs ====================
function loadLogs(logType) {
    fetch(`/api/logs/${logType}?lines=50`)
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('logs-content');
            if (!content) return;
            if (data.error) content.innerHTML = `<p class="error">${data.error}</p>`;
            else content.innerHTML = `<div class="log-header">📜 ${logType.toUpperCase()}</div><pre class="log-content">${data.lines.join('\n')}</pre>`;
        });
}

function loadFailedLogins() {
    fetch('/api/logs/failed-logins')
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('logs-content');
            if (!content) return;
            content.innerHTML = `<div class="log-header">🔐 محاولات فاشلة</div><pre class="log-content">${data.failed_attempts.join('\n')}</pre>`;
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
            const ctx = document.getElementById('statsChart')?.getContext('2d');
            if (!ctx) return;
            if (!statsChart) {
                statsChart = new Chart(ctx, {
                    type: 'line',
                    data: { labels: stats.map((_,i)=>i), datasets: [{ label: 'CPU %', data: cpuData, borderColor: '#e94560', tension: 0.4 }, { label: 'Memory %', data: memoryData, borderColor: '#f39c12', tension: 0.4 }, { label: 'Disk %', data: diskData, borderColor: '#2ecc71', tension: 0.4 }] },
                    options: { responsive: true, plugins: { legend: { labels: { color: '#eaeaea' } } }, scales: { y: { ticks: { color: '#aaa' }, grid: { color: '#333' } }, x: { ticks: { color: '#aaa' }, grid: { color: '#333' } } } }
                });
            } else {
                statsChart.data.labels = stats.map((_,i)=>i);
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
            if (document.getElementById('cpu-warning')) document.getElementById('cpu-warning').value = t.cpu_warning;
            if (document.getElementById('cpu-critical')) document.getElementById('cpu-critical').value = t.cpu_critical;
            if (document.getElementById('memory-warning')) document.getElementById('memory-warning').value = t.memory_warning;
            if (document.getElementById('memory-critical')) document.getElementById('memory-critical').value = t.memory_critical;
            if (document.getElementById('disk-warning')) document.getElementById('disk-warning').value = t.disk_warning;
            if (document.getElementById('disk-critical')) document.getElementById('disk-critical').value = t.disk_critical;
        });
}

function saveSetting(metric, level) {
    const value = document.getElementById(`${metric}-${level}`)?.value;
    if (!value) return;
    fetch('/api/alerts/thresholds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metric, level, value: parseInt(value) })
    })
    .then(res => res.json())
    .then(data => alert(data.success ? '✅ تم الحفظ' : '❌ خطأ'));
}

// ==================== Export ====================
function exportJSON(type) {
    const endpoint = type === 'stats' ? '/api/export/stats/json' : '/api/export/alerts/json';
    fetch(endpoint)
        .then(res => res.json())
        .then(data => {
            const resultDiv = document.getElementById('export-result');
            if (resultDiv) {
                resultDiv.innerHTML = `<div class="result-box success"><p>✅ تم التصدير (${data.exported} سجل)</p><a href="/api/export/download/${data.filename}" class="btn btn-primary" download>تحميل</a></div>`;
            }
        });
}

function exportCSV() {
    fetch('/api/export/stats/csv')
        .then(res => res.json())
        .then(data => {
            const resultDiv = document.getElementById('export-result');
            if (resultDiv) {
                resultDiv.innerHTML = `<div class="result-box success"><p>✅ تم التصدير (${data.exported} سجل)</p><a href="/api/export/download/${data.filename}" class="btn btn-primary" download>تحميل</a></div>`;
            }
        });
}

function generateReport() {
    const resultDiv = document.getElementById('export-result');
    if (resultDiv) resultDiv.innerHTML = '<p class="loading">جاري إنشاء التقرير...</p>';
    setTimeout(() => {
        if (resultDiv) resultDiv.innerHTML = '<div class="result-box success"><p>✅ تم إنشاء التقرير</p><a href="#" class="btn btn-primary">📄 PDF</a></div>';
    }, 2000);
}

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('theme') === 'dark') document.body.classList.add('dark-mode');
    initCharts();
    loadProcesses();
    // تحميل بيانات الشبكة إذا كان القسم نشطاً
    if (document.getElementById('network')?.classList.contains('active')) {
        scanWiFi();
        loadDevices();
    }
});
