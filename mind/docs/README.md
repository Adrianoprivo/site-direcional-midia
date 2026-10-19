# PrivoMind — documentos do projeto

Mapa mental próprio do Adriano, em `direcionalmidia.com.br/mind`, inspirado nas funções do MindMeister (sem copiar código, marca ou textos).

| Arquivo | O que é |
| --- | --- |
| `recon.md` | Mapeamento do MindMeister: telas, fluxos, dados, o que não copiar |
| `features.csv` | Lista de funções com prioridade (must / should / could / skip) e o que já foi feito |
| `architecture.md` | Plano técnico: como encaixa no site, banco, fases |

## Como funciona
- Página única `mind/index.html` (mesmo molde da Privo Central).
- Login: Supabase Auth do projeto "central de projetos" (mesma conta da Central).
- Dados: tabela `public.mapas` (um registro por mapa, mapa inteiro em `dados`), protegida por usuário (RLS).
- Editor: biblioteca Mind Elixir 5.15.1 (MIT), carregada por CDN.

## Status
- Fase 1 (login, lista, editor pelo teclado e toque, salvar sozinho, exportar PNG): construída em 2026-10-19 na branch `privomind`.
