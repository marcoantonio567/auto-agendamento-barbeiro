document.addEventListener('DOMContentLoaded',()=>{
  // salvar nome no localStorage na última etapa
  const inp = document.getElementById('client_name');
  if(inp){
    const saved = localStorage.getItem('client_name');
    if(saved) inp.value = saved;
    inp.addEventListener('input',()=>localStorage.setItem('client_name',inp.value));
  }
});