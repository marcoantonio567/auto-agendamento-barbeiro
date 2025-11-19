document.addEventListener('DOMContentLoaded',()=>{
  const form = document.querySelector('form.filters');
  if(form){
    form.querySelectorAll('select,input[type="date"],input[type="time"]').forEach(el=>{
      el.addEventListener('change',()=>{
        if(typeof form.requestSubmit === 'function'){
          form.requestSubmit();
        }else{
          form.submit();
        }
      });
    });
    const clear = form.querySelector('.clear-filters');
    if(clear){
      clear.addEventListener('click',e=>{
        e.preventDefault();
        const url = clear.getAttribute('href');
        if(url){
          window.location.href = url;
        }else{
          form.querySelectorAll('select,input[type="date"],input[type="time"]').forEach(el=>{
            if(el.tagName === 'SELECT'){
              el.selectedIndex = 0;
            }else{
              el.value = '';
            }
          });
          if(typeof form.requestSubmit === 'function'){
            form.requestSubmit();
          }else{
            form.submit();
          }
        }
      });
    }
  }
});