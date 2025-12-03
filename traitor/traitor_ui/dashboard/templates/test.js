const ws = new WebSocket("ws://" + window.location.host + "/ws/live/");
const ctx = document.getElementById("chart").getContext("2d");

const chart = new Chart(ctx, {
    type: "line",
    data: { labels: [], datasets: [{ data: [] }] },
    options: { animation: false }
});

ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    chart.data.labels.push("");
    chart.data.datasets[0].data.push(msg.value);
    if (chart.data.labels.length > 80) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    chart.update();
};