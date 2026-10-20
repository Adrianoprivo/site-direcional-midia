(function(){
  const store=JSON.parse(sessionStorage.getItem('mockdb')||'[]');let logged=sessionStorage.getItem('mocklog')==='1';
  const persist=()=>sessionStorage.setItem('mockdb',JSON.stringify(store));
  window.__db=store;window.__updates=0;
  function q(table){
    let op='select',payload=null,filters=[],single=false,order=null;
    const api={
      select(){if(op==='select')op='select';return api},
      insert(p){op='insert';payload=p;return api},
      update(p){op='update';payload=p;return api},
      delete(){op='delete';return api},
      eq(k,v){filters.push([k,v]);return api},
      order(k,o){order=[k,o];return api},
      single(){single=true;return api},
      then(res,rej){return Promise.resolve(run()).then(res,rej)}
    };
    function run(){
      const match=r=>filters.every(([k,v])=>r[k]===v);
      const now=new Date().toISOString();
      if(op==='insert'){const r={id:'xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx'.replace(/x/g,()=>(Math.random()*16|0).toString(16)),titulo:'Novo mapa',favorito:false,criado_em:now,atualizado_em:now,...JSON.parse(JSON.stringify(payload))};store.push(r);persist();return {data:single?r:[r],error:null}}
      if(op==='update'){const rows=store.filter(match);rows.forEach(r=>{Object.assign(r,JSON.parse(JSON.stringify(payload)));r.atualizado_em=new Date().toISOString()});window.__updates++;persist();return {data:single?rows[0]:rows,error:null}}
      if(op==='delete'){for(let i=store.length-1;i>=0;i--)if(match(store[i]))store.splice(i,1);persist();return {data:null,error:null}}
      let rows=store.filter(match).map(r=>JSON.parse(JSON.stringify(r)));
      if(single)return rows[0]?{data:rows[0],error:null}:{data:null,error:{message:'not found'}};
      return {data:rows,error:null};
    }
    return api;
  }
  /* armazenamento simulado: guarda as imagens como data URL na memória */
  const files=window.__files=JSON.parse(sessionStorage.getItem('mockfiles')||'{}');const salvaF=()=>sessionStorage.setItem('mockfiles',JSON.stringify(files));
  const paraDataUrl=b=>new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result);f.readAsDataURL(b)});
  const storage={from:()=>({
    async upload(path,blob){if(window.__falharUpload)return {data:null,error:{message:'falhou'}};files[path]=await paraDataUrl(blob);salvaF();return {data:{path},error:null}},
    async createSignedUrl(path){return files[path]?{data:{signedUrl:files[path]},error:null}:{data:null,error:{message:'not found'}}},
    async createSignedUrls(paths){return {data:paths.map(p=>({path:p,signedUrl:files[p]||null,error:files[p]?null:'not found'})),error:null}},
    async list(prefix){return {data:Object.keys(files).filter(k=>k.startsWith(prefix+'/')).map(k=>({name:k.slice(prefix.length+1)})),error:null}},
    async remove(paths){paths.forEach(p=>delete files[p]);salvaF();return {data:null,error:null}}
  })};
  window.supabase={createClient:()=>({storage,
    auth:{getSession:async()=>({data:{session:logged?{user:{id:'u1'}}:null}}),
      signInWithPassword:async({email,password})=>{if(password==='certa'){logged=true;sessionStorage.setItem('mocklog','1');return {error:null}}return {error:{message:'bad'}}},
      signOut:async()=>{logged=false;sessionStorage.removeItem('mocklog')}},
    from:q})};
})();
