document.addEventListener('DOMContentLoaded',()=>{
  const inp = document.getElementById('client_name');
  const cb = document.getElementById('save_name_checkbox');
  if(inp){
    const opt = localStorage.getItem('client_name_opt_in') === '1';
    if(cb){ cb.checked = opt; }
    if(opt){
      const saved = localStorage.getItem('client_name');
      if(saved) inp.value = saved;
    }
    inp.addEventListener('input',()=>{
      if(cb && cb.checked){
        localStorage.setItem('client_name', inp.value);
      }
    });
  }
  if(cb){
    cb.addEventListener('change',()=>{
      if(cb.checked){
        localStorage.setItem('client_name_opt_in','1');
        const val = (inp && inp.value) ? inp.value : '';
        localStorage.setItem('client_name', val);
      }else{
        localStorage.removeItem('client_name_opt_in');
        localStorage.removeItem('client_name');
      }
    });
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