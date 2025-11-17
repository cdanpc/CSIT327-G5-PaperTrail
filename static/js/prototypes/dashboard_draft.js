'use strict';

document.addEventListener('DOMContentLoaded', function () {
  // Viewport height polyfill for reliable 100vh CSS on some browsers
  function setVh() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
  }
  setVh();
  window.addEventListener('resize', setVh);
  // Toast setup
  const toastEl = document.getElementById('inProgressToast');
  let toast;
  if (toastEl && window.bootstrap && bootstrap.Toast) {
    toast = new bootstrap.Toast(toastEl, { delay: 2000 });
  }

  // Utility to show toast
  function showInProgress() {
    if (toast) {
      toast.show();
    } else if (toastEl) {
      // Fallback if bootstrap.Toast not found
      toastEl.classList.add('show');
      setTimeout(() => toastEl.classList.remove('show'), 2000);
    }
  }

  // Intercept all in-progress features and anchors with href="#"
  const inertSelectors = '[data-feature="in-progress"], a[href="#"]';
  document.querySelectorAll(inertSelectors).forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      showInProgress();
    });
    // Keyboard accessibility for non-anchor tiles
    if (!el.hasAttribute('href')) {
      el.setAttribute('tabindex', '0');
    }
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        showInProgress();
      }
    });
  });

  // Animate stat numbers
  const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);
  function animateNumber(el, target, duration = 1000) {
    const start = 0;
    const startTime = performance.now();
    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(1, elapsed / duration);
      const eased = easeOutCubic(progress);
      const value = Math.round(start + (target - start) * eased);
      el.textContent = value.toLocaleString();
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
  document.querySelectorAll('.stat-number[data-target]').forEach((el) => {
    const target = parseInt(el.getAttribute('data-target'), 10) || 0;
    animateNumber(el, target);
  });

  // Initialize Chart.js bar chart with metric switching
  const ctx = document.getElementById('insightsChart');
  let insightsChart;
  
  if (ctx && window.Chart) {
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    // Define different datasets for each metric
    const metricsData = {
      uploads: {
        label: 'Uploads',
        data: [1, 2, 3, 2, 4, 1, 0],
        backgroundColor: 'rgba(13, 110, 253, 0.5)',
        borderColor: 'rgba(13, 110, 253, 1)',
      },
      quizzes: {
        label: 'Quiz Attempts',
        data: [2, 3, 1, 4, 2, 3, 1],
        backgroundColor: 'rgba(255, 193, 7, 0.5)',
        borderColor: 'rgba(255, 193, 7, 1)',
      },
      flashcards: {
        label: 'Flashcard Practice',
        data: [5, 8, 6, 10, 7, 4, 2],
        backgroundColor: 'rgba(13, 202, 240, 0.5)',
        borderColor: 'rgba(13, 202, 240, 1)',
      },
      views: {
        label: 'Resource Views',
        data: [15, 22, 18, 25, 20, 12, 8],
        backgroundColor: 'rgba(25, 135, 84, 0.5)',
        borderColor: 'rgba(25, 135, 84, 1)',
      },
    };
    
    // Initialize chart with default metric (uploads)
    insightsChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: metricsData.uploads.label,
            data: metricsData.uploads.data,
            backgroundColor: metricsData.uploads.backgroundColor,
            borderColor: metricsData.uploads.borderColor,
            borderWidth: 1,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } },
        },
        plugins: {
          legend: { display: false },
          tooltip: { intersect: false, mode: 'index' },
        },
      },
    });
    
    // Handle metric switching
    document.querySelectorAll('input[name="metricType"]').forEach((radio) => {
      radio.addEventListener('change', (e) => {
        const metric = e.target.value;
        const metricData = metricsData[metric];
        
        if (metricData && insightsChart) {
          // Update chart data
          insightsChart.data.datasets[0].label = metricData.label;
          insightsChart.data.datasets[0].data = metricData.data;
          insightsChart.data.datasets[0].backgroundColor = metricData.backgroundColor;
          insightsChart.data.datasets[0].borderColor = metricData.borderColor;
          
          // Animate the update
          insightsChart.update('active');
        }
      });
    });
  }

  // Calendar today marker (simple)
  const dayMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const today = new Date();
  const todayKey = dayMap[today.getDay()];
  document.querySelectorAll('.calendar-glance [data-day]').forEach((li) => {
    if (li.getAttribute('data-day') === todayKey) {
      li.classList.add('today');
    }
  });
});
