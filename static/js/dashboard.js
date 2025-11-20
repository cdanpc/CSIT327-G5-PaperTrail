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
    let metrics; 
    try { 
      metrics = JSON.parse(dataScript.textContent); 
      console.log('Learning Insights Metrics:', metrics);
    } catch(e){ 
      console.warn('Invalid metrics JSON', e); 
      return; 
    }
    const ctx = document.getElementById('insightsChart');
    if(!ctx || !window.Chart) return;

    const palette = metrics.palette || {
      uploads: '#0d6efd',
      quizzes_created: '#ffc107',
      quizzes_attempted: '#fd7e14',
      decks_created: '#0dcaf0',
      decks_reviewed: '#20c997',
      bookmarks: '#198754'
    };

    let currentMetric = 'uploads';
    
    // Helper: Create dataset for single metric
    const baseDataset = (key, labelOverride) => {
      const data = metrics[key] || [];
      const color = palette[key] || '#6c757d';
      return {
        label: labelOverride || key.charAt(0).toUpperCase()+key.slice(1),
        data: data,
        backgroundColor: data.map(() => color + 'B3'),
        borderColor: data.map(() => color),
        borderWidth: 1,
        borderRadius: 8,
        borderSkipped: false
      };
    };
    
    // Helper: Create stacked datasets for comparison metrics
    const stackedDatasets = (createdKey, engagedKey, labelPrefix) => [
      {
        label: `${labelPrefix} Created`,
        data: metrics[createdKey] || [],
        backgroundColor: palette[createdKey] + 'B3',
        borderColor: palette[createdKey],
        borderWidth: 1,
        borderRadius: 8,
        borderSkipped: false,
        stack: 'stack0'
      },
      {
        label: `${labelPrefix} Engaged`,
        data: metrics[engagedKey] || [],
        backgroundColor: palette[engagedKey] + 'B3',
        borderColor: palette[engagedKey],
        borderWidth: 1,
        borderRadius: 8,
        borderSkipped: false,
        stack: 'stack0'
      }
    ];

    function computeYAxisMax(metric){
      let values = [];
      if(metric === 'all') {
        // For 'all' view, we show aggregated totals for quizzes and decks
        if(Array.isArray(metrics.uploads)) values = values.concat(metrics.uploads);
        if(Array.isArray(metrics.quizzes_created) && Array.isArray(metrics.quizzes_attempted)) {
          for(let i=0; i<metrics.quizzes_created.length; i++) {
            values.push((metrics.quizzes_created[i] || 0) + (metrics.quizzes_attempted[i] || 0));
          }
        }
        if(Array.isArray(metrics.decks_created) && Array.isArray(metrics.decks_reviewed)) {
          for(let i=0; i<metrics.decks_created.length; i++) {
            values.push((metrics.decks_created[i] || 0) + (metrics.decks_reviewed[i] || 0));
          }
        }
        if(Array.isArray(metrics.bookmarks)) values = values.concat(metrics.bookmarks);
      } else if(metric === 'quizzes' || metric === 'decks') {
        // For stacked views, sum the two metrics per day
        const created = metric === 'quizzes' ? 'quizzes_created' : 'decks_created';
        const engaged = metric === 'quizzes' ? 'quizzes_attempted' : 'decks_reviewed';
        if(Array.isArray(metrics[created]) && Array.isArray(metrics[engaged])) {
          for(let i=0; i<metrics[created].length; i++) {
            values.push((metrics[created][i] || 0) + (metrics[engaged][i] || 0));
          }
        }
      } else if(Array.isArray(metrics[metric])) {
        values = metrics[metric];
      }
      const localMax = values.reduce((m,v)=> (typeof v === 'number' && v>m)? v:m, 0);
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
        plugins: { 
          legend: { 
            display: false,
            position: 'top',
            labels: { 
              boxWidth: 12,
              padding: 10,
              font: { size: 11 }
            }
          } 
        },
        animation: { duration: 450 },
        layout: { padding: { top: 10, bottom: 2, left: 8, right: 8 } },
        scales: {
          x: { 
            grid: { display: false, drawBorder: false }, 
            ticks: { padding: 4 }, 
            offset: true,
            stacked: false
          },
          y: { 
            beginAtZero: true, 
            grid: { color: 'rgba(102,126,234,0.1)', drawBorder: false }, 
            ticks: { precision: 0, padding: 8 }, 
            max: computeYAxisMax('uploads'),
            stacked: false
          }
        }
      }
    });

    function updateMetric(metric){
      console.log('Switching to metric:', metric);
      if(metric === 'all'){
        // Show 4 main categories side-by-side (Uploads, Quizzes, Decks, Bookmarks)
        // Aggregate created+engaged for Quizzes and Decks
        const quizTotal = (metrics.labels || []).map((_, i) => 
          (metrics.quizzes_created[i] || 0) + (metrics.quizzes_attempted[i] || 0)
        );
        const decksTotal = (metrics.labels || []).map((_, i) => 
          (metrics.decks_created[i] || 0) + (metrics.decks_reviewed[i] || 0)
        );
        
        console.log('All view - Quiz totals:', quizTotal);
        console.log('All view - Decks totals:', decksTotal);
        
        chart.data.datasets = [
          baseDataset('uploads','Uploads'),
          {
            label: 'Quizzes',
            data: quizTotal,
            backgroundColor: quizTotal.map(() => palette.quizzes_created + 'B3'),
            borderColor: quizTotal.map(() => palette.quizzes_created),
            borderWidth: 1,
            borderRadius: 8,
            borderSkipped: false
          },
          {
            label: 'Decks',
            data: decksTotal,
            backgroundColor: decksTotal.map(() => palette.decks_created + 'B3'),
            borderColor: decksTotal.map(() => palette.decks_created),
            borderWidth: 1,
            borderRadius: 8,
            borderSkipped: false
          },
          baseDataset('bookmarks','Bookmarks')
        ];
        chart.options.plugins.legend.display = true;
        chart.options.scales.x.stacked = false;
        chart.options.scales.y.stacked = false;
      } else if(metric === 'quizzes') {
        // Stacked bar: Created vs Attempted
        console.log('Quizzes view - Created:', metrics.quizzes_created);
        console.log('Quizzes view - Attempted:', metrics.quizzes_attempted);
        chart.data.datasets = stackedDatasets('quizzes_created', 'quizzes_attempted', 'Quizzes');
        chart.options.plugins.legend.display = true;
        chart.options.scales.x.stacked = true;
        chart.options.scales.y.stacked = true;
      } else if(metric === 'decks') {
        // Stacked bar: Cards Created vs Cards Reviewed
        console.log('Decks view - Created:', metrics.decks_created);
        console.log('Decks view - Reviewed:', metrics.decks_reviewed);
        chart.data.datasets = stackedDatasets('decks_created', 'decks_reviewed', 'Cards');
        chart.options.plugins.legend.display = true;
        chart.options.scales.x.stacked = true;
        chart.options.scales.y.stacked = true;
      } else {
        // Single metric view
        if(!metrics[metric]) return;
        console.log('Single metric view:', metric, metrics[metric]);
        chart.data.datasets = [ baseDataset(metric) ];
        chart.options.plugins.legend.display = false;
        chart.options.scales.x.stacked = false;
        chart.options.scales.y.stacked = false;
      }
      currentMetric = metric;
      chart.options.scales.y.max = computeYAxisMax(metric);
      chart.update();
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
