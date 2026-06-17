document.addEventListener("DOMContentLoaded", function () {
  const counters = document.querySelectorAll(".count-up");
  counters.forEach((counter) => {
    const target = Number(counter.dataset.target || counter.textContent || 0);
    const duration = 900;
    let start = 0;
    const stepTime = Math.max(Math.floor(duration / (target || 1)), 20);
    function update() {
      start += Math.max(1, Math.round(target / (duration / stepTime)));
      if (start >= target) {
        counter.textContent = target;
      } else {
        counter.textContent = start;
        requestAnimationFrame(update);
      }
    }
    update();
  });

  const hero = document.querySelector(".hero-banner");
  if (hero) {
    hero.classList.add("fade-in");
  }

  const sliderConfig = {
    transport: {
      values: ["car", "electric_vehicle", "bus", "train", "bicycle", "walking"],
      labels: ["Car", "Electric Vehicle", "Bus", "Train", "Bicycle", "Walking"],
      emissions: [2.5, 1.2, 1.2, 1.0, 0.5, 0.4],
      multiplier: 4,
    },
    food: {
      values: ["heavy_meat", "mixed", "vegetarian", "vegan"],
      labels: ["Heavy Meat", "Mixed Diet", "Vegetarian", "Vegan"],
      emissions: [5.2, 3.6, 2.5, 1.8],
      multiplier: 1,
    },
    electricity: {
      values: ["high", "medium", "low"],
      labels: ["High", "Medium", "Low"],
      emissions: [4.5, 2.8, 1.5],
      multiplier: 1,
    },
    shopping: {
      values: ["high", "medium", "low"],
      labels: ["High", "Medium", "Low"],
      emissions: [3.8, 2.2, 1.0],
      multiplier: 1,
    },
    flight: {
      values: ["frequently", "occasionally", "never"],
      labels: ["Frequently", "Occasionally", "Never"],
      emissions: [6.8, 3.0, 0.0],
      multiplier: 1,
    },
  };

  const updateCalculatorPreview = () => {
    const sliderElements = document.querySelectorAll(".slider-input");
    if (!sliderElements.length) return;
    let total = 0;
    const categories = {};

    sliderElements.forEach((field) => {
      const key = field.dataset.name;
      const config = sliderConfig[key];
      const value = field.value;
      const index = config.values.indexOf(value);
      const label = config.labels[index >= 0 ? index : 0];
      const emission = config.emissions[index >= 0 ? index : 0] * config.multiplier;
      categories[key] = emission;
      const labelElement = document.getElementById(`${key}Label`);
      const inputElement = document.getElementById(`${key}Input`);
      if (labelElement) labelElement.textContent = label;
      if (inputElement) inputElement.value = value;
      total += emission;
    });

    const score = Math.max(0, Math.min(100, Math.round(100 - total * 7)));
    const top = Object.entries(categories).reduce((best, current) => (current[1] > best[1] ? current : best))[0];
    const topNames = {
      transport: "Transportation",
      food: "Food",
      electricity: "Electricity",
      shopping: "Shopping",
      flight: "Air Travel",
    };
    const previewTotal = document.getElementById("previewTotal");
    const previewScore = document.getElementById("previewScore");
    const previewSource = document.getElementById("previewTopSource");
    const previewBar = document.getElementById("previewBar");
    if (previewTotal) previewTotal.textContent = total.toFixed(1);
    if (previewScore) previewScore.textContent = score;
    if (previewSource) previewSource.textContent = topNames[top] || "Transportation";
    if (previewBar) {
      previewBar.style.width = `${score}%`;
      previewBar.setAttribute("aria-valuenow", score);
    }
  };

  const sliderInputs = document.querySelectorAll(".slider-input");
  sliderInputs.forEach((slider) => slider.addEventListener("input", updateCalculatorPreview));
  updateCalculatorPreview();
});
