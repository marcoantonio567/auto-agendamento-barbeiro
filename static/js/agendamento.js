document.addEventListener('DOMContentLoaded',()=>{
  const inp = document.getElementById('client_name');
  if(inp){
    const saved = localStorage.getItem('client_name');
    if(saved) inp.value = saved;
    inp.addEventListener('input',()=>localStorage.setItem('client_name',inp.value));
  }
  document.querySelectorAll('.options').forEach(container=>{
    const cards = container.querySelectorAll('label.option-card');
    const autoAttr = container.getAttribute('data-autosubmit');
    const autoSubmit = autoAttr !== 'false';
    cards.forEach(card=>{
      const input = card.querySelector('input[type="radio"]');
      if(!input) return;
      input.addEventListener('change',()=>{
        const name = input.name;
        container.querySelectorAll(`input[type="radio"][name="${name}"]`).forEach(r=>{
          const parent = r.closest('label.option-card');
          if(parent) parent.classList.remove('selected');
        });
        card.classList.add('selected');
        const form = input.closest('form');
        if(form){
          if(autoSubmit){
            if(typeof form.requestSubmit === 'function'){
              form.requestSubmit();
            }else{
              form.submit();
            }
          }else{
            const btn = form.querySelector('button[type="submit"]');
            if(btn){
              btn.disabled = false;
            }
          }
        }
      });
      if(input.checked){
        card.classList.add('selected');
        const form = input.closest('form');
        if(form && !autoSubmit){
          const btn = form.querySelector('button[type="submit"]');
          if(btn){
            btn.disabled = false;
          }
        }
      }
    });
  });
});