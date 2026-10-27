-- Privo Post fase 1: conexão com o Google (CON-01..06). Só as Edge Functions (chave de serviço) acessam.
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
create index gbp_oauth_estados_user_idx on public.gbp_oauth_estados(user_id);

alter table public.gbp_conexoes      enable row level security;
alter table public.gbp_oauth_estados enable row level security;
-- Sem regras de acesso de propósito + sem permissão para os papéis da página.
revoke all on public.gbp_conexoes      from anon, authenticated;
revoke all on public.gbp_oauth_estados from anon, authenticated;
