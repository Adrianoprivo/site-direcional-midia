<!-- Guia oficial de publicação (16/11/2026). Também instalado como skill "publicar-instagram". -->

# Publicar no Instagram pelo Privo Post

Português do Brasil, simples e curto.

## Regra principal
- O Instagram @oadriano_souza publica **só pelo Privo Post** (direcionalmidia.com.br/post), que é a API própria da Direcional Mídia.
- **Nunca use o Windsor para publicar nem para procurar o Instagram.** O Windsor saiu do Privo Post no fim de outubro de 2026 e não tem mais o Instagram do Adriano. Se uma ferramenta do Windsor aparecer, ignore para Instagram.
- Só publique depois do "ok" do Adriano para aquele post ("pode postar", "ok publica"). Esse ok vale para um post só.
- Publique **uma vez**. Se não souber se saiu, confira o perfil antes de tentar de novo, para não postar em dobro.

## Arquivos
- As artes ficam no GitHub `Adrianoprivo/site-direcional-midia`, em `ig/posts/<pasta>/`, na branch `main`.
- O Instagram precisa do link **direto** de cada arquivo, não do link da pasta. Formato:
  `https://raw.githubusercontent.com/Adrianoprivo/site-direcional-midia/main/ig/posts/<pasta>/slide-01.jpg`
- Se o Adriano mandar o link da pasta (`github.com/.../tree/main/...`), liste os arquivos (API pública: `https://api.github.com/repos/Adrianoprivo/site-direcional-midia/contents/ig/posts/<pasta>?ref=main`) e use o `download_url` de cada um, em ordem.
- Feed e carrossel: JPG 1080x1350 (4:5), de 1 a 10 imagens. Reels: MP4 vertical 9:16. Stories: imagem ou vídeo 9:16 (1080x1920); Stories não levam legenda.

## Caminho A: sessão no computador do Adriano (app do Claude com o navegador)
1. Abra `https://direcionalmidia.com.br/post/` no navegador do app. Se pedir login, peça para o Adriano entrar (nunca digite a senha).
2. Rode na página, **sem esperar a resposta** (a publicação pode levar mais de 45 s):
   `window.__pubR=null; sb.functions.invoke('ig-api',{body:{acao:'publicar', imagens:[...links...], legenda:'...', autorizado:true}}).then(r=>window.__pubR=r)`
   - Reels: troque `imagens` por `video:'link.mp4'`.
   - Stories: adicione `stories:true` e não mande legenda (cada imagem vira um story, na ordem; ou 1 vídeo).
3. Leia `window.__pubR` a cada ~20 s até chegar. Sucesso: `data.publicado === true` (com `id` e `link`). Erro: leia `await window.__pubR.error.context.json()`.
4. Nunca reenvie enquanto não tiver a resposta.

## Caminho B: nuvem ou claude.ai (sem o computador do Adriano)
Use o conector **Supabase**, projeto "central de projetos" (`ftahvdzbyqnvarukytws`), com `execute_sql`. O token do Instagram fica no banco; nunca o leia nem o mostre.
Cada função devolve um `request_id`. Espere ~4 s e leia a resposta numa chamada separada:
`select status_code, content::text from net._http_response where id = <request_id>;`

1. Criar o contêiner: `select public.privo_ig_criar_midia('<json>'::jsonb, true);`
   - Foto única: `{"image_url":"<link>","caption":"<legenda>"}`
   - Carrossel: um por imagem `{"image_url":"<link>","is_carousel_item":"true"}`; depois `{"media_type":"CAROUSEL","children":"<id1>,<id2>,...","caption":"<legenda>"}`
   - Stories: um por story `{"media_type":"STORIES","image_url":"<link>"}` (ou `"video_url"`)
   - Reels: `{"media_type":"REELS","video_url":"<link>","caption":"<legenda>","share_to_feed":"true"}` (ou `select public.privo_ig_criar_reels('<link>','<legenda>',true);`)
   - Escape aspas simples da legenda dobrando (`'` vira `''`).
2. Conferir: `select public.privo_ig_status('<container>');` e ler a resposta até `"status_code":"FINISHED"` (fotos: segundos; vídeo: até 1 min). Carrossel: confira cada imagem antes de criar o CAROUSEL, e o CAROUSEL antes de publicar.
3. Publicar **uma vez** por contêiner final: `select public.privo_ig_publicar('<container>', true);` e ler a resposta `{"id":"<media_id>"}`. Stories: publique um por vez, na ordem.
4. Link: `select public.privo_ig_link('<media_id>');` e ler `permalink` e `timestamp` (UTC; São Paulo = UTC-3).

Se o conector Supabase não estiver disponível na sessão: **não use o Windsor**. Diga ao Adriano que o conector do Supabase não carregou e mande os links diretos das artes e a legenda, para ele publicar na aba Publicar do Privo Post (ou para tentar de novo numa sessão no computador dele).

## Depois de publicar
- Mande ao Adriano o link do post.
- Lance a linha no Registro da planilha "Controle de Posts — Instagram @oadriano_souza" (id 10D6zXXrodhpAH6I5ZljSNISLz5mgKgebjhveu4UhdMg), com o ok dele.
