/* Progressive enhancement: annotate existing UI; retain all Pterodactyl handlers. */
(()=>{'use strict';
let queued=false;const inspected=new WeakSet();
let settings={};try{settings=JSON.parse(document.querySelector('meta[name="comic-theme-config"]')?.content||'{}');}catch{}
const currentUser=(document.querySelector('meta[name="comic-user"]')?.content||'').trim();
const userText=value=>String(value??'').replace(/\{user\}/gi,currentUser||'User');
function applyPanelBackground(){
 const cfg=settings.background||{},image=String(cfg.image||'');
 const valid=/^\/comic-theme\/uploads\/background-[0-9a-f]{16}\.(?:jpg|png|webp|gif)$/i.test(image);
 if(!valid){
  if(document.body.classList.contains('comic-has-background')){
   document.body.classList.remove('comic-has-background');delete document.body.dataset.comicBackground;
   ['background-image','background-size','background-position','background-repeat','background-attachment'].forEach(k=>document.body.style.removeProperty(k));
  }
  return;
 }
 const overlay=Math.min(90,Math.max(0,parseInt(cfg.overlay,10)||0))/100,key=image+'|'+overlay;
 if(document.body.dataset.comicBackground===key)return;
 const escaped=image.replace(/["\\]/g,'\\$&');
 document.body.dataset.comicBackground=key;document.body.classList.add('comic-has-background');
 document.body.style.setProperty('background-image',`linear-gradient(rgba(8,11,16,${overlay}),rgba(8,11,16,${overlay})),url("${escaped}")`,'important');
 document.body.style.setProperty('background-size','cover','important');
 document.body.style.setProperty('background-position','center center','important');
 document.body.style.setProperty('background-repeat','no-repeat','important');
 document.body.style.setProperty('background-attachment','fixed','important');
}
function serviceLinks(body){
 const links=(Array.isArray(settings.links)?settings.links:[]).filter(l=>l.enabled&&safeUrl(l.url));
 if(!links.length)return;
 const hr=document.createElement('hr');hr.className='comic-drawer-sep';body.append(hr);
 const h=document.createElement('div');h.className='comic-drawer-title';h.textContent=settings.heading||'Layanan & Bantuan';body.append(h);
 links.forEach(l=>{const a=document.createElement('a');a.className='comic-drawer-item comic-link-'+(['green','yellow','dark'].includes(l.tone)?l.tone:'dark');a.href=l.url;a.target='_blank';a.rel='noopener noreferrer';const t=document.createElement('span');t.textContent=l.label;a.append(t);const arrow=document.createElement('span');arrow.textContent='↗';arrow.className='comic-link-arrow';a.append(arrow);body.append(a);});
}
function safeUrl(value){try{const u=new URL(value);return ['http:','https:'].includes(u.protocol)&&!u.username&&!u.password;}catch{return false;}}
function updateBrand(el){if(el&&settings.brand&&el.textContent!==settings.brand){el.textContent=settings.brand;el.title=settings.brand;}}
function adminEnhance(){
 if(!document.querySelector('.main-sidebar'))return;
 document.body.classList.add('comic-admin');
 const header=document.querySelector('.main-header');if(header&&!header.dataset.comicResize){header.dataset.comicResize='true';const resize=()=>document.body.style.setProperty('--comic-admin-header-height',header.offsetHeight+'px');resize();if(typeof ResizeObserver!=='undefined')new ResizeObserver(resize).observe(header);}
 const toggle=document.querySelector('.main-header .sidebar-toggle');
 if(toggle&&!toggle.dataset.comicMenu){toggle.dataset.comicMenu='true';toggle.setAttribute('aria-label','Buka menu admin');toggle.setAttribute('aria-expanded','false');toggle.innerHTML='<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>';toggle.addEventListener('click',()=>requestAnimationFrame(()=>toggle.setAttribute('aria-expanded',String(document.body.classList.contains('sidebar-open')))));
  const backdrop=document.createElement('div');backdrop.className='comic-admin-backdrop';backdrop.setAttribute('aria-hidden','true');const close=()=>{document.body.classList.remove('sidebar-open');toggle.setAttribute('aria-expanded','false');toggle.focus({preventScroll:true});};backdrop.addEventListener('click',close);document.body.append(backdrop);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('sidebar-open'))close();});
 }
 updateBrand(document.querySelector('.main-header .logo span'));
 const menu=document.querySelector('.sidebar-menu');
 if(menu&&!menu.querySelector('[data-comic-back]')){
  const mkItem=(href,icon,text,cls)=>{const li=document.createElement('li');li.dataset.comicBack='true';li.className='comic-admin-back '+cls;const a=document.createElement('a');a.href=href;const i=document.createElement('i');i.className='fa '+icon;i.setAttribute('aria-hidden','true');const sp=document.createElement('span');sp.textContent=text;a.append(i,sp);li.append(a);return li;};
  const back=mkItem('/','fa-arrow-left','Kembali ke Panel','');
  menu.prepend(back);
 }
 if(menu&&!menu.querySelector('[data-comic-settings]')){
  const li=document.createElement('li');li.dataset.comicSettings='true';li.classList.toggle('active',location.pathname==='/admin/settings/comic-links');
  const a=document.createElement('a');a.href='/admin/settings/comic-links';a.innerHTML='<i class="fa fa-link" aria-hidden="true"></i><span>Tampilan &amp; Link</span>';li.append(a);
  const original=menu.querySelector('a[href$="/admin/settings"]')?.closest('li');if(original)original.after(li);else menu.append(li);
 }
 const secOwner=document.querySelector('meta[name="comic-security-owner"]')?.content==='1';
 if(menu&&secOwner&&!menu.querySelector('[data-comic-security]')){
  const li=document.createElement('li');li.dataset.comicSecurity='true';li.classList.toggle('active',location.pathname==='/admin/settings/comic-security');
  const a=document.createElement('a');a.href='/admin/settings/comic-security';a.innerHTML='<i class="fa fa-shield" aria-hidden="true"></i><span>Setting Admin</span>';li.append(a);
  const after=menu.querySelector('[data-comic-settings]')||menu.querySelector('a[href$="/admin/settings"]')?.closest('li');if(after)after.after(li);else menu.append(li);
 }
 if(menu&&secOwner&&!menu.querySelector('[data-comic-egg-changer]')){
  const li=document.createElement('li');li.dataset.comicEggChanger='true';li.classList.toggle('active',location.pathname==='/admin/settings/egg-changer');
  const a=document.createElement('a');a.href='/admin/settings/egg-changer';a.innerHTML='<i class="fa fa-exchange" aria-hidden="true"></i><span>Eggs Changer</span>';li.append(a);
  const after=menu.querySelector('[data-comic-security]')||menu.querySelector('[data-comic-settings]')||menu.querySelector('a[href$="/admin/settings"]')?.closest('li');if(after)after.after(li);else menu.append(li);
 }
 if(menu&&!menu.querySelector('[data-comic-account-links]')){
  const originalLinks=[...document.querySelectorAll('.navbar-custom-menu a[href]')];
  if(originalLinks.length){const heading=document.createElement('li');heading.dataset.comicAccountLinks='true';heading.className='header comic-admin-mobile-account';heading.textContent='ACCOUNT';menu.append(heading);
   originalLinks.forEach(original=>{const li=document.createElement('li');li.className='comic-admin-mobile-account';const a=document.createElement('a');a.href=original.href;const label=original.id==='logoutButton'?'Logout':original.closest('.user-menu')?'Account':'Kembali ke Panel';a.textContent=label;a.addEventListener('click',e=>{e.preventDefault();original.click();});li.append(a);menu.append(li);});
  }
 }
 if(location.pathname.startsWith('/admin/settings')){
  const tabs=document.querySelector('.nav-tabs');
  if(tabs&&!tabs.querySelector('[data-comic-settings-tab]')){const li=document.createElement('li');li.dataset.comicSettingsTab='true';li.innerHTML='<a href="/admin/settings/comic-links">Tampilan &amp; Link</a>';tabs.append(li);}
  if(tabs&&secOwner&&!tabs.querySelector('[data-comic-security-tab]')){const li=document.createElement('li');li.dataset.comicSecurityTab='true';li.innerHTML='<a href="/admin/settings/comic-security">Setting Admin</a>';tabs.append(li);}
  if(tabs&&secOwner&&!tabs.querySelector('[data-comic-egg-tab]')){const li=document.createElement('li');li.dataset.comicEggTab='true';li.innerHTML='<a href="/admin/settings/egg-changer">Eggs Changer</a>';tabs.append(li);}
 }
 const nav=document.querySelector('.main-header .navbar');
 if(nav&&!nav.querySelector('.comic-admin-search')){const b=document.createElement('button');b.type='button';b.className='comic-admin-search';b.innerHTML=svgI('search');b.setAttribute('aria-label','Cari menu admin');b.addEventListener('click',adminSearch);nav.append(b);}
 if(nav&&!nav.querySelector('.comic-admin-home')){const h=document.createElement('a');h.href='/';h.className='comic-admin-home';h.title='Kembali ke Panel';h.setAttribute('aria-label','Kembali ke Panel');h.innerHTML=svgI('home');nav.append(h);}
}
function loginEnhance(){
 if(document.getElementById('logo'))return;
 const input=document.querySelector('form input');if(!input)return;
 let el=input.parentElement,card=null;
 while(el&&el!==document.body){const c=getComputedStyle(el).backgroundColor;if(el.classList.contains('comic-login-card')||c==='rgb(255, 255, 255)'){card=el;break;}el=el.parentElement;}
 if(card&&!card.classList.contains('comic-login-card')){card.classList.add('comic-login-card');document.body.classList.add('comic-login');
  [...card.querySelectorAll('label,input,button,a,img')].forEach((n,i)=>n.style.setProperty('--ci',i));}
}
function restrictMenu(){
 if(document.querySelector('meta[name="comic-admin-restrict"]')?.content!=='1')return;
 const menu=document.querySelector('.sidebar-menu');if(!menu)return;
 const keep=/^\/admin\/servers\/?$/;
 const own=li=>li.dataset.comicBack||li.dataset.comicAccountLinks||li.classList.contains('comic-admin-back')||li.classList.contains('comic-admin-mobile-account');
 [...menu.children].forEach(li=>{
  if(own(li))return;
  const a=li.querySelector(':scope > a[href]');
  let ok=false;
  if(a){try{ok=keep.test(new URL(a.href,location.origin).pathname);}catch(e){}}
  li.hidden=!ok;li.style.display=ok?'':'none';
 });
 document.querySelectorAll('[data-comic-settings-tab]').forEach(n=>n.remove());
}
function adminSearch(){
 const d=document.createElement('dialog');d.className='comic-notify-dialog';d.setAttribute('aria-label','Cari menu admin');
 const h=document.createElement('h2');h.textContent='Cari Menu Admin';const input=document.createElement('input');input.placeholder='Settings, Users, Nodes…';input.setAttribute('aria-label','Nama menu');
 const results=document.createElement('div');results.className='comic-search-results';const close=document.createElement('button');close.textContent='Tutup';close.onclick=()=>d.close();
 const links=[...document.querySelectorAll('.sidebar-menu a[href]')].filter(a=>a.getAttribute('href')!=='#'&&!a.closest('li[hidden]'));
 const render=()=>{results.textContent='';links.filter(a=>a.textContent.toLowerCase().includes(input.value.toLowerCase())).forEach(a=>{const row=document.createElement('a');row.href=a.href;row.textContent=a.textContent.trim();results.append(row);});if(!results.children.length)results.textContent='Menu tidak ditemukan.';};
 input.addEventListener('input',render);d.append(h,input,results,close);d.onclose=()=>d.remove();document.body.append(d);render();d.showModal();input.focus();
}


// ---- User Egg Changer: admin ID 1 memilih Nest, user pemilik server memilih Egg di Nest yang sama ----
const clientEggState=new Map();
function clientEggMessage(data,fallback){
 if(data&&typeof data.message==='string'&&data.message.trim())return data.message;
 if(data&&data.errors&&typeof data.errors==='object'){const first=Object.values(data.errors).flat().find(Boolean);if(first)return String(first);}
 return fallback;
}
function clientServerTabParent(identifier){
 const prefix='/server/'+identifier;
 const known=new Set(['console','files','databases','schedules','users','backups','network','startup','settings','activity','mods','plugins','subdomain','subdomains','versions','reinstall','changer eggs']);
 let best=null,bestCount=0;
 document.querySelectorAll('#app a[href]').forEach(a=>{
  if(!a.pathname.startsWith(prefix)||!known.has(a.textContent.trim().toLowerCase()))return;
  const p=a.parentElement;if(!p)return;
  const count=[...p.children].filter(x=>x.tagName==='A'&&x.pathname&&x.pathname.startsWith(prefix)&&known.has(x.textContent.trim().toLowerCase())).length;
  if(count>bestCount){best=p;bestCount=count;}
 });
 return bestCount>=2?best:null;
}
function showClientEggModal(identifier,data){
 document.querySelector('.comic-egg-modal')?.remove();
 const modal=document.createElement('div');modal.className='comic-egg-modal';modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');modal.setAttribute('aria-label','Changer Eggs');
 const card=document.createElement('div');card.className='comic-egg-card';
 const head=document.createElement('div');head.className='comic-egg-head';
 const title=document.createElement('div');title.innerHTML='<strong>CHANGER EGGS</strong><span></span>';title.querySelector('span').textContent=(data.server?.name||'Server')+' • Nest #'+(data.nest?.id??'-')+' '+(data.nest?.name||'');
 const close=document.createElement('button');close.type='button';close.className='comic-egg-close';close.textContent='×';close.setAttribute('aria-label','Tutup');
 head.append(title,close);
 const info=document.createElement('p');info.className='comic-egg-info';info.textContent='Pilih Egg dari Nest server ini. File server tidak dihapus dan tidak otomatis reinstall. Sebaiknya stop server sebelum mengganti Egg.';
 const label=document.createElement('label');label.textContent='Pilih Egg';
 const select=document.createElement('select');select.className='comic-egg-select';
 (Array.isArray(data.eggs)?data.eggs:[]).forEach(e=>{const o=document.createElement('option');o.value=String(e.id);o.textContent=e.name+(Number(e.id)===Number(data.current_egg_id)?' — Saat ini':'');o.selected=Number(e.id)===Number(data.current_egg_id);select.append(o);});
 const desc=document.createElement('div');desc.className='comic-egg-desc';
 const setDesc=()=>{const e=(data.eggs||[]).find(x=>String(x.id)===String(select.value));desc.textContent=e?.description||'Egg #'+(select.value||'-');};select.addEventListener('change',setDesc);setDesc();
 const status=document.createElement('div');status.className='comic-egg-status';status.setAttribute('aria-live','polite');
 const actions=document.createElement('div');actions.className='comic-egg-actions';
 const cancel=document.createElement('button');cancel.type='button';cancel.className='comic-egg-cancel';cancel.textContent='Batal';
 const save=document.createElement('button');save.type='button';save.className='comic-egg-save';save.textContent='Save / Ganti Egg';
 actions.append(cancel,save);card.append(head,info,label,select,desc,status,actions);modal.append(card);document.body.append(modal);
 const dismiss=()=>{modal.remove();document.body.classList.remove('comic-egg-open');};close.onclick=dismiss;cancel.onclick=dismiss;modal.addEventListener('click',e=>{if(e.target===modal)dismiss();});
 document.body.classList.add('comic-egg-open');select.focus({preventScroll:true});
 save.addEventListener('click',async()=>{
  if(!select.value||save.disabled)return;
  save.disabled=true;select.disabled=true;status.className='comic-egg-status';status.textContent='Menyimpan perubahan…';
  try{
   const csrf=document.querySelector('meta[name="comic-csrf"]')?.content||document.querySelector('meta[name="csrf-token"]')?.content||'';
   const r=await fetch('/comic-theme/client/servers/'+encodeURIComponent(identifier)+'/egg-changer',{method:'POST',credentials:'same-origin',headers:{'Accept':'application/json','Content-Type':'application/json','X-CSRF-TOKEN':csrf,'X-Requested-With':'XMLHttpRequest'},body:JSON.stringify({egg_id:Number(select.value)})});
   let payload={};try{payload=await r.json();}catch{}
   if(!r.ok)throw new Error(clientEggMessage(payload,'Gagal mengganti Egg (HTTP '+r.status+').'));
   status.className='comic-egg-status success';status.textContent=payload.warning?payload.message+' '+payload.warning:(payload.message||'Egg berhasil diganti.');
   const cached=clientEggState.get(identifier);if(cached?.data)cached.data.current_egg_id=Number(select.value);
   setTimeout(()=>location.reload(),payload.warning?2200:900);
  }catch(err){status.className='comic-egg-status error';status.textContent=err?.message||'Gagal mengganti Egg.';save.disabled=false;select.disabled=false;}
 });
}
function mountClientEggTab(identifier,data){
 const parent=clientServerTabParent(identifier);if(!parent)return;
 if(parent.querySelector('[data-comic-client-egg]'))return;
 const sample=[...parent.children].find(a=>a.tagName==='A'&&a.pathname&&a.pathname.startsWith('/server/'+identifier));
 if(!sample)return;
 const a=document.createElement('a');a.dataset.comicClientEgg='true';a.className=sample.className;a.href=location.pathname+location.search+'#comic-egg-changer';a.textContent='Changer Eggs';a.setAttribute('role','button');
 a.addEventListener('click',e=>{e.preventDefault();showClientEggModal(identifier,data);});parent.append(a);
}
function setupClientEggChanger(){
 const m=location.pathname.match(/^\/server\/([^/]+)/);if(!m)return;
 const identifier=m[1];let state=clientEggState.get(identifier);
 if(state?.data){if(state.data.enabled)mountClientEggTab(identifier,state.data);return;}
 if(state?.loading)return;
 state={loading:true,data:null};clientEggState.set(identifier,state);
 fetch('/comic-theme/client/servers/'+encodeURIComponent(identifier)+'/egg-changer',{credentials:'same-origin',headers:{'Accept':'application/json','X-Requested-With':'XMLHttpRequest'}})
  .then(async r=>{let d={};try{d=await r.json();}catch{}if(!r.ok)throw new Error('HTTP '+r.status);return d;})
  .then(d=>{state.loading=false;state.data=d;if(d.enabled)mountClientEggTab(identifier,d);})
  .catch(()=>{state.loading=false;state.data={enabled:false};});
}


function updatePageClass(){
 [...document.body.classList].forEach(c=>{if(c.startsWith('comic-page-'))document.body.classList.remove(c);});
 let page='dashboard';
 if(location.pathname==='/')page='dashboard';
 else if(/^\/server\/[^/]+\/?$/.test(location.pathname))page='console';
 else {
  const m=location.pathname.match(/^\/server\/[^/]+\/([^/?#]+)/);
  if(m&&m[1])page=m[1].toLowerCase().replace(/[^a-z0-9]+/g,'-');
  else if(location.pathname.startsWith('/account'))page='account';
  else if(location.pathname.startsWith('/admin'))page='admin';
  else page=(location.pathname.split('/').filter(Boolean).pop()||'page').toLowerCase().replace(/[^a-z0-9]+/g,'-');
 }
 document.body.classList.add('comic-page-'+page);
}
function enhanceConsoleLayout(){
 document.querySelectorAll('#app input, #app textarea').forEach(el=>{
  const ph=((el.getAttribute('placeholder')||'')+' '+(el.getAttribute('aria-label')||'')).toLowerCase();
  if(/type a command|command/.test(ph))el.classList.add('comic-command-input');
 });
 const terms=[...document.querySelectorAll('.xterm')];
 terms.forEach(term=>{
  let wrap=term;
  for(let i=0;i<6&&wrap&&wrap!==document.body;i++,wrap=wrap.parentElement){
   if(wrap.querySelector('.xterm')&&wrap.querySelector('.xterm-viewport')){wrap.classList.add('comic-console-card');break;}
  }
 });
 document.querySelectorAll('#app div,#app section').forEach(el=>{
  const kids=[...el.children].filter(n=>/^(BUTTON|A)$/.test(n.tagName));
  if(kids.length<2||kids.length>5)return;
  const texts=kids.map(n=>n.textContent.trim().toLowerCase());
  if(texts.some(t=>/^start(\s|$)/.test(t))&&texts.some(t=>/^restart(\s|$)/.test(t))){
   el.classList.add('comic-console-actions');
   kids.forEach(btn=>{
    const t=btn.textContent.trim().toLowerCase();
    if(/^start(\s|$)/.test(t))btn.classList.add('comic-console-btn-start');
    else if(/^restart(\s|$)/.test(t))btn.classList.add('comic-console-btn-restart');
    else if(/^(stop|kill)(\s|$)/.test(t))btn.classList.add('comic-console-btn-stop');
   });
  }
 });
 if(/^\/server\/[^/]+/.test(location.pathname)&&!document.querySelector('.comic-quick-menu')){
  const btn=document.createElement('button');btn.type='button';btn.className='comic-quick-menu';
  btn.setAttribute('aria-label','Menu cepat');
  btn.innerHTML=svgI('dashboard',18)+'<span>MENU</span>';
  btn.addEventListener('click',openDrawer);
  document.body.append(btn);
 }
}
const neutrals=new Set(['rgb(63, 77, 90)','rgb(51, 64, 76)','rgb(81, 95, 108)','rgb(31, 41, 51)']);
function annotate(){
 queued=false;document.body.classList.add('comic-ptero');updatePageClass();applyPanelBackground();adminEnhance();loginEnhance();restrictMenu();
 const logo=document.getElementById('logo');
 if(logo){const row=logo.parentElement;row?.classList.add('comic-header-row');const head=row?.parentElement;head?.classList.add('comic-header');
   setupDrawer(logo);updateBrand(logo.querySelector('a'));hero();notice();gate();
   const search=logo.nextElementSibling?.querySelector('.navigation-link');if(search){search.classList.add('comic-native-search');search.setAttribute('role','button');search.setAttribute('aria-label','Cari server');search.tabIndex=0;if(!search.dataset.comicKeys){search.dataset.comicKeys='true';search.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();search.click();}});}}


 }

 // Production CSS modules intentionally omit readable local names. Use stable DOM semantics.
 document.querySelectorAll('svg[data-icon="folder"],svg[data-icon="file-alt"],svg[data-icon="file-archive"],svg[data-icon="file-import"]').forEach(svg=>{
   let row=svg.parentElement;
   for(let i=0;row&&i<5;i++,row=row.parentElement){
     if(row.tagName==='DIV'&&row.querySelector('input[type="checkbox"]')&&row.querySelectorAll('svg[data-icon="folder"],svg[data-icon="file-alt"],svg[data-icon="file-archive"],svg[data-icon="file-import"]').length===1){row.classList.add('comic-file');break;}
   }
 });
 // Server tabs: find the native tab bar even when plugins/admin add extra links.
 const tabLabels=new Set(['console','files','databases','schedules','users','backups','network','startup','settings','activity','mods','plugins','subdomain','subdomains','versions','reinstall','changer eggs']);
 const parents=new Set();
 document.querySelectorAll('#app a[href]').forEach(a=>{
  if(a.querySelector('.status-bar')){
   a.classList.add('comic-server-card');const info=a.firstElementChild;info?.classList.add('comic-server-info');
   const name=info?.querySelector('p');name?.classList.add('comic-server-title');
  }else if(/^\/server\/[^/]+/.test(a.pathname)&&tabLabels.has(a.textContent.trim().toLowerCase()))parents.add(a.parentElement);
 });
 const accSet=new Set(['/account','/account/api','/account/ssh','/account/activity']);const accParents=new Set();
 document.querySelectorAll('#app a[href]').forEach(a=>{if(accSet.has(a.pathname.replace(/\/$/,'')||'/')&&!a.closest('.comic-header'))accParents.add(a.parentElement);});
 accParents.forEach(par=>{if(!par)return;const n=[...par.children].filter(a=>a.tagName==='A'&&accSet.has(a.pathname.replace(/\/$/,'')||'/')).length;if(n>=2)(par.parentElement&&par.parentElement.id!=='app'?par.parentElement:par).classList.add('comic-subnav','comic-account-nav');});
 parents.forEach(parent=>{
  if(!parent)return;
  const tabs=[...parent.children].filter(a=>a.tagName==='A'&&/^\/server\/[^/]+/.test(a.pathname));
  const roots=new Set(tabs.map(a=>a.pathname.match(/^\/server\/[^/]+/)[0]));
  const known=tabs.filter(a=>tabLabels.has(a.textContent.trim().toLowerCase())).length;
  if(tabs.length>=3&&roots.size===1&&known>=3&&known>=tabs.length*0.5)(parent.parentElement&&parent.parentElement.id!=='app'?parent.parentElement:parent).classList.add('comic-subnav');
 });
 document.querySelectorAll('#app div,#app section,#app article').forEach(el=>{
   if(inspected.has(el))return;inspected.add(el);
   if(el.closest('.xterm,.ace_editor,.comic-header,.comic-subnav,.comic-file'))return;
   const cs=getComputedStyle(el);
   if(neutrals.has(cs.backgroundColor)&&parseFloat(cs.borderRadius)>0&&el.clientWidth>=120&&el.clientHeight>=45)el.classList.add('comic-card');
 });
 document.querySelectorAll('[class*="file_row"]').forEach(el=>el.classList.add('comic-file'));
 document.querySelectorAll('button').forEach(b=>{if(b.closest('.xterm'))return;const t=b.textContent.trim().toLowerCase();
   if(/^(delete|remove|kill|stop|hapus|hapus permanen)(\s|$)/.test(t))b.classList.add('comic-danger');
   else if(/^(start|upload|confirm|yes|ya|mulai)(\s|$)/.test(t))b.classList.add('comic-success');
   else if(/^(create|new file|save|restart|buat|simpan)(\s|$)/.test(t))b.classList.add('comic-primary');
   if(/^start(\s|$)/.test(t))b.classList.add('comic-console-btn-start');
   else if(/^restart(\s|$)/.test(t))b.classList.add('comic-console-btn-restart');
   else if(/^(stop|kill)(\s|$)/.test(t))b.classList.add('comic-console-btn-stop');
 });
 setupClientEggChanger();
 enhanceConsoleLayout();
}


// ---- Mobile three-dot menu + drawer (re-uses original links; clicks are forwarded so React handlers stay intact) ----
const I={console:'<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',files:'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',databases:'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',schedules:'<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/>',users:'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6M16 4.5a3.5 3.5 0 0 1 0 7M18 14.4c2.1.7 3.5 2.6 3.5 5.6"/>',backups:'<rect x="3" y="3" width="18" height="7" rx="2"/><rect x="3" y="14" width="18" height="7" rx="2"/><path d="M7 6.5h.01M7 17.5h.01"/>',network:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',startup:'<path d="M5 15c-1.5 1.2-2 4-2 6 2 0 4.8-.5 6-2M14 4c3-1.5 6-1.5 6-1.5s0 3-1.5 6l-6 6-4-4zM9 13l-3-.5 2-3.5 3 .5M11 15l.5 3 3.5-2-.5-3"/>',settings:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/>',activity:'<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8zM14 3v5h5M9 13h6M9 17h6"/>',home:'<path d="M3 11l9-8 9 8M5 10v10h5v-6h4v6h5V10"/>',search:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',dashboard:'<path d="M12 2 2 7l10 5 10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>',account:'<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',admin:'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',logout:'<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',server:'<rect x="3" y="3" width="18" height="7" rx="2"/><rect x="3" y="14" width="18" height="7" rx="2"/><path d="M7 6.5h.01M7 17.5h.01"/>',close:'<path d="M6 6l12 12M18 6 6 18"/>'};
Object.assign(I,{egg:'<ellipse cx="12" cy="12" rx="7" ry="9"/><path d="M9 9c2-1 4-1 6 0M8.5 14c2.3 1.3 4.7 1.3 7 0"/>',key:'<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3M14 9l2 2"/>',ssh:'<rect x="3" y="4" width="18" height="16" rx="2"/><polyline points="7 10 10 12 7 14"/><line x1="12" y1="15" x2="17" y2="15"/>'});
const svgI=(k,s=22)=>`<svg viewBox="0 0 24 24" width="${s}" height="${s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${I[k]||''}</svg>`;
const dots='<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2.2"/><circle cx="12" cy="12" r="2.2"/><circle cx="12" cy="19" r="2.2"/></svg>';
let moreBtn=null;
function closeDrawer(){document.body.classList.remove('comic-drawer-open');const d=document.querySelector('.comic-drawer');if(d)d.setAttribute('aria-hidden','true');moreBtn?.setAttribute('aria-expanded','false');document.getElementById('app')?.removeAttribute('inert');moreBtn?.focus({preventScroll:true});}
function item(key,label,orig,active,danger){
 const b=document.createElement('button');b.type='button';b.className='comic-drawer-item'+(active?' active':'')+(danger?' danger':'');
 b.dataset.k=key;b.innerHTML=svgI(key);const t=document.createElement('span');t.textContent=label;b.append(t);
 b.addEventListener('click',()=>{closeDrawer();orig.click();});return b;
}
function appendEggDrawerItem(body,identifier,data){
 if(!body||!identifier||!data?.enabled||body.querySelector('[data-k=\"egg\"]'))return;
 const proxy=document.createElement('button');proxy.type='button';proxy.addEventListener('click',()=>showClientEggModal(identifier,data));
 const eggItem=item('egg','Changer Eggs',proxy,false,false);eggItem.dataset.comicEggDrawer='true';
 const settingsItem=[...body.querySelectorAll('.comic-drawer-item')].find(el=>el.querySelector('span')?.textContent?.trim().toLowerCase()==='settings');
 if(settingsItem)body.insertBefore(eggItem,settingsItem);else body.append(eggItem);
 body.querySelectorAll('.comic-drawer-item').forEach((el,i)=>el.style.setProperty('--i',i));
}
function refreshEggDrawer(body){
 const m=location.pathname.match(/^\/server\/([^/]+)/);if(!m||!body)return;
 const identifier=m[1],state=clientEggState.get(identifier);
 if(state?.data){appendEggDrawerItem(body,identifier,state.data);return;}
 if(state?.loading)return;
 const next={loading:true,data:null};clientEggState.set(identifier,next);
 fetch('/comic-theme/client/servers/'+encodeURIComponent(identifier)+'/egg-changer',{credentials:'same-origin',headers:{'Accept':'application/json','X-Requested-With':'XMLHttpRequest'}})
  .then(async r=>{let d={};try{d=await r.json();}catch{}if(!r.ok)throw new Error('HTTP '+r.status);return d;})
  .then(data=>{next.loading=false;next.data=data;if(data.enabled){mountClientEggTab(identifier,data);if(document.body.classList.contains('comic-drawer-open'))appendEggDrawerItem(body,identifier,data);}})
  .catch(()=>{next.loading=false;next.data={enabled:false};});
}
function openDrawer(){
 const d=document.querySelector('.comic-drawer');if(!d)return;
 const body=d.querySelector('.comic-drawer-body');body.textContent='';
 const sub=document.querySelector('.comic-subnav');
 const links=sub?[...sub.querySelectorAll('a[href]')].filter(a=>(/^\/server\/[^/]+/.test(a.pathname)||/^\/admin\//.test(a.pathname)||/^\/account(\/|$)/.test(a.pathname))&&!/^\/account\/api\/?$/.test(a.pathname)):[];
 const isAcc=links.length>0&&links.every(a=>/^\/account(\/|$)/.test(a.pathname));
 d.querySelector('.comic-drawer-head span').textContent=isAcc?'Akun':(links.length?'Server Menu':'Menu');
 links.forEach(a=>{const isAdm=/^\/admin\//.test(a.pathname);let label=a.textContent.trim()||'Menu';let key=isAdm?'admin':label.toLowerCase();
   if(a.dataset.comicClientEgg)key='egg';else if(/^\/account\/ssh/.test(a.pathname))key='ssh';else if(/^\/account\/activity/.test(a.pathname))key='activity';else if(/^\/account\/?$/.test(a.pathname))key='account';
   body.append(item(I[key]?key:'server',label,a,a.classList.contains('active')||a.getAttribute('aria-current')==='page'||a.pathname===location.pathname));});
 refreshEggDrawer(body);
 const nav=document.getElementById('logo')?.nextElementSibling;
 if(nav){
   if(links.length){const hr=document.createElement('hr');hr.className='comic-drawer-sep';body.append(hr);}
   const h=document.createElement('div');h.className='comic-drawer-title';h.textContent='Account';body.append(h);
   const kids=[...nav.children];
   kids.forEach((el,i)=>{
     const href=el.getAttribute('href')||'';let key,label;
     if(el.tagName==='A'){if(/\/admin/.test(href)){key='admin';label='Admin';}else if(/\/account/.test(href)){key='account';label='Account';}else{key='dashboard';label='Dashboard';}}
     else if(i===kids.length-1){key='logout';label='Logout';}
     else{key='search';label='Search';}
     body.append(item(key,label,el,el.classList.contains('active')&&key==='dashboard'&&!links.length,key==='logout'));
   });
 }
 serviceLinks(body);body.querySelectorAll('.comic-drawer-item').forEach((el,i)=>el.style.setProperty('--i',i));document.getElementById('app')?.setAttribute('inert','');
 d.setAttribute('aria-hidden','false');document.body.classList.add('comic-drawer-open');moreBtn?.setAttribute('aria-expanded','true');
 d.querySelector('.comic-drawer-head button').focus({preventScroll:true});
}
function setupDrawer(logo){
 const row=logo.parentElement;
 if(row&&!row.querySelector('.comic-more')){
   moreBtn=document.createElement('button');moreBtn.type='button';moreBtn.className='comic-more';moreBtn.setAttribute('aria-label','Menu');moreBtn.setAttribute('aria-haspopup','dialog');moreBtn.setAttribute('aria-expanded','false');moreBtn.innerHTML='<svg class="comic-burger" viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2.3"/><circle cx="12" cy="12" r="2.3"/><circle cx="12" cy="19" r="2.3"/></svg>';moreBtn.setAttribute('aria-controls','comic-right-menu');
   moreBtn.addEventListener('click',openDrawer);row.append(moreBtn);
 } else if(row) moreBtn=row.querySelector('.comic-more');
 if(!document.querySelector('.comic-drawer')){
   const bd=document.createElement('div');bd.className='comic-drawer-backdrop';bd.addEventListener('click',closeDrawer);
   const d=document.createElement('nav');d.className='comic-drawer';d.id='comic-right-menu';d.setAttribute('role','dialog');d.setAttribute('aria-modal','true');d.setAttribute('aria-label','Menu');d.setAttribute('aria-hidden','true');
   d.innerHTML='<div class="comic-drawer-head">'+svgI('server',26)+'<span>Menu</span><button type="button" aria-label="Close menu">'+svgI('close',22)+'</button></div><div class="comic-drawer-body"></div>';
   d.querySelector('button').addEventListener('click',closeDrawer);
   document.body.append(bd,d);
   document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.body.classList.contains('comic-drawer-open'))closeDrawer();});
   d.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const els=[...d.querySelectorAll('button,a[href]')];const first=els[0],last=els[els.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
 }
}

// ---- Tap ripple (delegated, purely visual) ----
document.addEventListener('pointerdown',e=>{
 if(!document.body.classList.contains('comic-ptero'))return;
 const t=e.target.closest&&e.target.closest('button,.btn,.comic-drawer-item,.comic-server-card,.sidebar-menu a');
 if(!t||t.closest('.xterm,.ace_editor')||t.disabled||t.getAttribute('role')==='switch')return;
 if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 if(getComputedStyle(t).position==='static')t.style.position='relative';
 t.classList.add('comic-ripple-host');
 const r=t.getBoundingClientRect(),d=Math.max(r.width,r.height)*2;
 const s=document.createElement('span');s.className='comic-ripple';
 s.style.cssText='width:'+d+'px;height:'+d+'px;left:'+(e.clientX-r.left-d/2)+'px;top:'+(e.clientY-r.top-d/2)+'px';
 t.append(s);setTimeout(()=>s.remove(),650);
},{passive:true});

// ---- Banner WELCOME di Dashboard + gerbang join ----
const hex=v=>/^#[0-9a-fA-F]{6}$/.test(v||'');
const gateCfg=()=>settings.gate||{};
const gateKey=()=>'comic_joined_v'+(parseInt(gateCfg().version,10)||1);
function isJoined(){const k=gateKey();try{if(localStorage.getItem(k)==='1')return true;}catch{}return document.cookie.split('; ').includes(k+'=1');}
function markJoined(){const k=gateKey();try{localStorage.setItem(k,'1');}catch{}document.cookie=k+'=1; max-age=31536000; path=/; SameSite=Lax'+(location.protocol==='https:'?'; Secure':'');}
const mk=(t,c,txt)=>{const n=document.createElement(t);if(c)n.className=c;if(txt!=null)n.textContent=txt;return n;};
function applyColors(node,w){
 const set=(k,v,d)=>node.style.setProperty(k,hex(v)?v:d);
 set('--cw-title',w.title_color,'#ffffff');set('--cw-name',w.name_color,'#f7ca45');set('--cw-text',w.text_color,'#f6f7fb');set('--cw-accent',w.accent_color,'#f7ca45');
 node.style.setProperty('--cw-shade',String(Math.min(90,Math.max(0,parseInt(w.overlay,10)||0))/100));
}
function hero(){
 const w=settings.welcome||{};
 const old=document.querySelector('.comic-hero');
 const head=document.querySelector('.comic-header');
 if(!w.enabled||location.pathname!=='/'||!head){old?.remove();return;}
 const dups=document.querySelectorAll('.comic-hero');dups.forEach((d,i)=>{if(i>0)d.remove();});
 if(old){const anchor=document.querySelector('.comic-notice-board')||head;if(old.previousElementSibling!==anchor)anchor.after(old);return;}
 const h=mk('section','comic-hero');h.setAttribute('aria-label','Welcome');applyColors(h,w);
 const bg=mk('div','comic-hero-bg');
 if(w.banner&&/^(\/|https?:\/\/)/.test(w.banner)){
  if(w.banner_type==='video'){const v=document.createElement('video');v.src=w.banner;v.muted=true;v.loop=true;v.autoplay=true;v.playsInline=true;v.setAttribute('playsinline','');v.preload='auto';v.addEventListener('error',()=>v.remove());bg.append(v);v.play?.().catch(()=>{});}
  else{const i=document.createElement('img');i.src=w.banner;i.alt='';i.addEventListener('error',()=>i.remove());bg.append(i);}
 }
 const body=mk('div','comic-hero-body');
 const kicker=mk('div','comic-welcome-kicker');userText(w.title||'WELCOME TO {user}').split('').forEach((ch,i)=>{const sp=mk('span','',ch===' '?'\u00a0':ch);sp.style.setProperty('--n',i);kicker.append(sp);});
 const brand=userText(w.name||settings.brand||document.querySelector('#logo a')?.textContent||'Pterodactyl').trim();
 body.append(kicker,mk('h1','comic-welcome-name',brand));
 if(w.text)body.append(mk('p','comic-welcome-text',userText(w.text)));
 h.append(bg,mk('div','comic-hero-shade'),body);
 head.after(h);
}
const noticeCfg=()=>settings.notice||{};
function noticeKey(){const n=noticeCfg(),who=(currentUser||'user').toLowerCase().replace(/[^a-z0-9_-]+/g,'_').slice(0,48)||'user';return 'comic_notice_'+who+'_v'+(parseInt(n.version,10)||1);}
function noticeSeen(){try{return localStorage.getItem(noticeKey())==='1';}catch{return false;}}
function markNoticeSeen(){try{localStorage.setItem(noticeKey(),'1');}catch{}}
function notice(){
 const n=noticeCfg(),head=document.querySelector('.comic-header'),old=document.querySelector('.comic-notice-board');
 const isAdmin=location.pathname==='/admin'||location.pathname.startsWith('/admin/');
 if(!head||isAdmin||!n.enabled||(n.show_once!==false&&noticeSeen())){old?.remove();return;}
 if(old){if(old.previousElementSibling!==head)head.after(old);return;}
 const board=mk('section','comic-notice-board');board.setAttribute('role','status');board.setAttribute('aria-label',userText(n.title||'Pengumuman'));
 const badge=mk('div','comic-notice-icon','!');
 const copy=mk('div','comic-notice-copy');copy.append(mk('strong','comic-notice-title',userText(n.title||'PENGUMUMAN')));if(n.text)copy.append(mk('span','comic-notice-text',userText(n.text)));
 const actions=mk('div','comic-notice-actions');
 if(n.url&&safeUrl(n.url)){const a=mk('a','comic-notice-link',userText(n.button_label||'Lihat Info'));a.href=n.url;a.target='_blank';a.rel='noopener noreferrer';a.addEventListener('click',()=>{if(n.show_once!==false)markNoticeSeen();});actions.append(a);}
 const close=mk('button','comic-notice-close','×');close.type='button';close.setAttribute('aria-label','Tutup notifikasi');close.addEventListener('click',()=>{if(n.show_once!==false)markNoticeSeen();board.remove();});actions.append(close);
 board.append(badge,copy,actions);head.after(board);
}

let gateShown=false;
function gate(){
 if(gateShown)return;
 const w=settings.welcome||{},g=gateCfg();
 const gLinks=(Array.isArray(g.links)?g.links:[]).filter(l=>l&&l.label&&safeUrl(l.url));
 gateShown=true;
 if(!g.enabled||!gLinks.length||isJoined())return;
 const o=mk('div','comic-welcome');o.setAttribute('role','dialog');o.setAttribute('aria-modal','true');o.setAttribute('aria-label',g.title||'Join');applyColors(o,w);
 const card=mk('div','comic-welcome-card');
 card.append(mk('div','comic-welcome-kicker',g.title||'Join dulu ya!'));
 const box=mk('div','comic-gate');
 if(g.text)box.append(mk('p','comic-gate-text',g.text));
 const row=mk('div','comic-gate-links');
 const label=g.done_label||'Sudah Follow';
 const done=mk('button','comic-welcome-btn comic-gate-done',label);done.type='button';
 const need=g.require_click!==false;done.disabled=need;
 let unlocking=false;
 const unlock=()=>{if(!need||unlocking)return;unlocking=true;let n=3;done.textContent=label+' ('+n+')';const t=setInterval(()=>{n--;if(n<=0){clearInterval(t);done.disabled=false;done.textContent=label;done.classList.add('ready');}else done.textContent=label+' ('+n+')';},1000);};
 gLinks.forEach(l=>{const a=mk('a','comic-welcome-btn comic-gate-link',l.label);a.href=l.url;a.target='_blank';a.rel='noopener noreferrer';a.addEventListener('click',unlock);row.append(a);});
 done.addEventListener('click',()=>{if(done.disabled)return;markJoined();o.classList.add('closing');document.getElementById('app')?.removeAttribute('inert');document.body.classList.remove('comic-welcome-open');setTimeout(()=>o.remove(),380);});
 box.append(row,done);card.append(box);o.append(mk('div','comic-welcome-shade'),card);
 document.body.append(o);document.body.classList.add('comic-welcome-open');document.getElementById('app')?.setAttribute('inert','');
 (o.querySelector('.comic-gate-link')||done).focus({preventScroll:true});
}
function schedule(){if(!queued){queued=true;requestAnimationFrame(annotate);}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{annotate();new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});});else{annotate();new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});}
})();
