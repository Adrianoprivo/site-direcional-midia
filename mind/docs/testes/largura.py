# LRG: alça de largura do tópico (arrastar livre, salvar, recarregar, duplo clique = automático, linha e caixa, lado esquerdo)
import json
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
LONGO='se não, podemos criar uma, com riqueza de detalhamento e automatizada'
MAPA={"nodeData":{"id":"r","topic":"Centro","children":[
 {"id":"a","topic":"Implantação","direction":1,"children":[{"id":"a1","topic":LONGO},{"id":"a2","topic":"Curto"}]},
 {"id":"b","topic":"Esquerda","direction":0,"children":[{"id":"b1","topic":LONGO}]}]},"arrows":[],"summaries":[],"meta":{"privo":{"tema":"direcional","estilo":"linha"}}}
ID='11111111-1111-4111-8111-111111111111'
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
def carregar(pg,dados=MAPA,manter=False):
    if not manter:
        pg.goto('http://local/mind/')
        pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'%s',titulo:'T',favorito:false,atualizado_em:new Date().toISOString(),dados:d}]))}"%ID,dados)
    pg.goto('http://local/mind/?t=1#/mapa/'+ID); pg.wait_for_selector('me-root'); pg.wait_for_timeout(700)
def arrastar(pg,dx):
    bb=pg.locator('#alca-largura').bounding_box(); x=bb['x']+bb['width']/2; y=bb['y']+bb['height']/2
    pg.mouse.move(x,y); pg.mouse.down(); pg.mouse.move(x+dx/2,y,steps=4); pg.mouse.move(x+dx,y,steps=4); pg.mouse.up(); pg.wait_for_timeout(1500)
larg=lambda pg,i:pg.evaluate("i=>Math.round(mind.findEle(i).getBoundingClientRect().width/(mind.scaleVal||1))",i)
alt=lambda pg,i:pg.evaluate("i=>Math.round(mind.findEle(i).getBoundingClientRect().height/(mind.scaleVal||1))",i)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1900,'height':900}); pg.route('**/*',rotas)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    carregar(pg)
    ok('LRG-01 alça escondida sem seleção',pg.locator('#alca-largura').is_hidden())
    pg.evaluate("mind.selectNode(mind.findEle('a1'))"); pg.wait_for_timeout(200)
    ok('LRG-02 alça aparece no tópico selecionado',pg.locator('#alca-largura').is_visible())
    w0,h0=larg(pg,'a1'),alt(pg,'a1'); pg.screenshot(path=OUT+'/lrg-1-antes.png')
    arrastar(pg,-300)
    w1,h1=larg(pg,'a1'),alt(pg,'a1')
    ok('LRG-03 estreitou e quebrou linha',w1<w0-200 and h1>h0,(w0,h0,w1,h1))
    salvo=pg.evaluate("JSON.parse(sessionStorage.getItem('mockdb'))[0].dados.nodeData.children[0].children[0].style")
    ok('LRG-04 largura salva no banco',salvo and salvo.get('width','').endswith('px'),salvo)
    pg.screenshot(path=OUT+'/lrg-2-estreito.png')
    pg.evaluate("mind.selectNode(mind.findEle('a1'))"); pg.wait_for_timeout(200)
    arrastar(pg,120); w2=larg(pg,'a1')
    ok('LRG-05 alargar de novo (livre, sem opções fixas)',w2>w1+60,(w1,w2))
    carregar(pg,manter=True)
    ok('LRG-06 largura continua depois de recarregar',abs(larg(pg,'a1')-w2)<=3,(w2,larg(pg,'a1')))
    pg.evaluate("mind.selectNode(mind.findEle('a1'))"); pg.wait_for_timeout(200)
    pg.locator('#alca-largura').dblclick(); pg.wait_for_timeout(1500)
    ok('LRG-07 duplo clique volta ao automático',abs(larg(pg,'a1')-w0)<=3,(w0,larg(pg,'a1')))
    salvo=pg.evaluate("JSON.parse(sessionStorage.getItem('mockdb'))[0].dados.nodeData.children[0].children[0].style||{}")
    ok('LRG-08 automático tira a largura do banco','width' not in salvo,salvo)
    # lado esquerdo: arrastar para a direita estreita
    pg.evaluate("mind.selectNode(mind.findEle('b1'))"); pg.wait_for_timeout(200)
    wb=larg(pg,'b1'); arrastar(pg,250)
    ok('LRG-09 lado esquerdo estreita puxando pra direita',larg(pg,'b1')<wb-150,(wb,larg(pg,'b1')))
    # estilo caixa
    d2=json.loads(json.dumps(MAPA)); d2['meta']['privo']['estilo']='caixa'; d2['nodeData']['children'][0]['children'][0]['style']={'width':'200px'}
    carregar(pg,d2)
    ok('LRG-10 estilo caixa respeita a largura',abs(larg(pg,'a1')-200)<=3,larg(pg,'a1'))
    pg.screenshot(path=OUT+'/lrg-3-caixa.png')
    ok('LRG-11 sem erros na página',not errs,errs)
    print('FALHAS:',falhas)
