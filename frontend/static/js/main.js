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
}

// إنشاء الرسوم البيانية
function initCharts() {
    // CPU Chart - Line Chart
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
            plugins: {
                legend: { 
                    labels: { color: '#eaeaea' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#aaa' },
                    grid: { color: '#333' }
                },
                x: {
                    ticks: { color: '#aaa' },
                    grid: { color: '#333' }
                }
            }
        }
    });

    // Memory Chart - Line Chart
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
            plugins: {
                legend: { 
                    labels: { color: '#eaeaea' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#aaa' },
                    grid: { color: '#333' }
                },
                x: {
                    ticks: { color: '#aaa' },
                    grid: { color: '#333' }
                }
            }
        }
    });

    // Disk Chart - Doughnut
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
            plugins: {
                legend: { labels: { color: '#eaeaea' } }
            }
        }
    });
}

// تحديث لوحة التحكم بالبيانات الحية
function updateDashboard(data) {
    // تحديث CPU
    const cpuValue = data.cpu.percent;
    document.getElementById('cpu-value').textContent = cpuValue.toFixed(1) + '%';
    
    // إضافة للـ History
    cpuHistory.push(cpuValue);
    if (cpuHistory.length > maxHistoryPoints) {
        cpuHistory.shift();
    }
    
    // تحديث CPU Chart
    updateLineChart(cpuChart, cpuHistory, 'CPU');

    // تحديث Memory
    const memoryValue = data.memory.percent;
    document.getElementById('memory-value').textContent = memoryValue.toFixed(1) + '%';
    
    memoryHistory.push(memoryValue);
    if (memoryHistory.length > maxHistoryPoints) {
        memoryHistory.shift();
    }
    
    updateLineChart(memoryChart, memoryHistory, 'Memory');

    // تحديث Disk
    const diskValue = data.disk.percent;
    document.getElementById('disk-value').textContent = diskValue.toFixed(1) + '%';
    diskChart.data.datasets[0].data = [diskValue, 100 - diskValue];
    diskChart.update();

    // تحديث Network
    const sentMB = (data.network.bytes_sent / (1024 ** 2)).toFixed(2);
    const recvMB = (data.network.bytes_recv / (1024 ** 2)).toFixed(2);
    document.getElementById('network-sent').textContent = sentMB + ' MB';
    document.getElementById('network-recv').textContent = recvMB + ' MB';

    // تحديث Uptime
    updateUptime(data.uptime);

    // تحديث عدد العمليات
    document.getElementById('process-count').textContent = data.process_count;

    // تحديث الألوان حسب الاستخدام
    updateCardColors(cpuValue, memoryValue, diskValue);
}

// تحديث الـ Line Chart
function updateLineChart(chart, data, label) {
    chart.data.labels = data.map((_, i) => i);
    chart.data.datasets[0].data = data;
    chart.update('none');
}

// تحديث وقت التشغيل
function updateUptime(uptime) {
    const seconds = uptime.total_seconds;
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    const formatted = `${days}d ${hours}h ${minutes}m ${secs}s`;
    document.getElementById('uptime-value').textContent = formatted;
}

// تحديث ألوان الـ Cards حسب الخطورة
function updateCardColors(cpu, memory, disk) {
    const cpuCard = document.querySelector('[data-metric="cpu"]');
    const memoryCard = document.querySelector('[data-metric="memory"]');
    const diskCard = document.querySelector('[data-metric="disk"]');

    if (cpuCard) {
        cpuCard.style.borderColor = cpu > 80 ? '#e74c3c' : cpu > 50 ? '#f39c12' : '#0f3460';
    }
    if (memoryCard) {
        memoryCard.style.borderColor = memory > 80 ? '#e74c3c' : memory > 50 ? '#f39c12' : '#0f3460';
    }
    if (diskCard) {
        diskCard.style.borderColor = disk > 80 ? '#e74c3c' : disk > 50 ? '#f39c12' : '#0f3460';
    }
}

// تهيئة الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
});
