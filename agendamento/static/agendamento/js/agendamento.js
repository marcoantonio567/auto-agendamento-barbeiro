document.addEventListener('DOMContentLoaded',()=>{
  if (window.lucide && typeof window.lucide.createIcons === 'function') {
    window.lucide.createIcons();
  }
  const inp = document.getElementById('client_name');
  const phoneInp = document.getElementById('client_phone');
  const cb = document.getElementById('save_name_checkbox');
  const formatBrPhone = (value)=>{
    const digits = (value||'').replace(/\D/g,'').slice(0,11);
    const a = digits.slice(0,2);
    const b = digits.slice(2,3);
    const c = digits.slice(3,7);
    const d = digits.slice(7,11);
    if(!a) return '';
    if(digits.length < 2) return `(${a}`;
    let out = `(${a}) `;
    if(b) out += `${b} `;
    if(c) out += c;
    if(d) out += `-${d}`;
    return out;
  };
  if(inp){
    const opt = localStorage.getItem('client_name_opt_in') === '1';
    if(cb){ cb.checked = opt; }
    if(opt){
      const saved = localStorage.getItem('client_name');
      if(saved) inp.value = saved;
      const savedPhone = localStorage.getItem('client_phone');
      if(phoneInp && savedPhone) phoneInp.value = savedPhone;
    }
    inp.addEventListener('input',()=>{
      if(cb && cb.checked){
        localStorage.setItem('client_name', inp.value);
      }
    });
  }
  if(phoneInp){
    const applyMask = ()=>{
      const masked = formatBrPhone(phoneInp.value);
      phoneInp.value = masked;
      if(cb && cb.checked){
        localStorage.setItem('client_phone', masked);
      }
    };
    const savedPhoneRaw = localStorage.getItem('client_phone');
    if(cb && cb.checked && savedPhoneRaw){
      phoneInp.value = formatBrPhone(savedPhoneRaw);
    }
    phoneInp.addEventListener('input', applyMask);
    phoneInp.addEventListener('blur', applyMask);
  }
  if(cb){
    cb.addEventListener('change',()=>{
      if(cb.checked){
        localStorage.setItem('client_name_opt_in','1');
        const val = (inp && inp.value) ? inp.value : '';
        localStorage.setItem('client_name', val);
        const phoneVal = (phoneInp && phoneInp.value) ? phoneInp.value : '';
        localStorage.setItem('client_phone', phoneVal);
      }else{
        localStorage.removeItem('client_name_opt_in');
        localStorage.removeItem('client_name');
        localStorage.removeItem('client_phone');
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
  const toggleBtn = document.getElementById('toggle-password');
  const pwdInput = document.getElementById('password');
  if(toggleBtn && pwdInput){
    const swap = toggleBtn.querySelector('.icon-swap');
    toggleBtn.addEventListener('click',()=>{
      const visible = pwdInput.type === 'text';
      pwdInput.type = visible ? 'password' : 'text';
      if(swap){
        swap.setAttribute('data-visible', visible ? 'false' : 'true');
      }
    });
  }
  const adminUserInput = document.getElementById('username');
  const saveCredsCb = document.getElementById('save_creds_checkbox');
  if(adminUserInput){
    const opt = localStorage.getItem('admin_username_opt_in') === '1';
    if(saveCredsCb){ saveCredsCb.checked = opt; }
    if(opt){
      const saved = localStorage.getItem('admin_username');
      if(saved) adminUserInput.value = saved;
    }
    adminUserInput.addEventListener('input',()=>{
      if(saveCredsCb && saveCredsCb.checked){
        localStorage.setItem('admin_username', adminUserInput.value);
      }
    });
  }
  if(saveCredsCb){
    saveCredsCb.addEventListener('change',()=>{
      if(saveCredsCb.checked){
        localStorage.setItem('admin_username_opt_in','1');
        const val = (adminUserInput && adminUserInput.value) ? adminUserInput.value : '';
        localStorage.setItem('admin_username', val);
      }else{
        localStorage.removeItem('admin_username_opt_in');
        localStorage.removeItem('admin_username');
      }
    });
  }
});
