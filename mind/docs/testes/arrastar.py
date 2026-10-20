# ARR-01..11: arrastar que encaixa na estrutura (spec.md, seção 5)
import json
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
MAPA={"nodeData":{"id":"r","topic":"Centro","children":[
 {"id":"a","topic":"Alfa","direction":1,"metadata":{"pos":{"x":0,"y":-20}},"children":[{"id":"a1","topic":"Alfa 1","metadata":{"pos":{"x":80,"y":40}},"children":[{"id":"a11","topic":"Alfa 1.1"}]},{"id":"a2","topic":"Alfa 2"},{"id":"a3","topic":"Alfa 3"}]},
 {"id":"b","topic":"Beta","direction":0,"children":[{"id":"b1","topic":"Beta 1"},{"id":"b2","topic":"Beta 2"}]}]},"arrows":[],"summaries":[]}
ID='11111111-1111-4111-8111-111111111111'
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
def box(pg,i): return pg.evaluate("i=>{const r=mind.findEle(i).getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,cx:r.x+r.width/2,cy:r.y+r.height/2,l:r.left,r:r.right,t:r.top,b:r.bottom}}",i)
def pai(pg,i): return pg.evaluate("i=>{let p=null;const f=(n,par)=>{if(n.id===i)p=par;(n.children||[]).forEach(c=>f(c,n))};f(mind.getData().nodeData,null);return p&&p.id}",i)
def filhos(pg,i): return pg.evaluate("i=>{const f=n=>n.id===i?n:(n.children||[]).map(f).find(Boolean);return (f(mind.getData().nodeData).children||[]).map(c=>c.id)}",i)
def lado(pg,i): return pg.evaluate("i=>mind.findEle(i).closest('.lhs')?'esq':'dir'",i)
def no(pg,i): return pg.evaluate("i=>{const f=n=>n.id===i?n:(n.children||[]).map(f).find(Boolean);const n=f(mind.getData().nodeData);return {dir:n.direction,pos:n.metadata&&n.metadata.pos||null}}",i)
def sobrepostos(pg): return pg.evaluate("""()=>{const r=[...document.querySelectorAll('#mapa me-tpc')].map(t=>[t.textContent,t.getBoundingClientRect()]);const o=[];
  for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){const a=r[i][1],b=r[j][1];if(a.left<b.right-1&&b.left<a.right-1&&a.top<b.bottom-1&&b.top<a.bottom-1)o.push(r[i][0]+' x '+r[j][0])}return o}""")
