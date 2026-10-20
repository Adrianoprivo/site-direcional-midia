import json
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
MAPA={"nodeData":{"id":"r","topic":"Centro","children":[
 {"id":"a","topic":"Alfa","direction":1,"children":[{"id":"a1","topic":"Alfa 1","children":[{"id":"a11","topic":"Alfa 1.1"}]},{"id":"a2","topic":"Alfa 2"},{"id":"a3","topic":"Alfa 3"}]},
 {"id":"b","topic":"Beta","direction":0,"children":[{"id":"b1","topic":"Beta 1"},{"id":"b2","topic":"Beta 2"}]}]},"arrows":[],"summaries":[]}
def box(pg,i): return pg.evaluate("i=>{const r=mind.findEle(i).getBoundingClientRect();return {x:r.x,y:r.y,cx:r.x+r.width/2,cy:r.y+r.height/2}}",i)
def arrasta(pg,i,dx,dy,passos=10):
    b=box(pg,i); pg.mouse.move(b['cx'],b['cy']); pg.mouse.down()
    for k in range(1,passos+1): pg.mouse.move(b['cx']+dx*k/passos,b['cy']+dy*k/passos); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(500)
def rel(pg,i,ref='r'):
    a=box(pg,i);r=box(pg,ref);return (round(a['x']-r['x']),round(a['y']-r['y']))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); pg.route('**/*',rotas)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'11111111-1111-4111-8111-111111111111',titulo:'Teste',favorito:false,atualizado_em:new Date().toISOString(),dados:%s}]))" % json.dumps(MAPA) if False else "")
    pg.goto('http://local/mind/')
    pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'11111111-1111-4111-8111-111111111111',titulo:'Teste',favorito:false,atualizado_em:new Date().toISOString(),dados:d}]))}",MAPA)
    pg.goto('http://local/mind/?t=1#/mapa/11111111-1111-4111-8111-111111111111'); pg.wait_for_selector('me-root'); pg.wait_for_timeout(800)
    pg.screenshot(path=OUT+'/b0.png')
    antes={i:rel(pg,i) for i in ['a1','a11','a2','a3','b1','b2']}
    # 1) sub-topico direita com neto
    arrasta(pg,'a1',90,-110)
    depois={i:rel(pg,i) for i in ['a1','a11','a2','a3']}
    print('a1 moveu:',(depois['a1'][0]-antes['a1'][0],depois['a1'][1]-antes['a1'][1]),'| neto acompanhou:',(depois['a11'][0]-antes['a11'][0],depois['a11'][1]-antes['a11'][1]),'| irmaos parados:',depois['a2']==antes['a2'] and depois['a3']==antes['a3'])
    # 2) sub-topico lado esquerdo
    arrasta(pg,'b2',-80,60)
    print('b2 moveu:',tuple(x-y for x,y in zip(rel(pg,'b2'),antes['b2'])),'| b1 parado:',rel(pg,'b1')==antes['b1'])
    pg.screenshot(path=OUT+'/b1.png')
    # linha acompanha? ponta da linha perto do topico movido: checar path do svg sublines contendo coordenada
    # 3) raiz move o mapa todo
    r0=box(pg,'r'); rel_a=rel(pg,'a1'); arrasta(pg,'r',-150,80)
    r1=box(pg,'r'); print('raiz moveu na tela:',round(r1['x']-r0['x']),round(r1['y']-r0['y']),'| mapa junto:',rel(pg,'a1')==rel_a,'| dados raiz sem pos:',pg.evaluate("JSON.stringify(mind.getData().nodeData.metadata||null)"))
    # 4) soltar em cima de outro -> muda de galho
    a3=box(pg,'a3'); b1=box(pg,'b1'); arrasta(pg,'a3',b1['cx']-a3['cx'],b1['cy']-a3['cy'],14)
    pg.wait_for_timeout(600)
    print('Alfa 3 agora filho de:',pg.evaluate("(()=>{const f=(n,p)=>{if(n.id==='a3')return p;for(const c of n.children||[]){const r=f(c,n.topic);if(r)return r}};return f(mind.getData().nodeData,null)})()"))
    pg.wait_for_timeout(1200); print('status:',pg.text_content('#e-status'))
    # 5) recarregar mantem
    pos_antes={i:rel(pg,i) for i in ['a1','a11','b2']}
    pg.reload(); pg.wait_for_selector('me-root'); pg.wait_for_timeout(900)
    pos_dep={i:rel(pg,i) for i in ['a1','a11','b2']}
    print('recarregou igual:',pos_antes==pos_dep, pos_antes, pos_dep)
    # 6) clique seleciona e Tab cria filho
    bb=box(pg,'b1'); pg.mouse.click(bb['cx'],bb['cy']); pg.wait_for_timeout(300)
    print('selecionado:',pg.evaluate("mind.currentNode&&mind.currentNode.textContent"))
    pg.keyboard.press('Tab'); pg.wait_for_timeout(300); pg.keyboard.type('Novo neto'); pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    print('tab criou:',pg.evaluate("[...document.querySelectorAll('#mapa me-tpc')].some(e=>e.textContent.trim()==='Novo neto')"))
    pg.screenshot(path=OUT+'/b2.png')
    print('ERROS:',errs)
    b.close()
