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
  const modal = document.getElementById('confirmModal');
  const modalMsg = document.getElementById('modalMessage');
  const modalCancel = document.getElementById('modalCancel');
  const modalConfirm = document.getElementById('modalConfirm');
  const shiftForm = document.getElementById('shiftForm');
  let pendingUrl = null;
  const openBtn = document.querySelector('.open-shift-modal');
  if(openBtn && modal){
    openBtn.addEventListener('click',()=>{
      modal.classList.add('show');
    });
  }
  document.querySelectorAll('.shift-option').forEach(opt=>{
    opt.addEventListener('click',()=>{
      pendingUrl = opt.getAttribute('data-url');
      const msg = opt.getAttribute('data-message')||'Confirmar mover?';
      if(modalMsg){ modalMsg.textContent = msg; }
      document.querySelectorAll('.shift-option').forEach(o=>o.classList.remove('selected'));
      opt.classList.add('selected');
      if(modalConfirm){ modalConfirm.disabled = false; }
    });
  });
  const hideModal = ()=>{
    if(modal){ modal.classList.remove('show'); }
    pendingUrl = null;
  };
  if(modalCancel){ modalCancel.addEventListener('click', hideModal); }
  const backdrop = modal ? modal.querySelector('.modal-backdrop') : null;
  if(backdrop){ backdrop.addEventListener('click', hideModal); }
  if(modalConfirm){
    modalConfirm.addEventListener('click',()=>{
      if(shiftForm && pendingUrl){
        shiftForm.setAttribute('action', pendingUrl);
        if(typeof shiftForm.requestSubmit === 'function'){
          shiftForm.requestSubmit();
        }else{
          shiftForm.submit();
        }
        hideModal();
      }else{
        hideModal();
      }
    });
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
