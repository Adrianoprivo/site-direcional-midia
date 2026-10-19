# Plano técnico: PrivoMind (direcionalmidia.com.br/mind)

Data: 2026-10-19 · Base: recon.md + leitura do repositório `site-direcional-midia` + Supabase "central de projetos"

## Como o site funciona hoje (conferido)

| Peça | Como está |
| --- | --- |
| Hospedagem | Site estático num container **nginx**, publicado pelo **EasyPanel** na VPS |
| Publicação | Cada alteração na branch `main` do GitHub vai pro ar sozinha |
| Central | Um único arquivo `central/index.html` → vira `direcionalmidia.com.br/central` |
| Login | Supabase Auth (e-mail + senha), mesma conta do Adriano |
| Banco | Projeto Supabase "central de projetos", tabela `docs` com proteção por usuário (RLS) ligada |
| Visual | Cores em variáveis, modo claro e escuro |

## Decisões

1. **Mesmo molde da Central.** Pasta nova `mind/` com um `index.html`. Sem servidor novo, sem build, sem custo.
2. **Mesmo login.** Mesmo projeto Supabase. Quem entra na Central entra no PrivoMind com a mesma senha.
3. **Tabela própria `mapas`** (não usar a `docs` da Central). Motivo: a Central carrega **tudo** da `docs` ao abrir; mapas grandes iam deixar a Central lenta.
4. **Editor: biblioteca Mind Elixir** (licença MIT, carregada por CDN como o Supabase). Já traz teclado, arrastar, recolher, desfazer, temas, exportar imagem.
5. **Visual próprio**, com as mesmas variáveis de cor da Central (família "Privo"). Nada da marca do MindMeister.

## Banco de dados

```sql
create table public.mapas (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null default auth.uid() references auth.users(id) on delete cascade,
  titulo      text not null default 'Novo mapa',
  dados       jsonb not null,            -- o mapa inteiro (formato Mind Elixir)
  favorito    boolean not null default false,
  criado_em   timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);
alter table public.mapas enable row level security;
create policy "dono vê e mexe" on public.mapas
  for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create index on public.mapas (user_id, atualizado_em desc);
```

Compartilhar com outra pessoa (fase 3): tabela `mapas_acesso (mapa_id, email, nivel)` + regra extra. Fica pra depois.

## Telas da fase 1

| ID | Tela | O que tem |
| --- | --- | --- |
| P01 | Login | e-mail + senha (mesmo da Central) |
| P02 | Meus mapas | lista com busca, favoritos, criar, renomear, apagar (com confirmação) |
| P03 | Editor | mapa na tela toda, teclado (Enter/Tab/Del), arrastar, recolher, zoom, desfazer, salvar sozinho, botão voltar |

## Ordem de construção

| Fase | Entrega | Pronto quando |
| --- | --- | --- |
| **1A** | Tabela `mapas` criada + login + lista de mapas | consigo criar e ver mapas vazios |
| **1B** | Editor funcionando + salvar sozinho | crio um mapa, fecho, abro e está igual |
| **1C** | Publicar em `/mind` + testar no celular | uso de verdade por 3 dias |
| 2 | Cor/ícone/nota/link no tópico, modo Esboço, exportar PNG/PDF, tema escuro | — |
| 3 | Apresentação, compartilhar com outra pessoa, histórico | — |

## Pontos de atenção

- **Teste antes de publicar:** como tudo que entra na `main` vai pro ar, o PrivoMind nasce numa branch separada e só entra na `main` depois de testado.
- **Segurança (já existente):** o Supabase avisa que a proteção contra senhas vazadas está desligada. Ligar leva 1 minuto no painel.
- **Repositório público:** a chave que aparece no código é a pública (feita pra ficar no navegador). Ok **desde que** toda tabela tenha RLS, como a `mapas` acima.
