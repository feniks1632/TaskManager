document.addEventListener('DOMContentLoaded', function () {
    const chartElement = document.getElementById('weeklyChart');
    if (!chartElement) return;

    const ctx = chartElement.getContext('2d');
    const labels = JSON.parse(chartElement.dataset.labels);
    const data = JSON.parse(chartElement.dataset.data);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Создано задач',
                data: data,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
});