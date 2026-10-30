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
    # a bolinha NÃO pode mudar de lugar quando o galho abre/fecha, e fechado tem que ter o tracinho ligando o fim da linha até ela
    JS="""id=>{const t=mind.findEle(id),e=t.nextElementSibling,r=e.getBoundingClientRect(),mp=t.parentElement,ps=getComputedStyle(mp,'::after'),pr=mp.getBoundingClientRect(),tr=t.getBoundingClientRect(),esq=!!t.closest('.lhs');
      return {minus:e.classList.contains('minus'),cx:Math.round(r.x+r.width/2),cy:Math.round(r.y+r.height/2),stub:ps.content!=='none'&&ps.content!=='normal',w:Math.round(parseFloat(ps.width)||0),
        ligado:ps.content!=='none'&&ps.content!=='normal'?(esq?Math.abs((pr.left+parseFloat(ps.left))-(r.x+r.width/2))<2||true:true):false,borda:esq?Math.round(tr.left):Math.round(tr.right)}}"""
    for i in ('d1','e1'):
        pg.evaluate("i=>mind.expandNode(mind.findEle(i),true)",i); pg.wait_for_timeout(300)
        pg.evaluate("i=>mind.expandNode(mind.findEle(i),false)",i); pg.wait_for_timeout(250)
        f=pg.evaluate("("+JS+")('%s')"%i)
        pg.evaluate("i=>mind.expandNode(mind.findEle(i),true)",i); pg.wait_for_timeout(250)
        a=pg.evaluate("("+JS+")('%s')"%i)
        ok('LIN %s: a bolinha fica no MESMO lugar fechada e aberta (não pula)'%i,abs(f['cx']-a['cx'])<=1 and abs(f['cy']-a['cy'])<=1,(f['cx'],a['cx']))
        ok('LIN %s: fechado tem o tracinho ligando o fim da linha à bolinha; aberto não precisa'%i,f['stub'] and f['w']==20 and not a['stub'],(f['stub'],f['w'],a['stub']))
        ok('LIN %s: a bolinha está a ~20 px do fim da linha (o tracinho cobre exatamente isso)'%i,abs(abs(f['cx']-f['borda'])-20)<=3,(f['cx'],f['borda']))
    pg.evaluate("['e1','e2','d1'].forEach(i=>{const e=mind.findEle(i);if(e.nextElementSibling.classList.contains('minus'))mind.expandNode(e,false)})"); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('#mapa me-tpc .text').forEach(s=>{s.style.fontSize='24px';s.style.letterSpacing='2px'})"); pg.wait_for_timeout(500)
    pg.evaluate("(()=>{window.__d=id=>{const t=mind.findEle(id),e=t.nextElementSibling,r=e.getBoundingClientRect(),tr=t.getBoundingClientRect(),esq=!!t.closest('.lhs');return Math.round(Math.abs((r.x+r.width/2)-(esq?tr.left:tr.right)))};return 1})()")
    depois=pg.evaluate("['e1','e2','d1'].map(i=>__d(i))")
    ok('LIN depois de o texto crescer a bolinha continua a ~20 px do fim da linha (linhas refeitas)',all(abs(x-20)<=3 for x in depois),depois)
    pg.screenshot(path=OUT+'/linha-bolinha.png')
    # painel de fonte mostra cada fonte
    pg.evaluate("mind.scale(1);mind.toCenter()"); r=pg.evaluate("(()=>{const r=mind.findEle('d1').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()"); pg.mouse.click(*r); pg.wait_for_timeout(300)
    pg.click('#fmt [data-f=fonte]'); pg.wait_for_timeout(300)
    fams=pg.evaluate("[...document.querySelectorAll('#pop [data-fonte]')].map(b=>b.style.fontFamily)")
    ok('FNT botões do painel mostram 4 fontes diferentes',len(fams)==4 and len(set(fams))==4 and 'Lora' in fams[1] and 'Caveat' in fams[2] and 'JetBrains' in fams[3],fams)
    pg.screenshot(path=OUT+'/painel-fonte.png')
    ok('ERROS de página',errs==[],errs); print('FALHAS:',falhas); b.close()
