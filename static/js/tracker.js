/**
 * AI Workout & Diet Plan - Progress Tracker & Chart.js Visualizations
 */

document.addEventListener("DOMContentLoaded", async () => {
  const chartCanvas = document.getElementById("progressChart");
  if (!chartCanvas) return;

  try {
    const response = await fetch("/api/progress/stats");
    const data = await response.json();

    if (data.status !== "success" || !data.labels || data.labels.length === 0) {
      const emptyMsg = document.getElementById("chart-empty-msg");
      if (emptyMsg) emptyMsg.style.display = "block";
      chartCanvas.style.display = "none";
      return;
    }

    const ctx = chartCanvas.getContext("2d");

    // Target weight line
    const targetLine = new Array(data.labels.length).fill(data.target_weight);

    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "Recorded Weight (kg)",
            data: data.weights,
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.15)",
            borderWidth: 3,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: "#10b981",
            pointRadius: 5
          },
          {
            label: "Target Goal (kg)",
            data: targetLine,
            borderColor: "#f59e0b",
            borderWidth: 2,
            borderDash: [6, 6],
            fill: false,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: "#cbd5e1", font: { size: 12 } }
          },
          tooltip: {
            backgroundColor: "#1e293b",
            titleColor: "#fff",
            bodyColor: "#cbd5e1",
            borderColor: "#334155",
            borderWidth: 1
          }
        },
        scales: {
          x: {
            grid: { color: "rgba(51, 65, 85, 0.4)" },
            ticks: { color: "#94a3b8" }
          },
          y: {
            grid: { color: "rgba(51, 65, 85, 0.4)" },
            ticks: { color: "#94a3b8" }
          }
        }
      }
    });

    // Secondary BMI trajectory chart if available
    const bmiCanvas = document.getElementById("bmiTrajectoryChart");
    if (bmiCanvas && data.bmis) {
      const bmiCtx = bmiCanvas.getContext("2d");
      new Chart(bmiCtx, {
        type: "line",
        data: {
          labels: data.labels,
          datasets: [{
            label: "BMI History",
            data: data.bmis,
            borderColor: "#06b6d4",
            backgroundColor: "rgba(6, 182, 212, 0.12)",
            borderWidth: 2.5,
            fill: true,
            tension: 0.3,
            pointBackgroundColor: "#06b6d4",
            pointRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: "#cbd5e1" } }
          },
          scales: {
            x: { grid: { color: "rgba(51, 65, 85, 0.3)" }, ticks: { color: "#94a3b8" } },
            y: { grid: { color: "rgba(51, 65, 85, 0.3)" }, ticks: { color: "#94a3b8" } }
          }
        }
      });
    }

  } catch (err) {
    console.error("Failed to load progress stats:", err);
  }
});

// Quick Water Intake Logging from Dashboard
window.logQuickWater = async (amountMl = 250) => {
  try {
    const res = await fetch("/api/progress/quick-water", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount_ml: amountMl })
    });
    const data = await res.json();
    if (data.status === "success") {
      const displayEl = document.getElementById("dashboard-water-val");
      if (displayEl) {
        displayEl.textContent = `${(data.total_water_ml / 1000).toFixed(2)} L`;
      }
      const toast = document.createElement("div");
      toast.className = "alert alert-success";
      toast.style.position = "fixed";
      toast.style.bottom = "20px";
      toast.style.right = "20px";
      toast.style.zIndex = "9999";
      toast.textContent = `+${amountMl}ml logged! Total: ${(data.total_water_ml / 1000).toFixed(2)} L`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    }
  } catch (err) {
    console.error("Error logging water:", err);
  }
};
