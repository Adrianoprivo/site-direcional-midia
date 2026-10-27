# Privo Post — Arquitetura

Data: 2026-10-27 · Base: [spec.md](spec.md), [recon.md](recon.md), leitura do repositório `site-direcional-midia` e do Supabase "central de projetos" · Status: aprovada em 27/10/2026; tabelas e funções criadas no Supabase

## Peças

| Peça | Onde | O que faz |
| --- | --- | --- |
| Página | `post/index.html` no site (nginx estático, EasyPanel publica a `main`) | Login, botão Conectar, lista de perfis. Usa a biblioteca do Supabase por CDN, igual à Central e ao PrivoMind. |
| Login | Supabase Auth, projeto `ftahvdzbyqnvarukytws` | Mesma conta do Adriano. |
| `gbp-oauth-start` | Edge Function (exige login) | Cria o código de proteção (CON-04) e devolve o endereço da tela de permissão do Google. |
| `gbp-oauth-callback` | Edge Function (pública, é o Google que chama) | Confere o código, troca a autorização por tokens, guarda e volta para `/post`. |
| `gbp-api` | Edge Function (exige login) | `status`, `perfis` (lista contas e perfis), `desconectar`. Renova o acesso quando vence. |
| Segredos | Supabase → Edge Functions → Secrets | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`. O Adriano cola a chave secreta direto no painel. |

## Fluxo de conexão

1. Página chama `gbp-oauth-start` com o login do Supabase.
2. Função grava um código aleatório em `gbp_oauth_estados` (vale 10 min) e devolve o endereço do Google com `access_type=offline`, `prompt=consent`, escopos `https://www.googleapis.com/auth/business.manage openid email` (openid/email só para mostrar com qual conta conectou).
3. Adriano clica em "Permitir" no Google.
4. Google chama `gbp-oauth-callback?code=…&state=…`.
5. Função confere o código (existe, não venceu, não foi usado), troca por tokens em `oauth2.googleapis.com/token`, lê o e-mail da conta e grava em `gbp_conexoes`.
6. Redireciona para `https://direcionalmidia.com.br/post?google=conectado` (ou `?google=erro`).

**URL de retorno a cadastrar no cliente OAuth "Privo Post Web":**
`https://ftahvdzbyqnvarukytws.supabase.co/functions/v1/gbp-oauth-callback`
(a cadastrada antes, `direcionalmidia.com.br/post/oauth/callback`, sai.)

## Banco (tabelas novas)

```sql
create table public.gbp_conexoes (
  user_id        uuid primary key references auth.users(id) on delete cascade,
  google_email   text not null,
  refresh_token  text not null,
  access_token   text,
  expira_em      timestamptz,
  escopos        text,
  criado_em      timestamptz not null default now(),
  atualizado_em  timestamptz not null default now()
);

create table public.gbp_oauth_estados (
  estado     text primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  expira_em  timestamptz not null,
  usado_em   timestamptz
);

alter table public.gbp_conexoes      enable row level security;
alter table public.gbp_oauth_estados enable row level security;
-- Sem nenhuma regra de acesso: a página não lê nem grava essas tabelas.
-- Só as funções (chave de serviço) mexem nelas. Tokens nunca chegam ao navegador.
```

## Código

- Funções: `post/supabase/functions/` (`_shared/comum.ts` + uma pasta por função). `gbp-oauth-callback` sobe com `verify_jwt = false`; as outras com `true`.
- Banco: `post/supabase/migrations/20261027_privo_post_conexao_google.sql`.

## Chamadas ao Google (fase 1, só leitura)

- Contas: `GET https://mybusinessaccountmanagement.googleapis.com/v1/accounts`
- Perfis: `GET https://mybusinessbusinessinformation.googleapis.com/v1/{conta}/locations?readMask=name,title,storefrontAddress`
- Desconectar: `POST https://oauth2.googleapis.com/revoke?token=…`

## Testes antes de publicar

- Funções: chamada sem login → recusada; código de proteção vencido/repetido → recusado; tokens nunca aparecem na resposta.
- Página: login, conectar, cancelar no Google, lista de perfis, desconectar, no PC e no celular.
- Advisors de segurança do Supabase sem alerta novo.
