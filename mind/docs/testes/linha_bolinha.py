# a bolinha de abrir/fechar fica no fim da linha mesmo quando o tamanho do tópico muda depois (fonte/emoji carregando) e a fonte aparece no painel
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
A='11111111-1111-4111-8111-111111111111'
mapa={'id':A,'titulo':'T','favorito':False,'atualizado_em':'2026-10-30T10:00:00Z','criado_em':'2026-10-30T10:00:00Z','excluido_em':None,'dados':{'nodeData':{'id':'r','topic':'Centro','children':[
 {'id':'e','topic':'Lado esquerdo','direction':0,'children':[{'id':'e1','topic':'Ajuste: bolinha de abrir/fechar pequena','icons':['⌛'],'expanded':False,'children':[{'id':'e11','topic':'x'},{'id':'e12','topic':'y'}]},{'id':'e2','topic':'Outro','expanded':False,'children':[{'id':'e21','topic':'z'}]}]},
 {'id':'d','topic':'Lado direito','direction':1,'children':[{'id':'d1','topic':'Tópico da direita com texto','expanded':False,'children':[{'id':'d11','topic':'x'}]}]}]},'arrows':[],'summaries':[]}}
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1400,'height':800}); pg.route('**/*',rotas); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://local/mind/'); pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([d]))}",mapa)
    pg.goto('http://local/mind/?t=1#/mapa/'+A); pg.wait_for_selector('me-root'); pg.wait_for_timeout(900); pg.evaluate("mind.scale(1);mind.toCenter()"); pg.wait_for_timeout(300)
    # distância entre o fim da linha e a bolinha de cada galho fechado
    medir=pg.evaluate("""()=>{window.__dist=id=>{const t=mind.findEle(id),e=t.nextElementSibling,esq=!!t.closest('.lhs');const mw=t.closest('me-main > me-wrapper'),svg=[...mw.children].find(c=>c.tagName==='svg');
      let k=0,alvo=null;const paths=svg.children;const rec=w=>{const f=w.children[1]&&w.children[1].children;if(!f)return;for(const c of f){const tp=c.firstChild.firstChild,p=paths[k++];if(tp===t)alvo=p;const ep=c.firstChild.children[1];if(ep&&ep.expanded)rec(c)}};rec(mw);
      const rp=alvo.getBoundingClientRect(),re=e.getBoundingClientRect(),cx=re.x+re.width/2,fim=esq?rp.left:rp.right;return Math.round(Math.abs(cx-fim))};return ['e1','e2','d1'].map(__dist)}""")
    ok('LIN bolinha encostada no fim da linha no começo',max(medir)<=26,medir)
    # simula o que acontece quando a fonte/emoji termina de carregar: o texto fica mais largo e mais alto depois do desenho
    pg.evaluate("document.querySelectorAll('#mapa me-tpc .text').forEach(s=>{s.style.fontSize='24px';s.style.letterSpacing='2px'})"); pg.wait_for_timeout(500)
    depois=pg.evaluate("['e1','e2','d1'].map(__dist)")
    ok('LIN depois de o texto crescer, as linhas são refeitas e a bolinha continua no fim da linha',max(depois)<=26,depois)
    pg.screenshot(path=OUT+'/linha-bolinha.png')
    # painel de fonte mostra cada fonte
    pg.evaluate("mind.scale(1);mind.toCenter()"); r=pg.evaluate("(()=>{const r=mind.findEle('d1').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()"); pg.mouse.click(*r); pg.wait_for_timeout(300)
    pg.click('#fmt [data-f=fonte]'); pg.wait_for_timeout(300)
    fams=pg.evaluate("[...document.querySelectorAll('#pop [data-fonte]')].map(b=>b.style.fontFamily)")
    ok('FNT botões do painel mostram 4 fontes diferentes',len(fams)==4 and len(set(fams))==4 and 'Lora' in fams[1] and 'Caveat' in fams[2] and 'JetBrains' in fams[3],fams)
    pg.screenshot(path=OUT+'/painel-fonte.png')
    ok('ERROS de página',errs==[],errs); print('FALHAS:',falhas); b.close()
