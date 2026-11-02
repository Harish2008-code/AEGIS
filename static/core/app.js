document.querySelectorAll('form[data-loading]').forEach(form=>form.addEventListener('submit',()=>{const button=form.querySelector('button');button.disabled=true;button.innerText=form.dataset.loading;button.classList.add('loading')}));

const expiryConfig=document.getElementById('expiry-document-kinds');
if(expiryConfig){
 const allowed=JSON.parse(expiryConfig.textContent), select=document.querySelector('select[name="kind"]'), label=document.getElementById('expiry-upload-field'), input=label.querySelector('input');
 const updateExpiry=()=>{const applicable=allowed.includes(select.value);label.hidden=!applicable;input.disabled=!applicable;if(!applicable)input.value='';};
 select.addEventListener('change',updateExpiry);updateExpiry();
}
