// Dashboard JS: counters, multi-metric insights chart, calendar events
(function(){
  function animateCounters() {
    document.querySelectorAll('.stat-value[data-target]').forEach(el => {
      const target = parseInt(el.getAttribute('data-target')||'0',10);
      let current = 0;
      const step = Math.max(1, Math.ceil(target/40));
      const timer = setInterval(()=>{
        current += step;
        if(current >= target){ current = target; clearInterval(timer); }
        el.textContent = current;
      }, 20);
    });
  }

  function initInsightsChart() {
    const dataScript = document.getElementById('weekly-metrics-data');
    if(!dataScript) return;
    let metrics; try { metrics = JSON.parse(dataScript.textContent); } catch(e){ console.warn('Invalid metrics JSON', e); return; }
    const ctx = document.getElementById('insightsChart');
    if(!ctx || !window.Chart) return;

    const palette = metrics.palette || {
      uploads: '#0d6efd',
      quizzes: '#ffc107',
      flashcards: '#0dcaf0',
      activity: '#198754'
    };

    let currentMetric = 'uploads';
    const baseDataset = (key,labelOverride) => ({
      label: labelOverride || key.charAt(0).toUpperCase()+key.slice(1),
      data: metrics[key] || [],
      backgroundColor: (metrics[key]||[]).map(()=> palette[key] + 'B3'),
      borderRadius: 8,
      borderSkipped: false
    });

    function computeYAxisMax(metric){
      // Collect values for selected metric or all metrics
      let values = [];
      if(metric === 'all') {
        ['uploads','quizzes','flashcards','activity'].forEach(k => { if(Array.isArray(metrics[k])) values = values.concat(metrics[k]); });
      } else if(Array.isArray(metrics[metric])) {
        values = metrics[metric];
      }
      const localMax = values.reduce((m,v)=> (typeof v === 'number' && v>m)? v:m, 0);
      // Next multiple of 10 strictly greater than localMax; if all zeros, use 10
      const base = Math.floor(localMax / 10) * 10;
      return base + 10;
    }
    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: metrics.labels || [],
        datasets: [ baseDataset('uploads','Uploads') ]
      },
      options: {
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        animation: { duration: 450 },
        // Minimal padding for bars to reach close to bottom edge
        layout: { padding: { top: 10, bottom: 2, left: 8, right: 8 } },
        scales: {
          x: { 
            grid: { display: false, drawBorder: false }, 
            ticks: { padding: 4 }, 
            offset: true 
          },
          y: { 
            beginAtZero: true, 
            grid: { color: 'rgba(102,126,234,0.1)', drawBorder: false }, 
            ticks: { precision: 0, padding: 8 }, 
            max: computeYAxisMax('uploads') 
          }
        }
      }
    });

    // No height sync required; fixed px heights handled via CSS

    function updateMetric(metric){
      if(metric === 'all'){
        chart.data.datasets = ['uploads','quizzes','flashcards','activity'].filter(k=>metrics[k]).map(k=> baseDataset(k));
      } else {
        if(!metrics[metric]) return;
        chart.data.datasets = [ baseDataset(metric) ];
      }
      currentMetric = metric;
      chart.options.plugins.legend.display = metric === 'all';
      // Update y-axis suggestedMax dynamically
      chart.options.scales.y.max = computeYAxisMax(metric);
      chart.update();
      // No height sync required; fixed px heights handled via CSS
    }

    document.querySelectorAll('input[name="metricType"]').forEach(radio => {
      radio.addEventListener('change', e => {
        if(e.target.checked){ updateMetric(e.target.value); }
      });
    });
  }

  function initCalendarEvents(){
    const script = document.getElementById('calendar-events-data');
    if(!script) return;
    let events; try { events = JSON.parse(script.textContent); } catch(e){ return; }
    // Attach tooltips / dots dynamically (if calendar was rendered differently)
    document.querySelectorAll('.calendar-day').forEach(cell => {
      const day = cell.getAttribute('data-day');
      if(day && events[day] && events[day].length){
        cell.classList.add('has-event');
        // If not already an event-dot (template added first item), add one
        if(!cell.querySelector('.event-dot')){
          const dot = document.createElement('div');
          dot.className = 'event-dot';
          dot.title = events[day][0].title;
          cell.appendChild(dot);
        }
        if(events[day].length > 1 && !cell.querySelector('.event-count-badge')){
          const badge = document.createElement('span');
          badge.className = 'event-count-badge';
          badge.textContent = `+${events[day].length}`;
          cell.appendChild(badge);
        }
      }
    });
    // Modal display for events
    const modalEl = document.getElementById('calendarEventsModal');
    const listEl = document.getElementById('calendarEventsList');
    let modalInstance = null;
    if(modalEl && window.bootstrap){ modalInstance = new bootstrap.Modal(modalEl); }
    document.addEventListener('click', (e) => {
      const targetCell = e.target.closest('.calendar-day.has-event');
      if(!targetCell) return;
      const day = targetCell.getAttribute('data-day');
      const dayEvents = events[day];
      if(!dayEvents || !listEl || !modalInstance) return;
      listEl.innerHTML = '';
      dayEvents.forEach(ev => {
        const li = document.createElement('li');
        const badge = document.createElement('span');
        badge.className = 'event-badge ' + ev.type;
        badge.textContent = ev.type.replace('_',' ').replace('quiz','Quiz').replace('resource','Resource').replace('flashcard','Flashcards');
        const titleSpan = document.createElement('span');
        titleSpan.textContent = ev.title;
        li.appendChild(badge);
        li.appendChild(titleSpan);
        listEl.appendChild(li);
      });
      const label = document.getElementById('calendarEventsModalLabel');
      if(label){ label.textContent = `Events on ${day}`; }
      modalInstance.show();
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    animateCounters();
    initInsightsChart();
    initCalendarEvents();
    // Fixed heights; no dynamic resize syncing needed
    // In-progress toast logic
    const toastEl = document.getElementById('inProgressToast');
    if(toastEl && window.bootstrap){
      const toast = new bootstrap.Toast(toastEl, { delay: 2500 });
      document.querySelectorAll('[data-feature="in-progress"]').forEach(el => {
        el.addEventListener('click', e => {
          e.preventDefault(); toast.show();
        });
      });
    }
  });
})();
