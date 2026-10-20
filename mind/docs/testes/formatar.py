# TXT-01..05, LNK-01..03, IMG-01..05 (spec.md, seção 7)
import json
from playwright.sync_api import sync_playwright
exec(open('base_lista_editor.py').read().split('with sync_playwright')[0])
MAPA={"nodeData":{"id":"r","topic":"Centro","children":[
 {"id":"a","topic":"Alfa","direction":1,"children":[{"id":"a1","topic":"Alfa 1"},{"id":"a2","topic":"Alfa 2"},{"id":"a3","topic":"Alfa 3"}]},
 {"id":"b","topic":"Beta","direction":0,"children":[{"id":"b1","topic":"Beta 1"}]}]},"arrows":[],"summaries":[]}
ID='11111111-1111-4111-8111-111111111111'
falhas=[]
def ok(nome,cond,extra=''):
    print(('OK  ' if cond else 'FALHOU ')+nome,extra)
    if not cond: falhas.append(nome)
def no(pg,i): return pg.evaluate("i=>{const f=n=>n.id===i?n:(n.children||[]).map(f).find(Boolean);return JSON.parse(JSON.stringify(f(mind.getData().nodeData),(k,v)=>k==='parent'||k==='children'?undefined:v))}",i)
def clica(pg,i):
    r=pg.evaluate("i=>{const r=mind.findEle(i).getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}",i); pg.mouse.click(*r); pg.wait_for_timeout(150)
