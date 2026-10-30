# VIS-01..05, EST-02, ROD-01..04 (spec.md, seções 4, 6 e 8)
import json
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
MAPA={"nodeData":{"id":"r","topic":"Planejamento","children":[
 {"id":"a","topic":"Conteúdo","direction":1,"children":[{"id":"a1","topic":"Reels"},{"id":"a2","topic":"Carrossel","children":[{"id":"a21","topic":"Roteiro"},{"id":"a22","topic":"Arte"}]}]},
 {"id":"b","topic":"Site","direction":0,"children":[{"id":"b1","topic":"Página inicial"},{"id":"b2","topic":"Blog"}]},
 {"id":"c","topic":"Anúncios","direction":1,"expanded":False,"children":[{"id":"c1","topic":"Meta"},{"id":"c2","topic":"Google","children":[{"id":"c21","topic":"Busca"}]}]}]},"arrows":[],"summaries":[]}
ID='11111111-1111-4111-8111-111111111111'
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
def carregar(pg,dados=MAPA):
    pg.goto('http://local/mind/')
    pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'%s',titulo:'Planejamento',favorito:false,atualizado_em:new Date().toISOString(),dados:d}]))}"%ID,dados)
    pg.goto('http://local/mind/?t=1#/mapa/'+ID); pg.wait_for_selector('me-root'); pg.wait_for_timeout(700); pg.evaluate("mind.scale(1);mind.toCenter()"); pg.wait_for_timeout(150)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); pg.route('**/*',rotas)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    carregar(pg)
    # VIS-01 setinha
    ok('VIS-01 setinha no fundo e nos tópicos',pg.evaluate("[getComputedStyle(document.querySelector('#mapa .map-container')).cursor,getComputedStyle(mind.findEle('a1')).cursor,getComputedStyle(mind.findEle('r')).cursor].every(c=>c==='default')"))
    # VIS-02 centro com cor sólida, sem gradiente
    ok('VIS-02 centro sólido',pg.evaluate("(()=>{const s=getComputedStyle(mind.findEle('r'));return s.backgroundImage==='none'&&s.backgroundColor==='rgb(76, 29, 149)'})()"))
    # VIS-04 bolinha com número quando fechado
    ok('VIS-04 bolinha fechada mostra 3',pg.evaluate("mind.findEle('c').parentElement.querySelector('me-epd').dataset.n")=='3')
    pg.screenshot(path=OUT+'/ap-1-direcional.png')
    # VIS-05 editar o centro: texto legível
    pg.locator('me-root me-tpc').dblclick(); pg.wait_for_timeout(300)
    cor=pg.evaluate("(()=>{const s=getComputedStyle(document.querySelector('#input-box'));return [s.color,s.backgroundColor]})()")
    ok('VIS-05 centro em edição legível',cor[0]!=cor[1] and cor[0]!='rgb(255, 255, 255)',cor)
    pg.screenshot(path=OUT+'/ap-2-editando-centro.png',clip={'x':420,'y':330,'width':440,'height':140})
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    # EST-02: Tab no centro 3 vezes → todos à direita
    pg.locator('me-root me-tpc').click(); pg.wait_for_timeout(100)
    for k in range(3):
        pg.locator('me-root me-tpc').click(); pg.keyboard.press('Tab'); pg.wait_for_timeout(150); pg.keyboard.type('Novo %d'%k); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    lados=pg.evaluate("mind.getData().nodeData.children.filter(c=>c.topic.startsWith('Novo')).map(c=>[c.direction,mind.findEle(c.id).closest('.lhs')?'esq':'dir'])")
    ok('EST-02 Tab no centro sempre à direita',len(lados)==3 and all(l==[1,'dir'] for l in lados),lados)
    pg.locator('me-root me-tpc').click(); pg.keyboard.press('Enter'); pg.wait_for_timeout(150); pg.keyboard.type('Pelo Enter'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    ok('EST-02 Enter no centro também à direita',pg.evaluate("mind.getData().nodeData.children.find(c=>c.topic==='Pelo Enter').direction")==1)
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(300)
    ok('EST-02 desfazer não troca lados',pg.evaluate("mind.getData().nodeData.children.filter(c=>c.topic.startsWith('Novo')).every(c=>!mind.findEle(c.id).closest('.lhs'))"))
    # ROD-02 zoom
    ok('ROD-01 rodapé visível',pg.is_visible('#rodape') and pg.text_content('#z-val')=='100%')
    pg.click('#z-mais'); pg.click('#z-mais'); pg.wait_for_timeout(150); ok('ROD-02 + duas vezes = 120%',pg.text_content('#z-val')=='120%' and abs(pg.evaluate('mind.scaleVal')-1.2)<.01)
    for k in range(5): pg.click('#z-menos')
    pg.wait_for_timeout(150); ok('ROD-02 − cinco vezes = 70%',pg.text_content('#z-val')=='70%')
    pg.click('#z-val'); pg.wait_for_timeout(150); ok('ROD-02 clicar no número volta pra 100%',pg.text_content('#z-val')=='100%')
    pg.mouse.move(640,600); pg.keyboard.down('Control'); pg.mouse.wheel(0,-300); pg.keyboard.up('Control'); pg.wait_for_timeout(300)
    ok('ROD-02 número acompanha zoom pela rodinha',pg.text_content('#z-val')==str(round(pg.evaluate('mind.scaleVal')*100))+'%',pg.text_content('#z-val'))
    pg.click('#z-val')
    # ROD-03 centralizar
    r0=pg.evaluate("mind.findEle('r').getBoundingClientRect().x"); pg.mouse.move(1000,650); pg.mouse.down(); pg.mouse.move(800,500,steps=6); pg.mouse.up(); pg.click('#centralizar'); pg.wait_for_timeout(300)
    c=pg.evaluate("(()=>{const r=mind.findEle('r').getBoundingClientRect(),m=document.getElementById('mapa').getBoundingClientRect();return [r.x+r.width/2-(m.x+m.width/2),r.y+r.height/2-(m.y+m.height/2)]})()")
    ok('ROD-03 centralizar põe o centro no meio da tela',abs(c[0])<4 and abs(c[1])<4,c)
    # ROD-04 + VIS-02/03 aparência
    pg.click('#ap-btn'); pg.wait_for_timeout(150); ok('ROD-04 painel de aparência abre',pg.is_visible('#painel-ap') and pg.locator('#temas button').count()==5)
    pg.screenshot(path=OUT+'/ap-3-painel.png')
    for t in ['classico','grafite','oceano','terra']:
        pg.click('#temas [data-tema=%s]'%t); pg.wait_for_timeout(200); pg.screenshot(path=OUT+'/ap-tema-%s.png'%t)
    ok('VIS-02 tema troca o centro',pg.evaluate("getComputedStyle(mind.findEle('r')).backgroundColor")=='rgb(124, 45, 18)')
    pg.click('#estilos [data-e=caixa]'); pg.wait_for_timeout(250)
    ok('VIS-03 estilo caixa',pg.evaluate("document.getElementById('mapa').classList.contains('caixa')&&getComputedStyle(mind.findEle('a1')).borderTopStyle==='solid'"))
    pg.mouse.click(1000,150); pg.wait_for_timeout(100); ok('painel fecha clicando fora',not pg.is_visible('#painel-ap'))
    pg.screenshot(path=OUT+'/ap-4-caixa.png')
    pg.wait_for_timeout(1200); ok('salvou tema e estilo',pg.evaluate("JSON.stringify(window.__db[0].dados.meta.privo)")=='{"tema":"terra","estilo":"caixa"}')
    pg.reload(); pg.wait_for_selector('me-root'); pg.wait_for_timeout(600); pg.evaluate("mind.scale(1);mind.toCenter()"); pg.wait_for_timeout(150)
    ok('recarregou com tema e estilo',pg.evaluate("document.getElementById('mapa').classList.contains('caixa')&&getComputedStyle(mind.findEle('r')).backgroundColor==='rgb(124, 45, 18)'"))
    # escuro
    pg.emulate_media(color_scheme='dark'); pg.wait_for_timeout(400); pg.screenshot(path=OUT+'/ap-5-escuro-caixa.png')
    pg.click('#ap-btn'); pg.click('#temas [data-tema=direcional]'); pg.click('#estilos [data-e=linha]'); pg.mouse.click(1000,150); pg.wait_for_timeout(300)
    pg.screenshot(path=OUT+'/ap-6-escuro-linha.png')
    # celular
    pg.emulate_media(color_scheme='light'); pg.set_viewport_size({'width':390,'height':780}); pg.wait_for_timeout(400)
    rr=pg.evaluate("[document.getElementById('rodape').getBoundingClientRect().bottom,document.getElementById('acoes').getBoundingClientRect().top]")
    ok('ROD-01 celular: rodapé acima da barra',rr[0]<=rr[1]+1,rr)
    pg.screenshot(path=OUT+'/ap-7-celular.png')
    print('ERROS:',errs+falhas)
    b.close()
