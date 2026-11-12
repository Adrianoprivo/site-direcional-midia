# Publicar Reels no Instagram pelo banco (sem navegador)

Criado em 12/11/2026. Serve quando a sessão do Claude **não** tem o computador do Adriano conectado e a rede da sessão não alcança o Supabase.
O token do Instagram nunca sai do banco. As funções só rodam com `service_role` (anon e authenticated não executam).

## Pré-requisitos
- Conexão do Instagram ativa em `ig_conexoes` (1 conta). Token vale 60 dias; renova quando a aba do Privo Post é aberta depois de ~13/12/2026 (vence em 02/01/2027).
- Vídeo MP4 vertical 9:16 hospedado em link https público (ex.: `https://raw.githubusercontent.com/Adrianoprivo/site-direcional-midia/main/ig/posts/<pasta>/reel.mp4`).
- Aprovação do Adriano ("pode postar") — vira `p_autorizado = true`.

## Passos (via Supabase `execute_sql`, projeto "central de projetos")
1. Criar o contêiner: `select public.privo_ig_criar_reels('<link do mp4>', '<legenda>', true);` -> devolve `request_id`.
2. Ler a resposta (espere ~4 s): `select content::text from net._http_response where id = <request_id>;` -> `{"id":"<container>"}`.
3. Conferir o vídeo: `select public.privo_ig_status('<container>');` e ler a resposta do mesmo jeito. Repita a cada ~15 s até `FINISHED` (leva de 20 s a 1 min).
4. Publicar UMA vez: `select public.privo_ig_publicar('<container>', true);` -> resposta `{"id":"<media_id>"}`. **Não repita** (posta em dobro). Se der dúvida, olhe o perfil antes.
5. Link do post: `select public.privo_ig_link('<media_id>');` e ler a resposta (`permalink`, `timestamp` em UTC; São Paulo = UTC-3).
6. Lançar no Registro da planilha (com o "ok" do Adriano).

Cada `execute_sql` com várias instruções devolve só o resultado da última: rode o `select` da resposta numa chamada separada.

## Limites
- Só Reels pelo banco (fotos/carrossel continuam pelo Privo Post ou pela chave do `ig-api`).
- O Supabase precisa estar conectado na sessão do Claude. Se o sistema pedir permissão para a ação no banco, o Adriano aprova.
- Correção definitiva alternativa: liberar `ftahvdzbyqnvarukytws.supabase.co` na rede do Claude (Admin > Capabilities) e cadastrar o segredo `PRIVO_CHAVE_PUBLICAR` no Supabase (porta com chave já está no `ig-api`).