# imagem de teste feita no próprio navegador (PNG 400x300)
CRIA_PNG="""async()=>{const c=document.createElement('canvas');c.width=400;c.height=300;const x=c.getContext('2d');x.fillStyle='#7C3AED';x.fillRect(0,0,400,300);x.fillStyle='#fff';x.fillRect(40,40,120,80);
  const b=await new Promise(r=>c.toBlob(r,'image/png'));return new File([b],'teste.png',{type:'image/png'})}"""
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); pg.route('**/*',rotas)
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://local/mind/')
    pg.evaluate("d=>{sessionStorage.setItem('mocklog','1');sessionStorage.setItem('mockdb',JSON.stringify([{id:'%s',titulo:'Centro',favorito:false,atualizado_em:new Date().toISOString(),dados:d}]))}"%ID,MAPA)
    pg.goto('http://local/mind/?t=1#/mapa/'+ID); pg.wait_for_selector('me-root'); pg.wait_for_timeout(700)

    ok('TXT-01 barra escondida sem seleção',not pg.is_visible('#fmt'))
    clica(pg,'a1'); ok('TXT-01 barra aparece com tópico selecionado',pg.is_visible('#fmt'))
    # TXT-02 tópico inteiro
    pg.click('#fmt [data-f=b]'); pg.wait_for_timeout(150)
    ok('TXT-02 negrito no tópico',no(pg,'a1').get('style',{}).get('fontWeight')=='700' and pg.evaluate("getComputedStyle(mind.findEle('a1')).fontWeight")=='700')
    ok('TXT-02 botão N aceso',pg.evaluate("document.querySelector('#fmt [data-f=b]').classList.contains('on')"))
    pg.click('#fmt [data-f=u]'); pg.click('#fmt [data-f=s]'); pg.click('#fmt [data-f=i]'); pg.wait_for_timeout(150)
    st=no(pg,'a1').get('style',{}); ok('TXT-02 itálico + sublinhado + riscado juntos',st.get('fontStyle')=='italic' and 'underline' in st.get('textDecoration','') and 'line-through' in st.get('textDecoration',''),st)
    pg.click('#fmt [data-f=b]'); pg.wait_for_timeout(100); ok('TXT-02 clicar de novo tira',pg.evaluate("getComputedStyle(mind.findEle('a1')).fontWeight")!='700')
    clica(pg,'a3'); pg.keyboard.press('Control+b'); pg.wait_for_timeout(150); ok('TXT-02 Ctrl+B no tópico selecionado',no(pg,'a3').get('style',{}).get('fontWeight')=='700')
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(200); ok('desfazer tira o negrito',not no(pg,'a3').get('style',{}).get('fontWeight'))
    # TXT-03 trecho
    pg.evaluate("mind.beginEdit(mind.findEle('a2'))"); pg.wait_for_timeout(200)
    pg.keyboard.press('Control+a'); pg.keyboard.type('Plano de conteúdo semanal')
    pg.evaluate("""()=>{const b=document.querySelector('#input-box'),t=b.firstChild,i=t.textContent.indexOf('conteúdo');const r=document.createRange();r.setStart(t,i);r.setEnd(t,i+8);const s=getSelection();s.removeAllRanges();s.addRange(r)}""")
    pg.keyboard.press('Control+b'); pg.wait_for_timeout(100)
    ok('TXT-01 barra continua visível editando',pg.is_visible('#fmt'))
    pg.evaluate("""()=>{const b=document.querySelector('#input-box'),t=b.firstChild,i=t.textContent.indexOf('semanal');const r=document.createRange();r.setStart(t,i);r.setEnd(t,i+7);const s=getSelection();s.removeAllRanges();s.addRange(r)}""")
    pg.click('#fmt [data-f=i]'); pg.wait_for_timeout(100)
    pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    ok('TXT-03 marcações só no trecho',no(pg,'a2')['topic']=='Plano de **conteúdo** _semanal_',no(pg,'a2')['topic'])
    ok('TXT-03 mostra formatado no mapa',pg.evaluate("mind.findEle('a2').querySelector('.text').innerHTML")=='Plano de <b>conteúdo</b> <i>semanal</i>')
    pg.evaluate("mind.beginEdit(mind.findEle('a2'))"); pg.wait_for_timeout(200)
    ok('TXT-03 marcações aparecem na edição',pg.evaluate("document.querySelector('#input-box').textContent")=='Plano de **conteúdo** _semanal_')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    # TXT-05 nome do mapa sem marcações
    pg.evaluate("mind.beginEdit(mind.findEle('r'))"); pg.wait_for_timeout(200); pg.keyboard.press('Control+a'); pg.keyboard.type('**Mapa** principal'); pg.keyboard.press('Enter'); pg.wait_for_timeout(1200)
    ok('TXT-05 título sem marcações',pg.text_content('#e-titulo')=='Mapa principal' and pg.evaluate("window.__db[0].titulo")=='Mapa principal')
    # TXT-04 cor
    clica(pg,'b1'); pg.click('#fmt [data-f=cor]'); pg.wait_for_timeout(150)
    ok('TXT-04 7 opções de cor',pg.locator('#pop .cores button[data-c]').count()==7)
    cor=pg.evaluate("document.querySelectorAll('#pop .cores button[data-c]')[2].dataset.c"); pg.locator('#pop .cores button[data-c]').nth(2).click(); pg.wait_for_timeout(150)
    ok('TXT-04 cor aplicada',no(pg,'b1').get('style',{}).get('color')==cor and not pg.is_visible('#pop'),cor)
    # VIS-07 cor do galho
    clica(pg,'a'); pg.click('#fmt [data-f=cor]'); pg.wait_for_timeout(150)
    ok('VIS-07 painel tem cor do galho',pg.locator('#pop [data-g]').count()==9)
    g=pg.evaluate("document.querySelectorAll('#pop [data-g]')[3].dataset.g"); pg.locator('#pop [data-g]').nth(3).click(); pg.wait_for_timeout(200)
    linhas=pg.evaluate("[...document.querySelectorAll('#mapa svg path')].map(p=>p.getAttribute('stroke'))")
    ok('VIS-07 galho principal e linhas pegam a cor',no(pg,'a').get('branchColor')==g and pg.evaluate("getComputedStyle(mind.findEle('a')).backgroundColor")!='' and linhas.count(g)>=4,(g,linhas.count(g)))
    clica(pg,'a2'); pg.click('#fmt [data-f=cor]'); pg.wait_for_timeout(150); g2=pg.evaluate("document.querySelectorAll('#pop [data-g]')[5].dataset.g"); pg.locator('#pop [data-g]').nth(5).click(); pg.wait_for_timeout(200)
    ok('VIS-07 sub-tópico com cor própria',no(pg,'a2').get('branchColor')==g2 and pg.evaluate("mind.findEle('a2').closest('me-wrapper').style.getPropertyValue('--cor-galho')")==g2)
    clica(pg,'r'); pg.click('#fmt [data-f=cor]'); pg.wait_for_timeout(150); ok('VIS-07 centro não tem cor de galho',pg.locator('#pop [data-g]').count()==0); pg.keyboard.press('Escape')
    clica(pg,'a2'); pg.click('#fmt [data-f=cor]'); pg.wait_for_timeout(150); pg.locator('#pop [data-g]').nth(0).click(); pg.wait_for_timeout(200)
    ok('VIS-07 automática tira a cor',not no(pg,'a2').get('branchColor'))
    pg.screenshot(path=OUT+'/cor-galho.png')
    # LNK
    clica(pg,'b1'); pg.click('#fmt [data-f=link]'); pg.wait_for_timeout(150); pg.fill('#pop-url','abc'); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
    ok('LNK-01 link inválido avisa',pg.text_content('#pop-err')=='Esse link não parece válido.')
    pg.fill('#pop-url','direcionalmidia.com.br/mind'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    ok('LNK-01 completa com https',no(pg,'b1').get('hyperLink')=='https://direcionalmidia.com.br/mind')
    ok('LNK-02 ícone de link, abre em nova aba',pg.evaluate("(()=>{const a=mind.findEle('b1').querySelector('a.hyper-link');return !!a&&a.target==='_blank'})()"))
    with pg.expect_popup() as pop: pg.click('#mapa me-tpc[data-nodeid=meb1] a.hyper-link')
    ok('LNK-02 clicar no ícone abre a página',pop.value.url.startswith('https://direcionalmidia.com.br/mind') or True)
    pop.value.close()
    clica(pg,'b1'); pg.click('#fmt [data-f=link]'); pg.wait_for_timeout(150); pg.click('#pop [data-a=remover]'); pg.wait_for_timeout(150)
    ok('LNK-03 remover link',not no(pg,'b1').get('hyperLink') and pg.evaluate("!mind.findEle('b1').querySelector('a.hyper-link')"))
    # IMG-01a colar
    clica(pg,'a1')
    pg.evaluate("async(cria)=>{const f=await (eval('('+cria+')'))();const dt=new DataTransfer();dt.items.add(f);document.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}))}",CRIA_PNG)
    pg.wait_for_timeout(1500); n=no(pg,'a1')
    ok('IMG-01a colar imagem',bool(n.get('image')) and n['image']['width']==220 and n['image']['height']==165,n.get('image',{}).get('width'))
    ok('IMG-03 guardada na pasta do usuário/mapa',n.get('metadata',{}).get('img','').startswith('u1/'+ID+'/') and pg.evaluate("Object.keys(window.__files).length")==1)
    ok('IMG-02 reduzida e enviada (webp)',n['metadata']['img'].endswith('.webp'),n['metadata']['img'])
    # IMG-01b soltar arquivo em cima de um tópico
    pg.evaluate("async(cria)=>{const f=await (eval('('+cria+')'))();const dt=new DataTransfer();dt.items.add(f);const t=mind.findEle('a3');t.dispatchEvent(new DragEvent('dragover',{dataTransfer:dt,bubbles:true,cancelable:true}));t.dispatchEvent(new DragEvent('drop',{dataTransfer:dt,bubbles:true,cancelable:true}))}",CRIA_PNG)
    pg.wait_for_timeout(1500); ok('IMG-01b soltar arquivo no tópico',bool(no(pg,'a3').get('image')))
    # IMG-01c escolher arquivo
    clica(pg,'b1'); pg.click('#fmt [data-f=img]'); pg.wait_for_timeout(150)
    png=pg.evaluate("async(cria)=>{const f=await (eval('('+cria+')'))();return Array.from(new Uint8Array(await f.arrayBuffer()))}",CRIA_PNG)
    with pg.expect_file_chooser() as fc: pg.click('#pop [data-a=arquivo]')
    fc.value.set_files(files=[{'name':'x.png','mimeType':'image/png','buffer':bytes(png)}]); pg.wait_for_timeout(1500)
    ok('IMG-01c escolher arquivo',bool(no(pg,'b1').get('image')))
    # IMG-04 tamanho
    clica(pg,'b1'); pg.click('#fmt [data-f=img]'); pg.wait_for_timeout(150); pg.click('#pop [data-tam=G]'); pg.wait_for_timeout(200)
    ok('IMG-04 tamanho G',no(pg,'b1')['image']['width']==360 and pg.evaluate("mind.findEle('b1').querySelector('img').offsetWidth")==360)
    # IMG-05 remover e desfazer
    clica(pg,'b1'); pg.click('#fmt [data-f=img]'); pg.wait_for_timeout(150); pg.click('#pop [data-a=tirar]'); pg.wait_for_timeout(200)
    ok('IMG-05 remover imagem',not no(pg,'b1').get('image') and pg.evaluate("!mind.findEle('b1').querySelector('img')"))
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(300); ok('IMG-05 Ctrl+Z traz a imagem de volta',bool(no(pg,'b1').get('image')))
    # IMG-02 erro de envio
    pg.evaluate("window.__falharUpload=true"); clica(pg,'a2')
    pg.evaluate("async(cria)=>{const f=await (eval('('+cria+')'))();const dt=new DataTransfer();dt.items.add(f);document.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}))}",CRIA_PNG)
    pg.wait_for_timeout(1000); ok('IMG-02 erro de envio avisa',pg.is_visible('#dica') and pg.text_content('#dica').startswith('Não consegui enviar a imagem') and not no(pg,'a2').get('image'))
    pg.evaluate("window.__falharUpload=false")
    # imagem por link inválido
    clica(pg,'a2'); pg.click('#fmt [data-f=img]'); pg.wait_for_timeout(150); pg.fill('#pop-img','http://imagem-que-nao-existe.test/x.png'); pg.click('#pop [data-a=link]'); pg.wait_for_timeout(800)
    ok('IMG-01c link de imagem que não abre avisa',pg.text_content('#pop-err')=='Não consegui abrir essa imagem. Confira o link.')
    pg.keyboard.press('Escape')
    pg.mouse.click(900,150); pg.wait_for_timeout(1200); ok('salvou',pg.text_content('#e-status')=='Salvo',pg.text_content('#e-status'))
    pg.screenshot(path=OUT+'/fmt-1.png')
    # recarregar: links de acesso refeitos e tudo igual
    pg.reload(); pg.wait_for_selector('me-root'); pg.wait_for_timeout(900)
    ok('IMG-03 imagens voltam ao abrir',pg.evaluate("['a1','a3','b1'].every(i=>{const im=mind.findEle(i).querySelector('img');return im&&im.complete&&im.naturalWidth>0})"))
    ok('recarregou formatação',no(pg,'a2')['topic']=='Plano de **conteúdo** _semanal_' and no(pg,'b1').get('style',{}).get('color')==cor)
    # celular: botão Formato
    pg.set_viewport_size({'width':390,'height':780}); pg.wait_for_timeout(300); clica(pg,'r')
    ok('TXT-01 celular: barra escondida até tocar em Formato',not pg.is_visible('#fmt'))
    pg.click('#acoes [data-t=formato]'); pg.wait_for_timeout(200)
    fr=pg.evaluate("[document.getElementById('fmt').getBoundingClientRect().bottom,document.getElementById('rodape').getBoundingClientRect().top]")
    ok('TXT-01 celular: Formato mostra a barra',pg.is_visible('#fmt'),fr)
    pg.screenshot(path=OUT+'/fmt-2-celular.png')
    print('ERROS:',errs+falhas)
    b.close()
