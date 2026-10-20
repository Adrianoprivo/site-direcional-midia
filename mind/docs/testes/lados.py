# Bug 2026-10-19: trocar tema/estilo jogava todos os galhos pra esquerda (mapa preso no modo "tudo à esquerda")
import json
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
MAPA={"direction":0,"nodeData":{"id":"r","topic":"Centro","children":[
 {"id":"a","topic":"Alfa","direction":1,"children":[{"id":"a1","topic":"Alfa 1"}]},
 {"id":"b","topic":"Beta","direction":1},{"id":"c","topic":"Gama","direction":0}]},"arrows":[],"summaries":[]}
ID='11111111-1111-4111-8111-111111111111'
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
LADOS="['a','b','c'].map(i=>mind.findEle(i).closest('.lhs')?'esq':'dir').join(',')"
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); pg.route('**/*',rotas)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://local/mind/')
    pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'%s',titulo:'C',favorito:false,atualizado_em:new Date().toISOString(),dados:d}]))}"%ID,MAPA)
    pg.goto('http://local/mind/?t=1#/mapa/'+ID); pg.wait_for_selector('me-root'); pg.wait_for_timeout(700)
    ok('mapa gravado no modo errado abre certo',pg.evaluate(LADOS)=='dir,dir,esq' and pg.evaluate('mind.direction')==2,pg.evaluate(LADOS))
    pg.evaluate("Promise.all([novoNoLado(ME.LEFT),novoNoLado(ME.LEFT)])"); pg.wait_for_timeout(300); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok('dois cliques rápidos no + esquerdo não prendem o modo',pg.evaluate('mind.direction')==2)
    r=pg.evaluate("(()=>{const r=mind.findEle('r').getBoundingClientRect();return [r.x-150,r.y+r.height/2]})()")
    pg.evaluate("Promise.all([moverProCentro(mind.findEle('a1'),ME.LEFT)])"); pg.wait_for_timeout(300)
    ok('mover pro centro não prende o modo',pg.evaluate('mind.direction')==2)
    pg.click('#ap-btn'); pg.click('#temas [data-tema=grafite]'); pg.wait_for_timeout(300)
    ok('trocar tema mantém os lados',pg.evaluate(LADOS)=='dir,dir,esq',pg.evaluate(LADOS))
    pg.click('#estilos [data-e=caixa]'); pg.wait_for_timeout(300); pg.click('#estilos [data-e=linha]'); pg.wait_for_timeout(300)
    ok('trocar estilo mantém os lados',pg.evaluate(LADOS)=='dir,dir,esq',pg.evaluate(LADOS))
    pg.evaluate("mind.focusNode(mind.findEle('a'))"); pg.wait_for_timeout(200); pg.evaluate("mind.cancelFocus()"); pg.wait_for_timeout(200)
    ok('foco e sair do foco mantém o modo',pg.evaluate('mind.direction')==2 and pg.evaluate(LADOS)=='dir,dir,esq')
    pg.mouse.click(1000,150); pg.wait_for_timeout(1300)
    ok('grava no modo certo',pg.evaluate("window.__db[0].dados.direction")==2)
    print('ERROS:',errs+falhas)
    b.close()
