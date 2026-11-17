-- IG-PUB-07 (17/11/2026): enviar foto/vídeo do computador na aba Publicar.
-- O Instagram baixa a mídia por link público https, então o bucket é público para leitura.
-- Só quem tem o Instagram conectado (ig_conexoes) envia ou apaga, e só na própria pasta (<uid>/...).
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('privo-midia', 'privo-midia', true, 52428800, array['image/jpeg', 'video/mp4', 'video/quicktime'])
on conflict (id) do update set public = excluded.public, file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

-- ig_conexoes não é legível por "authenticated"; esta função só responde se QUEM CHAMA tem Instagram conectado.
create or replace function public.privo_tem_instagram()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.ig_conexoes c where c.user_id = auth.uid());
$$;
revoke all on function public.privo_tem_instagram() from public, anon;
grant execute on function public.privo_tem_instagram() to authenticated;

create policy "privo_midia_enviar" on storage.objects for insert to authenticated
  with check (
    bucket_id = 'privo-midia'
    and (storage.foldername(name))[1] = (select auth.uid())::text
    and (select public.privo_tem_instagram())
  );

create policy "privo_midia_apagar" on storage.objects for delete to authenticated
  using (
    bucket_id = 'privo-midia'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

-- Para o upsert/remoção pela biblioteca do Supabase (ler só a própria pasta).
create policy "privo_midia_ler_propria" on storage.objects for select to authenticated
  using (
    bucket_id = 'privo-midia'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
