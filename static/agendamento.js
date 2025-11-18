document.addEventListener('DOMContentLoaded',()=>{
  const inp = document.getElementById('client_name');
  if(inp){
    const saved = localStorage.getItem('client_name');
    if(saved) inp.value = saved;
    inp.addEventListener('input',()=>localStorage.setItem('client_name',inp.value));
  }
  document.querySelectorAll('.options').forEach(container=>{
    const cards = container.querySelectorAll('label.option-card');
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
      });
      if(input.checked){
        card.classList.add('selected');
      }
    });
  });
});