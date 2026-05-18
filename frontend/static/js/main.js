const socket = io();

let cpuChart, memoryChart, diskChart;

socket.on('connect', function() {
    console.log('Connected to server');
    updateStatus('متصل ✅');
});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
    updateStatus('مقطوع ❌');
});

function updateStatus(status) {
    document.getElementById('status').textContent = status;
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));

    document.getElementById(sectionId).classList.add('active');

    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');
}

function initCharts() {
    const cpuCtx = document.getElementById('cpuChart').getContext('2d');
    cpuChart = new Chart(cpuCtx, {
        type: 'doughnut',
        data: {
            labels: ['مستخدم', 'متاح'],
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#e94560', '#1a1a2e'],
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

    const memoryCtx = document.getElementById('memoryChart').getContext('2d');
    memoryChart = new Chart(memoryCtx, {
        type: 'doughnut',
        data: {
            labels: ['مستخدم', 'متاح'],
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#f39c12', '#1a1a2e'],
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

async function fetchSystemInfo() {
    try {
        const response = await fetch('/api/system-info');
        const data = await response.json();

        document.getElementById('cpu-value').textContent = data.cpu.toFixed(1) + '%';
        cpuChart.data.datasets[0].data = [data.cpu, 100 - data.cpu];
        cpuChart.update();

        document.getElementById('memory-value').textContent = data.memory.percent.toFixed(1) + '%';
        memoryChart.data.datasets[0].data = [data.memory.percent, 100 - data.memory.percent];
        memoryChart.update();

        document.getElementById('disk-value').textContent = data.disk.percent.toFixed(1) + '%';
        diskChart.data.datasets[0].data = [data.disk.percent, 100 - data.disk.percent];
        diskChart.update();

        const bootTime = new Date(data.uptime * 1000);
        const now = new Date();
        const uptime = Math.floor((now - bootTime) / 1000);
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = uptime % 60;
        document.getElementById('uptime-value').textContent = 
            `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    } catch (error) {
        console.error('Error fetching system info:', error);
    }
}

async function fetchProcessCount() {
    try {
        const response = await fetch('/api/process-count');
        const data = await response.json();
        document.getElementById('process-count').textContent = data.process_count;
    } catch (error) {
        console.error('Error fetching process count:', error);
    }
}

async function fetchNetworkInfo() {
    try {
        const response = await fetch('/api/network-info');
        const data = await response.json();
        document.getElementById('network-sent').textContent = 
            (data.bytes_sent / (1024 ** 2)).toFixed(2) + ' MB';
        document.getElementById('network-recv').textContent = 
            (data.bytes_recv / (1024 ** 2)).toFixed(2) + ' MB';
    } catch (error) {
        console.error('Error fetching network info:', error);
    }
}

function startUpdating() {
    setInterval(fetchSystemInfo, 1000);
    setInterval(fetchProcessCount, 2000);
    setInterval(fetchNetworkInfo, 2000);
}

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    fetchSystemInfo();
    fetchProcessCount();
    fetchNetworkInfo();
    startUpdating();
});