def arrasta(pg,i,x,y,passos=14,antes_de_soltar=None,soltar=True):
    b=box(pg,i); pg.mouse.move(b['cx'],b['cy']); pg.mouse.down()
    for k in range(1,passos+1): pg.mouse.move(b['cx']+(x-b['cx'])*k/passos,b['cy']+(y-b['cy'])*k/passos); pg.wait_for_timeout(16)
    pg.wait_for_timeout(80)
    r=antes_de_soltar() if antes_de_soltar else None
    if soltar: pg.mouse.up(); pg.wait_for_timeout(500)
    return r
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); pg.route('**/*',rotas)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://local/mind/')
    pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'%s',titulo:'Teste',favorito:false,atualizado_em:new Date().toISOString(),dados:d}]))}"%ID,MAPA)
    pg.goto('http://local/mind/?t=1#/mapa/'+ID); pg.wait_for_selector('me-root'); pg.wait_for_timeout(800)

    ok('ARR-09 posição antiga de sub-tópico descartada',no(pg,'a1')['pos'] is None)
    ok('ARR-09 galho principal mantém posição',no(pg,'a')['pos']=={'x':0,'y':-20})

    # ARR-11 + ARR-02: durante o arraste as bolinhas somem e aparece a prévia (linha reta = antes)
    a1=box(pg,'a1'); pg.mouse.move(a1['cx'],a1['cy']); pg.wait_for_timeout(200)
    ok('bolinha + aparece no hover',pg.evaluate("!document.getElementById('mais-frente').hidden"))
    def durante():
        return pg.evaluate("[document.getElementById('mais-frente').hidden,document.getElementById('mais-baixo').hidden,document.getElementById('fmt').hidden,getComputedStyle(document.getElementById('ima')).display,document.getElementById('ima-l').getAttribute('class')]")
    a1=box(pg,'a1')
    d=arrasta(pg,'a3',a1['cx'],a1['t']+3,antes_de_soltar=durante)
    ok('ARR-11 + e barra somem no arraste',d[0] and d[1] and d[2],d)
    ok('ARR-02 prévia "antes" = linha reta',d[3]=='block' and d[4]=='reta',d)
    ok('ARR-04 soltou antes de Alfa 1',filhos(pg,'a')==['a3','a1','a2'],filhos(pg,'a'))
    pg.wait_for_timeout(300)
    ok('ARR-11 + reaparece no lugar novo',pg.evaluate("(()=>{const e=document.getElementById('mais-frente');if(e.hidden)return false;const r=e.getBoundingClientRect(),t=mind.findEle('a3').getBoundingClientRect();return Math.abs((r.y+r.height/2)-(t.y+t.height/2))<6})()"))

    # depois (terço de baixo)
    a1=box(pg,'a1'); arrasta(pg,'a3',a1['cx'],a1['b']-2)
    ok('ARR-03 terço de baixo = depois',filhos(pg,'a')==['a1','a3','a2'],filhos(pg,'a'))

    # dentro (meio) + troca de lado (ARR-05): Alfa 2 vira filho de Beta 1 (lado esquerdo)
    b1=box(pg,'b1')
    d=arrasta(pg,'a2',b1['cx'],b1['cy'],antes_de_soltar=lambda: pg.evaluate("[document.querySelectorAll('#mapa me-tpc.alvo-drop').length,document.getElementById('ima-l').getAttribute('class')]"))
    ok('ARR-02 prévia "dentro" = contorno + curva',d[0]==1 and d[1]=='',d)
    ok('ARR-04 virou filho de Beta 1',pai(pg,'a2')=='b1')
    ok('ARR-05 agora aponta pra esquerda',lado(pg,'a2')=='esq')

    # leva o galho junto: Alfa 1 (com Alfa 1.1) vai pra dentro de Beta 2
    b2=box(pg,'b2')
    d=arrasta(pg,'a1',b2['cx'],b2['cy'],antes_de_soltar=lambda: (box(pg,'a1'),box(pg,'a11')))
    ok('ARR-01 neto acompanha durante o arraste',abs((d[1]['x']-d[0]['x'])-(box(pg,'a11')['x']-box(pg,'a1')['x']))<400)
    ok('ARR-05 galho inteiro trocou de lado',pai(pg,'a1')=='b2' and lado(pg,'a1')=='esq' and lado(pg,'a11')=='esq' and box(pg,'a11')['x']<box(pg,'a1')['x'])

    # ARR-06 sub-tópico solto no vazio volta pro lugar
    antes=box(pg,'b1'); arrasta(pg,'b1',antes['cx'],60)
    depois=box(pg,'b1'); ok('ARR-06 sub-tópico no vazio volta',pai(pg,'b1')=='b' and abs(depois['x']-antes['x'])<2 and abs(depois['y']-antes['y'])<2)

    # ARR-08 Esc cancela
    antes=box(pg,'a3'); arrasta(pg,'a3',antes['cx']-300,antes['cy']+150,soltar=False); pg.keyboard.press('Escape'); pg.mouse.up(); pg.wait_for_timeout(400)
    ok('ARR-08 Esc cancela',pai(pg,'a3')=='a' and abs(box(pg,'a3')['x']-antes['x'])<2)

    # centro: soltar perto do lado direito do centro → vira galho principal na direita
    r=box(pg,'r'); arrasta(pg,'b2',r['r']-6,r['cy'])
    ok('dentro do centro, lado direito',pai(pg,'b2')=='r' and no(pg,'b2')['dir']==1 and lado(pg,'b2')=='dir',no(pg,'b2'))

    # galho principal no vazio do mesmo lado: fica onde soltou (posição salva)
    bb=box(pg,'b'); arrasta(pg,'b',bb['cx']-40,bb['cy']-150)
    ok('ARR-06 principal fica onde soltou',no(pg,'b')['pos'] is not None and lado(pg,'b')=='esq',no(pg,'b'))
    # principal solto do outro lado do centro → passa pra lá em posição automática
    r=box(pg,'r'); bb=box(pg,'b'); arrasta(pg,'b',r['r']+260,r['b']+220)
    ok('ARR-06 principal do outro lado troca de lado',lado(pg,'b')=='dir' and no(pg,'b')['dir']==1 and no(pg,'b')['pos'] is None,no(pg,'b'))
    ok('ARR-05 filhos do principal acompanham o lado',lado(pg,'b2')=='dir' and all(lado(pg,x)=='dir' for x in filhos(pg,'b')))

    # ARR-07 arrastar o centro move a tela, não o mapa
    r0=box(pg,'r'); arrasta(pg,'r',r0['cx']-120,r0['cy']+60); r1=box(pg,'r')
    ok('ARR-07 centro move a tela',abs(r1['cx']-r0['cx']+120)<3 and pg.evaluate("!mind.getData().nodeData.metadata"))

    ok('ARR-04 nada sobreposto',sobrepostos(pg)==[],sobrepostos(pg))

    # desfazer volta o último movimento
    ant=pai(pg,'a3'); a2=box(pg,'a2'); arrasta(pg,'a3',a2['cx'],a2['cy'])
    ok('mover a3 pra dentro de Alfa 2',pai(pg,'a3')=='a2')
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(400)
    ok('Ctrl+Z desfaz o arraste',pai(pg,'a3')==ant,pai(pg,'a3'))
    ok('Ctrl+Z não mexe no lado dos outros galhos',lado(pg,'b')=='dir' and lado(pg,'b2')=='dir',(lado(pg,'b'),lado(pg,'b2')))
    # desfazer também volta a posição livre do galho principal
    aa=box(pg,'a'); arrasta(pg,'a',aa['cx']+30,aa['cy']-160); p1=no(pg,'a')['pos']
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(400)
    ok('Ctrl+Z volta a posição livre',no(pg,'a')['pos']!=p1,(p1,no(pg,'a')['pos']))
    pg.keyboard.press('Control+y'); pg.wait_for_timeout(400)
    ok('Ctrl+Y refaz a posição livre',no(pg,'a')['pos']==p1)

    pg.wait_for_timeout(1200); ok('salvou',pg.text_content('#e-status')=='Salvo')
    estado=pg.evaluate("JSON.stringify(mind.getData().nodeData,(k,v)=>k==='parent'?undefined:v)")
    pg.screenshot(path=OUT+'/arrastar-fim.png')
    pg.reload(); pg.wait_for_selector('me-root'); pg.wait_for_timeout(700)
    ok('recarregou igual',pg.evaluate("JSON.stringify(mind.getData().nodeData,(k,v)=>k==='parent'?undefined:v)")==estado)
    print('ERROS:',errs+falhas)
    b.close()
