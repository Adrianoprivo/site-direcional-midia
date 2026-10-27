-- Privo Post: conexão com o Instagram (API com login do Instagram). Só as Edge Functions acessam.
create table public.ig_conexoes (
  user_id        uuid primary key references auth.users(id) on delete cascade,
  ig_user_id     text not null,
  username       text,
  access_token   text not null,   -- token de longa duração (60 dias)
  obtido_em      timestamptz not null default now(),
  expira_em      timestamptz,
  permissoes     text,
  criado_em      timestamptz not null default now(),
  atualizado_em  timestamptz not null default now()
);

create table public.ig_oauth_estados (
  estado     text primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  expira_em  timestamptz not null,
  usado_em   timestamptz
);
create index ig_oauth_estados_user_idx on public.ig_oauth_estados(user_id);

alter table public.ig_conexoes      enable row level security;
alter table public.ig_oauth_estados enable row level security;
revoke all on public.ig_conexoes      from anon, authenticated;
revoke all on public.ig_oauth_estados from anon, authenticated;
