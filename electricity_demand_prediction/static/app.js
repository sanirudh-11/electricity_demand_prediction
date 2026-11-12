const commonOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { backgroundColor: "#17363d", padding: 10 } },
  scales: {
    x: { grid: { display: false }, ticks: { color: "#91a0a5", maxTicksLimit: 8, font: { size: 10 } } },
    y: { grid: { color: "#edf1f2" }, ticks: { color: "#91a0a5", font: { size: 10 } } }
  }
};
async function loadOverview() {
  const res = await fetch("/api/overview");
  const d = await res.json();
  new Chart(document.getElementById("dailyChart"), {
    type: "line", data: { labels: d.daily_labels, datasets: [{ data: d.daily_values,
      borderColor: "#0b9675", backgroundColor: "rgba(11,150,117,.10)", fill: true,
      tension: .35, pointRadius: 2, pointHoverRadius: 5, borderWidth: 2 }] },
    options: { ...commonOptions, scales: { ...commonOptions.scales, y: { ...commonOptions.scales.y, title: { display: true, text: "Demand (MW)", color: "#84949a" } } } }
  });
  new Chart(document.getElementById("hourChart"), {
    type: "bar", data: { labels: d.hour_labels, datasets: [{ data: d.hour_values,
      backgroundColor: d.hour_values.map((_,i)=> i>=17 && i<=21 ? "#0b9675" : "#b8e5d7"),
      borderRadius: 4, maxBarThickness: 15 }] },
    options: { ...commonOptions, scales: { ...commonOptions.scales, x: { ...commonOptions.scales.x, ticks: { ...commonOptions.scales.x.ticks, maxTicksLimit: 8 } } } }
  });
}
async function loadRows() {
  const res = await fetch("/api/data"); const rows = await res.json();
  document.getElementById("dataRows").innerHTML = rows.slice(-12).reverse().map(r =>
    `<tr><td>${r.datetime}</td><td><b>${r.demand_mw.toLocaleString()} MW</b></td><td>${r.temperature_c} °C</td><td>${r.humidity}%</td></tr>`
  ).join("");
}
const dateInput = document.getElementById("datetime");
const now = new Date(); now.setMinutes(0,0,0); now.setDate(now.getDate()+1);
dateInput.value = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}-${String(now.getDate()).padStart(2,"0")}T${String(now.getHours()).padStart(2,"0")}:00`;
document.getElementById("predictForm").addEventListener("submit", async e => {
  e.preventDefault();
  const btn = document.getElementById("predictBtn"); btn.disabled = true; btn.textContent = "Calculating…";
  const panel = document.getElementById("resultPanel");
  try {
    const response = await fetch("/api/predict", { method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ datetime: dateInput.value, temperature: document.getElementById("temperature").value,
        humidity: document.getElementById("humidity").value }) });
    const data = await response.json(); if (!response.ok) throw new Error(data.error || "Prediction failed");
    document.getElementById("resultTitle").textContent = "Estimated electricity demand";
    document.getElementById("resultNumber").innerHTML = `${data.demand.toLocaleString()} <small>MW</small>`;
    document.getElementById("resultNote").textContent = `${data.note} This is an educational estimate, not an official grid forecast.`;
    panel.scrollIntoView({behavior:"smooth",block:"nearest"});
  } catch(err) {
    document.getElementById("resultTitle").textContent = "Could not generate prediction";
    document.getElementById("resultNumber").textContent = "—";
    document.getElementById("resultNote").textContent = err.message;
  } finally { btn.disabled = false; btn.innerHTML = 'Generate prediction <span>→</span>'; }
});
loadOverview(); loadRows();
