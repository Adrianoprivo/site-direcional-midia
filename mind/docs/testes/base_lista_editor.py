import sys, os, time
from playwright.sync_api import sync_playwright
SITE=sys.argv[1]; PKG=sys.argv[2]; OUT=sys.argv[3]
MOCK=open(os.path.join(os.path.dirname(__file__),'mock-supabase.js')).read()
erros=[]
def rotas(route):
    u=route.request.url
    if 'supabase-js' in u: return route.fulfill(body=MOCK,content_type='application/javascript')
    if 'MindElixir.iife.js' in u: return route.fulfill(path=PKG+'/dist/MindElixir.iife.js',content_type='application/javascript')
    if 'MindElixir.css' in u: return route.fulfill(path=PKG+'/dist/MindElixir.css',content_type='text/css')
    if u.startswith('http://local/'): 
        p=SITE+u[len('http://local'):].split('#')[0].split('?')[0]
        if p.endswith('/'): p+='index.html'
        import mimetypes; return route.fulfill(path=p,content_type=mimetypes.guess_type(p)[0] or 'text/html')
    return route.abort()
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(viewport={'width':1280,'height':800})
    pg.on('pageerror',lambda e:erros.append(str(e)))
    pg.on('console',lambda m: erros.append('console:'+m.text) if m.type=='error' else None)
    pg.route('**/*',rotas)
    pg.goto('http://local/mind/')
    pg.wait_for_selector('#lg-form',state='visible'); pg.screenshot(path=OUT+'/1-login.png')
    pg.fill('#lg-email','a@b.com'); pg.fill('#lg-pass','errada'); pg.click('#lg-btn'); pg.wait_for_timeout(300)
    print('erro senha:',pg.text_content('#lg-msg'))
    pg.fill('#lg-pass','certa'); pg.click('#lg-btn'); pg.wait_for_selector('#lista',state='visible')
    pg.screenshot(path=OUT+'/2-lista-vazia.png')
    pg.click('#novo'); pg.wait_for_timeout(1500); print('ERR-ANTES:',erros, pg.evaluate('location.hash')); pg.wait_for_selector('#editor',state='visible'); pg.wait_for_selector('me-root, .map-container me-tpc',timeout=8000)
    pg.wait_for_timeout(500)
    # digita: seleciona raiz, renomeia, cria filhos
    root=pg.locator('me-root me-tpc').first
    root.dblclick(); pg.wait_for_timeout(300); pg.keyboard.press('Control+a'); pg.keyboard.type('Plano PrivoMind'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    root.click(); pg.keyboard.press('Tab'); pg.wait_for_timeout(200); pg.keyboard.type('Fase 1'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    pg.keyboard.press('Enter'); pg.wait_for_timeout(200); pg.keyboard.type('Fase 2'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    pg.keyboard.press('Tab'); pg.wait_for_timeout(200); pg.keyboard.type('Exportar PDF'); pg.keyboard.press('Enter')
    pg.wait_for_timeout(1500)
    print('status:',pg.text_content('#e-status'),'| titulo:',pg.text_content('#e-titulo'),'| updates:',pg.evaluate('window.__updates'))
    pg.screenshot(path=OUT+'/3-editor.png')
    pg.click('#e-ajuda'); pg.screenshot(path=OUT+'/4-ajuda.png'); pg.click('#e-ajuda')
    # recarrega e confere que salvou
    pg.reload(); pg.wait_for_selector('me-root',timeout=8000); pg.wait_for_timeout(500)
    topicos=pg.eval_on_selector_all('me-tpc','els=>els.map(e=>e.textContent.trim())')
    print('apos recarregar:',topicos)
    pg.click('#voltar'); pg.wait_for_selector('#lista',state='visible'); pg.wait_for_timeout(800)
    print('lista:',pg.text_content('#mapas'), pg.evaluate('[location.hash, mapas.length, document.getElementById("mapas").innerHTML.length, document.getElementById("busca").value]'))
    pg.click('button[data-a=fav]'); pg.wait_for_timeout(300)
    pg.fill('#busca','plano'); pg.wait_for_timeout(200); pg.screenshot(path=OUT+'/5-lista.png')
    pg.fill('#busca','xyz'); pg.wait_for_timeout(100); print('busca vazia:',pg.text_content('#mapas'))
    pg.fill('#busca','')
    # celular
    pg.set_viewport_size({'width':390,'height':800}); pg.screenshot(path=OUT+'/6-lista-celular.png')
    pg.click('button[data-a=abrir]'); pg.wait_for_selector('me-root'); pg.wait_for_timeout(600); pg.screenshot(path=OUT+'/7-editor-celular.png')
    pg.click('#voltar'); pg.wait_for_selector('#lista',state='visible')
    pg.click('button[data-a=del]'); pg.wait_for_timeout(300)
    print('depois de apagar:',pg.text_content('#mapas')[:60], '| db (vai pra lixeira, continua no banco):',pg.evaluate('window.__db.length'),pg.evaluate('!!window.__db[0].excluido_em'))
    pg.goto('http://local/mind/#/lixeira'); pg.wait_for_timeout(500); pg.once('dialog',lambda d:d.accept()); pg.click('button[data-a=del-forever]'); pg.wait_for_timeout(300)
    print('depois de apagar para sempre | db:',pg.evaluate('window.__db.length'))
    pg.goto('http://local/mind/#/')
    # tema escuro
    pg.emulate_media(color_scheme='dark'); pg.set_viewport_size({'width':1280,'height':800}); pg.click('#novo'); pg.wait_for_selector('me-root'); pg.wait_for_timeout(600); pg.screenshot(path=OUT+'/8-editor-escuro.png')
    print('ERROS:',erros)
    b.close()
