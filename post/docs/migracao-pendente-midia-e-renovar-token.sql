-- PENDENTE (12/11/2026): ainda NÃO aplicada. Projeto Supabase "central de projetos" (ftahvdzbyqnvarukytws).
-- 1) foto/carrossel pelo banco  2) renovação automática do token do Instagram. Só adiciona; não altera nada existente.
create or replace function public.privo_ig_criar_midia(p_campos jsonb, p_autorizado boolean)
returns bigint language plpgsql security definer set search_path = public, extensions, net as $$
declare k text; rid bigint;
begin
  if p_autorizado is not true then raise exception 'Confirme a prévia antes de publicar.'; end if;
  for k in select jsonb_object_keys(p_campos) loop
    if k not in ('media_type','image_url','video_url','caption','is_carousel_item','children','share_to_feed') then
      raise exception 'Campo não permitido: %', k;
    end if;
  end loop;
  if p_campos ? 'image_url' and (p_campos->>'image_url') !~ '^https://[^[:space:]]+$' then raise exception 'image_url precisa ser link https.'; end if;
  if p_campos ? 'video_url' and (p_campos->>'video_url') !~ '^https://[^[:space:]]+$' then raise exception 'video_url precisa ser link https.'; end if;
  if length(coalesce(p_campos->>'caption','')) > 2200 then raise exception 'A legenda passa de 2.200 caracteres.'; end if;
  select net.http_post(
    url := 'https://graph.instagram.com/me/media',
    headers := '{"Content-Type":"application/json"}'::jsonb,
    body := p_campos || jsonb_build_object('access_token', public.privo_ig_token()),
    timeout_milliseconds := 30000) into rid;
  return rid;
end $$;

create table if not exists public.ig_renovacao (request_id bigint primary key, criado timestamptz not null default now());
alter table public.ig_renovacao enable row level security;
revoke all on public.ig_renovacao from anon, authenticated;

create or replace function public.privo_ig_renovar_iniciar(p_forcar boolean default false)
returns bigint language plpgsql security definer set search_path = public, extensions, net as $$
declare c record; rid bigint;
begin
  select * into c from public.ig_conexoes limit 1;
  if c.user_id is null then return null; end if;
  if c.expira_em <= now() then return null; end if;
  if c.obtido_em > now() - interval '24 hours' then return null; end if;
  if not p_forcar and c.expira_em > now() + interval '30 days' then return null; end if;
  select net.http_get(url := 'https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=' || c.access_token) into rid;
  insert into public.ig_renovacao(request_id) values (rid);
  return rid;
end $$;

create or replace function public.privo_ig_renovar_aplicar()
returns int language plpgsql security definer set search_path = public, extensions, net as $$
declare r record; resp record; n int := 0; novo text; seg numeric;
begin
  for r in select request_id from public.ig_renovacao loop
    select * into resp from net._http_response where id = r.request_id;
    if resp.id is null then continue; end if;
    novo := resp.content::jsonb->>'access_token';
    seg  := (resp.content::jsonb->>'expires_in')::numeric;
    if resp.status_code = 200 and novo is not null and seg > 0 then
      update public.ig_conexoes set access_token = novo, obtido_em = now(),
        expira_em = now() + make_interval(secs => seg), atualizado_em = now();
      n := n + 1;
    end if;
    delete from public.ig_renovacao where request_id = r.request_id;
  end loop;
  return n;
end $$;

revoke all on function public.privo_ig_criar_midia(jsonb,boolean) from public, anon, authenticated;
revoke all on function public.privo_ig_renovar_iniciar(boolean) from public, anon, authenticated;
revoke all on function public.privo_ig_renovar_aplicar() from public, anon, authenticated;
grant execute on function public.privo_ig_criar_midia(jsonb,boolean) to service_role;
grant execute on function public.privo_ig_renovar_iniciar(boolean) to service_role;
grant execute on function public.privo_ig_renovar_aplicar() to service_role;
