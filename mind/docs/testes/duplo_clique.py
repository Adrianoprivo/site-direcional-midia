import sys,os
from playwright.sync_api import sync_playwright
exec(open(os.path.join(os.path.dirname(__file__),'base_lista_editor.py')).read().split('with sync_playwright')[0])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); pg.route('**/*',rotas)
    pg.goto('http://local/mind/'); pg.fill('#lg-email','a@b.com'); pg.fill('#lg-pass','certa'); pg.click('#lg-btn'); pg.wait_for_selector('#lista',state='visible')
    pg.click('#novo'); pg.wait_for_selector('me-root'); pg.wait_for_timeout(800)
    res=[]
    for i in range(4):
        root=pg.locator('me-root me-tpc').first
        root.dblclick(); pg.wait_for_timeout(300)
        ok=pg.evaluate("!!document.querySelector('#input-box')")
        res.append(ok)
        if ok: pg.keyboard.press('Control+a'); pg.keyboard.type('T%d'%i); pg.keyboard.press('Enter')
        else: pg.keyboard.press('Escape')
        pg.wait_for_timeout(1200)
    print(res, pg.text_content('#e-titulo'))
    b.close()
