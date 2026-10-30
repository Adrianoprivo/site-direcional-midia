# sublinhado/riscado visíveis (TXT-06), F5 mantém zoom e posição (VIS-09), bolinha fixa e clique também na linha (CLQ-02)
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
A='11111111-1111-4111-8111-111111111111'
mapa={'id':A,'titulo':'T','favorito':False,'atualizado_em':'2026-10-30T10:00:00Z','criado_em':'2026-10-30T10:00:00Z','excluido_em':None,'dados':{'nodeData':{'id':'r','topic':'Centro','children':[
 {'id':'d','topic':'Direita','direction':1,'children':[{'id':'d1','topic':'Tópico da direita','children':[{'id':'d11','topic':'filho'}]},{'id':'d2','topic':'Outro tópico'}]},
 {'id':'e','topic':'Esquerda','direction':0,'children':[{'id':'e1','topic':'Tópico da esquerda','children':[{'id':'e11','topic':'filho'}]}]}]},'arrows':[],'summaries':[]}}
def clica(pg,i):
    r=pg.evaluate("i=>{const r=mind.findEle(i).getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}",i); pg.mouse.click(*r); pg.wait_for_timeout(200)
def rect(pg,sel): return pg.evaluate("s=>{const r=document.querySelector(s).getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(v=>Math.round(v*10)/10)}",sel)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1400,'height':800}); pg.route('**/*',rotas); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://local/mind/'); pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([d]))}",mapa)
    pg.goto('http://local/mind/?t=1#/mapa/'+A); pg.wait_for_selector('me-root'); pg.wait_for_timeout(900)
    ok('VIS mapa com conteúdo abre em 50%',abs(pg.evaluate("mind.scaleVal")-.5)<.01)
    pg.evaluate("mind.scale(1);mind.toCenter()"); pg.wait_for_timeout(300)
    # ---- sublinhado e riscado ----
    dec=lambda i:pg.evaluate("i=>getComputedStyle(mind.findEle(i).querySelector('.text')).textDecorationLine",i)
    clica(pg,'d2'); pg.click('#fmt [data-f=u]'); pg.wait_for_timeout(200)
    ok('TXT sublinhado aparece de verdade no texto (botão da barra)','underline' in dec('d2'),dec('d2'))
    pg.click('#fmt [data-f=s]'); pg.wait_for_timeout(200)
    ok('TXT riscado aparece de verdade (junto com o sublinhado)','line-through' in dec('d2') and 'underline' in dec('d2'),dec('d2'))
    pg.click('#fmt [data-f=u]'); pg.click('#fmt [data-f=s]'); pg.wait_for_timeout(200); ok('TXT clicar de novo tira os dois',dec('d2')=='none',dec('d2'))
    clica(pg,'d2'); pg.click('#fmt [data-f=fonte]'); pg.wait_for_timeout(250); pg.click('#pop [data-f2=u]'); pg.wait_for_timeout(200)
    ok('TXT sublinhado pelo painel de fonte','underline' in dec('d2'))
    pg.click('#pop [data-f2=s]'); pg.wait_for_timeout(200); ok('TXT riscado pelo painel de fonte','line-through' in dec('d2'))
    pg.click('#pop [data-f2=limpar]'); pg.wait_for_timeout(200); ok('TXT "sem efeito" limpa',dec('d2')=='none')
    pg.keyboard.press('Escape')
    # ---- bolinha fixa e clique na linha ----
    pg.evaluate("mind.expandNode(mind.findEle('d1'),false);mind.expandNode(mind.findEle('e1'),false)"); pg.wait_for_timeout(300)
    pg.mouse.move(700,700); pg.wait_for_timeout(200)
    epd=lambda i:pg.evaluate("i=>{const r=mind.findEle(i).nextElementSibling.getBoundingClientRect();return [Math.round(r.x*10)/10,Math.round(r.y*10)/10,Math.round(r.width*10)/10]}",i)
    antes=epd('d1'); c=pg.evaluate("i=>{const r=mind.findEle(i).nextElementSibling.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}",'d1')
    pg.mouse.move(c[0],c[1],steps=5); pg.wait_for_timeout(300); depois=epd('d1')
    ok('CLQ bolinha não muda de tamanho nem de lugar quando o mouse chega',antes==depois,(antes,depois))
    estado=lambda i:pg.evaluate("i=>mind.findEle(i).nextElementSibling.classList.contains('minus')",i)
    def clicaEm(x,y):
        pg.mouse.move(x,y,steps=4); pg.wait_for_timeout(80); pg.mouse.down(); pg.wait_for_timeout(70); pg.mouse.up(); pg.wait_for_timeout(300)
    s0=estado('d1'); clicaEm(c[0]+14,c[1]); ok('CLQ clicar na linha logo ao lado (para fora) abre/fecha o galho da direita',estado('d1')!=s0)
    s0=estado('d1'); clicaEm(c[0],c[1]); ok('CLQ clicar na bolinha também abre/fecha',estado('d1')!=s0)
    ce=pg.evaluate("i=>{const r=mind.findEle(i).nextElementSibling.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}",'e1')
    s0=estado('e1'); clicaEm(ce[0]-14,ce[1]); ok('CLQ clicar na linha ao lado da bolinha do lado esquerdo também funciona',estado('e1')!=s0)
    # clicar no texto perto da borda NÃO pode abrir/fechar (só seleciona)
    tr=pg.evaluate("i=>{const r=mind.findEle(i).getBoundingClientRect();return [r.right-10,r.y+r.height/2]}",'d1'); s0=estado('d1'); clicaEm(*tr)
    ok('CLQ clicar no texto do tópico só seleciona (não abre/fecha)',estado('d1')==s0 and pg.evaluate("mind.currentNode&&mind.currentNode.nodeObj.id")=='d1')
    # ---- F5 mantém zoom e posição ----
    pg.evaluate("mind.scale(.8)"); pg.mouse.move(300,700); pg.mouse.down(); pg.mouse.move(380,660,steps=6); pg.mouse.up(); pg.wait_for_timeout(500)
    zoom0=pg.evaluate("mind.scaleVal"); r0=rect(pg,'me-root me-tpc')
    pg.reload(); pg.wait_for_selector('me-root'); pg.wait_for_timeout(1200)
    r1=rect(pg,'me-root me-tpc')
    ok('VIS F5 mantém o zoom',abs(pg.evaluate("mind.scaleVal")-zoom0)<.01 and pg.text_content('#z-val')==str(round(zoom0*100))+'%',(zoom0,pg.evaluate("mind.scaleVal")))
    ok('VIS F5 mantém a posição do mapa na tela',abs(r0[0]-r1[0])<3 and abs(r0[1]-r1[1])<3,(r0,r1))
    pg.reload(); pg.wait_for_selector('me-root'); pg.wait_for_timeout(1000)
    ok('VIS segundo F5 também mantém',abs(pg.evaluate("mind.scaleVal")-zoom0)<.01)
    pg.click('#voltar'); pg.mouse.move(1000,650); pg.wait_for_timeout(300); pg.evaluate("location.hash='#/mapa/%s'"%A); pg.wait_for_selector('me-root'); pg.wait_for_timeout(900)
    ok('VIS sair do mapa e voltar abre de novo em 50%',abs(pg.evaluate("mind.scaleVal")-.5)<.01,pg.evaluate("mind.scaleVal"))
    ok('ERROS de página',errs==[],errs); print('FALHAS:',falhas); b.close()
