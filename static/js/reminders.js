/**
 * AI Workout & Diet Plan - Notifications & Reminder Service
 */

document.addEventListener("DOMContentLoaded", () => {
  // Check notification permission
  const requestBtn = document.getElementById("request-notif-btn");
  if (requestBtn) {
    if ("Notification" in window && Notification.permission === "granted") {
      requestBtn.textContent = "🔔 Desktop Alerts Enabled";
      requestBtn.disabled = true;
      requestBtn.classList.remove("btn-primary");
      requestBtn.classList.add("btn-secondary");
    } else {
      requestBtn.addEventListener("click", requestNotificationPermission);
    }
  }

  // Periodic check for active reminders (every 30 seconds)
  setInterval(checkRemindersDue, 30000);
  checkRemindersDue();
});

async function requestNotificationPermission() {
  if (!("Notification" in window)) {
    alert("This browser does not support desktop notifications.");
    return;
  }

  const permission = await Notification.requestPermission();
  const requestBtn = document.getElementById("request-notif-btn");

  if (permission === "granted") {
    new Notification("Fitness Notifications Enabled!", {
      body: "You will now receive timely reminders for workouts, hydration, and nutrition.",
      icon: "/static/images/badge.png"
    });
    if (requestBtn) {
      requestBtn.textContent = "🔔 Desktop Alerts Enabled";
      requestBtn.disabled = true;
      requestBtn.classList.remove("btn-primary");
      requestBtn.classList.add("btn-secondary");
    }
  }
}

// Check if any reminder matches the current hour and minute
async function checkRemindersDue() {
  try {
    const res = await fetch("/api/reminders/active");
    const data = await res.json();
    if (data.status !== "success" || !data.reminders) return;

    const now = new Date();
    const currentHours = String(now.getHours()).padStart(2, "0");
    const currentMinutes = String(now.getMinutes()).padStart(2, "0");
    const currentTimeStr = `${currentHours}:${currentMinutes}`;

    // Day of week
    const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const currentDay = days[now.getDay()];

    data.reminders.forEach(rem => {
      const remDays = rem.days_of_week ? rem.days_of_week.split(",") : [];
      if (rem.reminder_time === currentTimeStr && remDays.includes(currentDay)) {
        // Prevent duplicate spam in the same minute using sessionStorage
        const key = `notified_${rem.id}_${currentTimeStr}`;
        if (!sessionStorage.getItem(key)) {
          triggerFitnessAlert(rem);
          sessionStorage.setItem(key, "true");
        }
      }
    });
  } catch (err) {
    console.error("Reminder check failed:", err);
  }
}

function triggerFitnessAlert(rem) {
  // 1. Desktop Notification
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(`Fitness Reminder: ${rem.title}`, {
      body: `Time for your scheduled ${rem.reminder_type}! Stay consistent with your goals.`,
      icon: "/static/images/badge.png"
    });
  }

  // 2. In-app toast notification
  const toast = document.createElement("div");
  toast.className = "alert alert-info";
  toast.style.position = "fixed";
  toast.style.top = "80px";
  toast.style.right = "20px";
  toast.style.zIndex = "10000";
  toast.style.boxShadow = "0 8px 24px rgba(0,0,0,0.5)";
  toast.innerHTML = `
    <div>
      <h4 style="margin: 0 0 4px; font-weight: bold;">⏰ ${rem.title}</h4>
      <p style="margin: 0; font-size: 0.85rem;">It's time for your ${rem.reminder_type} activity!</p>
    </div>
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 8000);
}

// Toggle Reminder active state
window.toggleReminder = async (remId) => {
  try {
    const res = await fetch(`/api/reminders/toggle/${remId}`, { method: "POST" });
    const data = await res.json();
    if (data.status === "success") {
      window.location.reload();
    }
  } catch (err) {
    console.error("Failed to toggle reminder:", err);
  }
};
