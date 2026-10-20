# VIS-L1..3: vista em lista (spec.md, seção 8)
import json
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
MAPA={"nodeData":{"id":"r","topic":"Centro","children":[
 {"id":"a","topic":"Alfa","direction":1,"children":[{"id":"a1","topic":"Alfa **1**"},{"id":"a2","topic":"Alfa 2"}]},
 {"id":"b","topic":"Beta","direction":0,"children":[{"id":"b1","topic":"Beta 1"}]}]},"arrows":[],"summaries":[]}
ID='11111111-1111-4111-8111-111111111111'
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
def arvore(pg,expr='mind.getData().nodeData'):
    return pg.evaluate("(()=>{const f=n=>n.topic+(n.children&&n.children.length?'['+n.children.map(f).join(',')+']':'');return f(%s)})()"%expr)
def linha(pg,id): return pg.locator('#outline .ln[data-id="%s"] .tx'%id)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); pg.route('**/*',rotas)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://local/mind/')
    pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'%s',titulo:'Centro',favorito:false,atualizado_em:new Date().toISOString(),dados:d}]))}"%ID,MAPA)
    pg.goto('http://local/mind/?t=1#/mapa/'+ID); pg.wait_for_selector('me-root'); pg.wait_for_timeout(700)

    pg.click('#vista-btn'); pg.wait_for_timeout(100); ok('menu de vista abre',pg.is_visible('#menu-vista'))
    pg.click('#menu-vista [data-v=lista]'); pg.wait_for_timeout(200)
    ok('VIS-L1 lista aparece e mapa some',pg.is_visible('#outline') and not pg.is_visible('#mapa'))
    ok('VIS-L1 rodapé mostra "Vista em lista" e esconde zoom',pg.text_content('#vista-nome')=='Vista em lista' and not pg.is_visible('#z-val'))
    ok('VIS-L1 mesmo conteúdo',pg.locator('#outline .ln').count()==6)
    ok('VIS-L1 formatação aparece na lista',pg.evaluate("document.querySelector('#outline .ln[data-id=a1] .tx').innerHTML")=='Alfa <b>1</b>')
    pg.screenshot(path=OUT+'/lista-1.png')
    # editar texto
    linha(pg,'a2').click(); pg.keyboard.press('End'); pg.keyboard.type(' editado')
    # Enter cria embaixo
    pg.keyboard.press('Enter'); pg.keyboard.type('Alfa 3')
    # Tab vira filho do de cima
    pg.keyboard.press('Enter'); pg.keyboard.type('Detalhe'); pg.keyboard.press('Tab')
    ok('VIS-L2 Enter + Tab',arvore(pg,'dadosLista.nodeData').startswith('Centro[Alfa[Alfa **1**,Alfa 2 editado,Alfa 3[Detalhe]]'),arvore(pg,'dadosLista.nodeData'))
    # Shift+Tab sobe um nível
    pg.keyboard.press('Shift+Tab')
    ok('VIS-L2 Shift+Tab sobe',arvore(pg,'dadosLista.nodeData').startswith('Centro[Alfa[Alfa **1**,Alfa 2 editado,Alfa 3,Detalhe]'),arvore(pg,'dadosLista.nodeData'))
    # Backspace em linha vazia apaga
    pg.keyboard.press('Enter'); pg.keyboard.press('Backspace')
    ok('VIS-L2 Backspace em linha vazia apaga',arvore(pg,'dadosLista.nodeData').count('Novo')==0 and arvore(pg,'dadosLista.nodeData').count(',]')==0 and pg.locator('#outline .ln').count()==9-1-0,pg.locator('#outline .ln').count())
    # setas
    pg.keyboard.press('ArrowUp'); ok('VIS-L2 seta pra cima',pg.evaluate("document.activeElement.closest('.ln').querySelector('.tx').textContent")=='Alfa 3')
    # abrir/fechar
    pg.click('#outline .ln[data-id=a] .tg'); pg.wait_for_timeout(100); ok('VIS-L2 triângulo fecha o galho',pg.locator('#outline .ln').count()==4)
    pg.click('#outline .ln[data-id=a] .tg'); pg.wait_for_timeout(100)
    # Enter no centro cria galho principal à direita (no topo)
    linha(pg,'r').click(); pg.keyboard.press('End'); pg.keyboard.press('Enter'); pg.keyboard.type('Gama'); pg.keyboard.press('ArrowDown')
    pg.wait_for_timeout(1200); ok('VIS-L3 salva enquanto está na lista',pg.text_content('#e-status')=='Salvo' and 'Gama' in json.dumps(pg.evaluate('window.__db[0].dados')))
    pg.screenshot(path=OUT+'/lista-2.png')
    # volta pro mapa
    pg.click('#vista-btn'); pg.click('#menu-vista [data-v=mapa]'); pg.wait_for_timeout(500)
    ok('VIS-L3 volta pro mapa com tudo',pg.is_visible('#mapa') and arvore(pg).startswith('Centro[Gama,Alfa[Alfa **1**,Alfa 2 editado,Alfa 3,Detalhe]'),arvore(pg))
    ok('VIS-L3 galho novo do centro à direita',pg.evaluate("!mind.findEle(mind.getData().nodeData.children[0].id).closest('.lhs')"))
    ok('VIS-L3 Beta continua à esquerda',pg.evaluate("!!mind.findEle('b').closest('.lhs')"))
    ok('mapa funciona depois (Tab)',True)
    pg.evaluate("mind.selectNode(mind.findEle('b1'))"); pg.keyboard.press('Tab'); pg.wait_for_timeout(200); pg.keyboard.type('Neto'); pg.keyboard.press('Enter'); pg.wait_for_timeout(1200)
    ok('mapa funciona depois da lista',arvore(pg).endswith('Beta[Beta 1[Neto]]]'),arvore(pg))
    pg.screenshot(path=OUT+'/lista-3-mapa.png')
    pg.reload(); pg.wait_for_selector('me-root'); pg.wait_for_timeout(600)
    ok('recarregou igual',arvore(pg).startswith('Centro[Gama,Alfa[') and 'Neto' in arvore(pg))
    print('ERROS:',errs+falhas)
    b.close()
