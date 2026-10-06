/**
 * AI Workout & Diet Plan - Main Client JS
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Auto dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = "0";
      alert.style.transition = "opacity 0.5s ease";
      setTimeout(() => alert.remove(), 500);
    }, 6000);
  });

  // 2. Mobile Nav Toggle
  const toggleBtn = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }

  // 3. Tab System
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      const container = btn.closest(".tabs-wrapper") || document;

      container.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      container.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const pane = document.getElementById(targetId);
      if (pane) pane.classList.add("active");
    });
  });

  // 4. Quick Live BMI Calculator Widget (Landing page / Profile page)
  const quickBmiForm = document.getElementById("quick-bmi-form");
  if (quickBmiForm) {
    quickBmiForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const height = parseFloat(document.getElementById("bmi-height").value);
      const weight = parseFloat(document.getElementById("bmi-weight").value);
      const resultBox = document.getElementById("bmi-result-box");

      if (!height || !weight || height <= 0 || weight <= 0) {
        alert("Please enter valid height and weight numbers.");
        return;
      }

      try {
        const res = await fetch("/api/calculate-bmi", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ height, weight })
        });
        const data = await res.json();
        if (data.status === "success" && resultBox) {
          resultBox.style.display = "block";
          document.getElementById("bmi-val").textContent = data.bmi;
          document.getElementById("bmi-cat").textContent = data.category;
          document.getElementById("bmi-cat").className = `badge badge-${data.color}`;
          document.getElementById("bmi-desc").textContent = data.description;
          document.getElementById("bmi-ideal").textContent = `Ideal Range: ${data.ideal_range}`;
        }
      } catch (err) {
        console.error("BMI calculation error:", err);
      }
    });
  }

  // 5. Video Modal Handling
  const videoModal = document.getElementById("video-modal");
  const modalIframe = document.getElementById("modal-video-frame");
  const modalTitle = document.getElementById("modal-video-title");

  window.openVideoModal = (embedUrl, title) => {
    if (videoModal && modalIframe) {
      modalIframe.src = embedUrl + "?autoplay=1";
      if (modalTitle) modalTitle.textContent = title;
      videoModal.style.display = "flex";
    }
  };

  window.closeVideoModal = () => {
    if (videoModal && modalIframe) {
      modalIframe.src = "";
      videoModal.style.display = "none";
    }
  };

  if (videoModal) {
    videoModal.addEventListener("click", (e) => {
      if (e.target === videoModal) window.closeVideoModal();
    });
  }
});
