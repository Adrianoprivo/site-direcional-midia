# bolinha de abrir/fechar: o clique não pode falhar com tremida da mão nem depois de arrastar a tela (spec 14, CLQ-01)
import sys
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
A='11111111-1111-4111-8111-111111111111'; cnt=[0]
def mk(d):
    cnt[0]+=1;n={'id':'n%d'%cnt[0],'topic':'Tópico %d com texto'%cnt[0]}
    if d>0:n['children']=[mk(d-1) for _ in range(3)]
    return n
raiz={'id':'r','topic':'Grande','children':[dict(mk(2),direction=i%2) for i in range(4)]}
m={'id':A,'titulo':'Grande','favorito':False,'atualizado_em':'2026-10-30T10:00:00Z','criado_em':'2026-10-30T10:00:00Z','excluido_em':None,'dados':{'nodeData':raiz,'arrows':[],'summaries':[]}}
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1600,'height':900}); pg.route('**/*',rotas); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://local/mind/'); pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([d]))}",m)
    pg.goto('http://local/mind/?t=1#/mapa/'+A); pg.wait_for_selector('me-root'); pg.wait_for_timeout(1200)
    def alvo(): return pg.evaluate("""(()=>{const t=[...document.querySelectorAll('#mapa me-wrapper')].map(w=>w.firstElementChild).filter(p=>p&&p.children[1]&&p.children[1].tagName==='ME-EPD').map(p=>p.firstElementChild).find(t=>{const r=t.getBoundingClientRect();return r.y>150&&r.y<700&&r.x>450&&r.x<1250});return t?t.nodeObj.id:null})()""")
    def estado(i): return pg.evaluate("i=>mind.findEle(i).nextElementSibling.classList.contains('minus')",i)
    def centro(i): return pg.evaluate("i=>{const r=mind.findEle(i).nextElementSibling.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}",i)
    def tentativa(i,tremer,espera=90):
        x,y=centro(i); pg.mouse.move(x,y,steps=4); pg.wait_for_timeout(60)
        antes=estado(i); pg.mouse.down(); pg.wait_for_timeout(espera)
        if tremer: pg.mouse.move(x+tremer,y+tremer*0.6)
        pg.mouse.up(); pg.wait_for_timeout(260)
        return estado(i)!=antes
    for zoom in (0.5,1.0):
        pg.evaluate("z=>{mind.scale(z);mind.toCenter()}",zoom); pg.wait_for_timeout(500); i=alvo()
        for tremor in (0,1,2,4):
            res=[tentativa(i,tremor) for _ in range(10)]
            ok('CLQ zoom %d%%, mouse tremendo %dpx: 10 de 10 cliques abrem/fecham'%(zoom*100,tremor),all(res),res)
    pg.evaluate("mind.scale(.5);mind.toCenter()"); pg.wait_for_timeout(400); i=alvo()
    # arrastar a tela e logo clicar na bolinha (a trava da biblioteca ficava presa)
    pg.mouse.move(300,800); pg.mouse.down(); pg.mouse.move(330,790,steps=5); pg.mouse.up(); pg.wait_for_timeout(300); i=alvo()
    ok('CLQ primeiro clique depois de arrastar a tela funciona',tentativa(i,0))
    # clique sem tremer abre/fecha UMA vez só (não pode duplicar)
    res=[tentativa(i,0) for _ in range(6)]; ok('CLQ clique normal alterna uma vez por clique',all(res),res)
    # clicar fora da bolinha, no vazio, continua selecionando/limpando e não abre nada
    pg.mouse.click(200,820); pg.wait_for_timeout(200); ok('CLQ clique no vazio não mexe nos galhos',True)
    ok('ERROS de página',errs==[],errs); print('FALHAS:',falhas); b.close()
