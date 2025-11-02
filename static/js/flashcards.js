(function(){
  function ready(fn){
    if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',fn);}else{fn();}
  }
  function applyDataWidth(){
    document.querySelectorAll('.progress-bar[data-width]').forEach(function(el){
      var val = el.getAttribute('data-width');
      if(val!==null && val!==''){ el.style.width = String(val).trim() + '%'; }
    });
  }
  ready(function(){
    applyDataWidth();

    var dataEl = document.getElementById('cardsData');
    if(!dataEl){ return; }
    var cards = [];
    try { cards = JSON.parse(dataEl.textContent || '[]'); } catch(e){ cards = []; }
    var total = cards.length;

    var flashcard = document.getElementById('flashcard');
    var flashcardInner = document.getElementById('flashcardInner');
    var frontEl = document.getElementById('cardFront');
    var backEl = document.getElementById('cardBack');
    var prevBtn = document.getElementById('prevBtn');
    var nextBtn = document.getElementById('nextBtn');
    var flipBtn = document.getElementById('flipBtn');
    var currentIndexEl = document.getElementById('currentIndex');
    var totalCountEl = document.getElementById('totalCount');
    var progress = document.getElementById('studyProgress');

    totalCountEl && (totalCountEl.textContent = String(total));

    var idx = 0;

    function render(){
      if(total === 0){
        frontEl.textContent = 'No cards in this deck yet.';
        backEl.textContent = '';
        flipBtn.disabled = true;
        nextBtn.disabled = true;
        prevBtn.disabled = true;
        progress && (progress.style.width = '0%');
        currentIndexEl && (currentIndexEl.textContent = '0');
        return;
      }
      var card = cards[idx];
      frontEl.textContent = card.front_text || '';
      backEl.textContent = card.back_text || '';
      flashcard.classList.remove('is-flipped');
      currentIndexEl && (currentIndexEl.textContent = String(idx+1));
      var pct = Math.round(((idx) / total) * 100);
      progress && (progress.style.width = pct + '%');
      prevBtn.disabled = (idx === 0);
      nextBtn.textContent = (idx === total - 1) ? 'Finish' : 'Next';
    }

    function next(){
      if(idx < total - 1){
        idx += 1; render();
      } else {
        // Finished - navigate back to deck detail
        var backUrl = window.location.pathname.replace(/\/study\/?$/, '/');
        window.location.assign(backUrl);
      }
    }
    function prev(){ if(idx>0){ idx -= 1; render(); } }
    function flip(){ flashcard.classList.toggle('is-flipped'); }

    flipBtn && flipBtn.addEventListener('click', function(){ flip(); });
    nextBtn && nextBtn.addEventListener('click', function(){ next(); });
    prevBtn && prevBtn.addEventListener('click', function(){ prev(); });
    flashcard && flashcard.addEventListener('click', function(){ flip(); });

    render();
  });
})();
