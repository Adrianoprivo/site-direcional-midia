# Mapa de reconhecimento: Postproxy → Privo Post

Recorte: publicar e agendar posts no **Perfil da Empresa no Google** (fase 1). Redes sociais ficam pra depois.
Para: uso próprio da Direcional Mídia (clientes de GMN); lá na frente, talvez produto barato.
Data: 2026-10-23
Status: **v1, só fontes públicas.** Falta abrir o painel do Postproxy (conta grátis) para conferir telas.

## Fontes

| # | fonte | URL | o que deu |
| --- | --- | --- | --- |
| 1 | preços oficiais | https://postproxy.dev/pricing/ | planos, limites, plataformas, o que cobra |
| 2 | comparativos oficiais | https://postproxy.dev/compare/ | concorrentes diretos (Ayrshare etc.) |
| 3 | guia de acesso à API do Google (de um concorrente, Upload-Post) | https://www.upload-post.com/google-business-profile-api/ | como pedir acesso, requisitos, endpoints |
| 4 | documentação oficial do Google | https://developers.google.com/my-business/reference/rest/v4/accounts.locations.localPosts/create | criar post (localPosts.create) |

## O coração do app (core loop)

Conectar o perfil uma vez (login do Google, OAuth) → escrever o post (texto, foto, botão) → publicar agora ou agendar → ver se foi ao ar → responder avaliações.

## Como o Postproxy ganha dinheiro (fonte 1, conferido em 2026-10-23)

| Plano | Preço | O que libera |
| --- | --- | --- |
| Grátis | US$ 0 | até 10 posts/mês |
| Agentic | US$ 17/mês | 5 perfis, posts ilimitados; perfil extra US$ 1 a 4 |
| Business | US$ 49/mês | 20 "grupos de perfis" (1 marca/cliente cada), até 11 redes por grupo |
| Enterprise | sob consulta | volume, SLA |

Leitura: ele **cobra por perfil conectado**. A API do Google por trás é a mesma que nós podemos usar. O valor que ele vende é: já ter o acesso aprovado, a fila de agendamento, o painel, os logs e 11 redes num lugar só.

## O que ele faz (fonte 1)

- Publicar, agendar, filas (horários fixos), importar posts antigos, logs de publicação
- Comentários, DMs, respostas, **avaliações do Google**
- Métricas de post e de perfil
- API + SDKs + webhooks + MCP (é por isso que o Claude consegue usar)
- Equipe/workspaces, 2FA

## Como funciona por trás (fontes 3 e 4)

- **API oficial do Google Business Profile.** O guia da fonte 3 não fala em cobrança do Google; confirmar na documentação oficial.
- Base: `https://mybusiness.googleapis.com/v4`
  - criar post: `POST accounts/{conta}/locations/{local}/localPosts` (texto até 1.500, foto por URL pública, botão)
  - editar/apagar post: `PATCH` / `DELETE` no post
  - avaliações: `GET .../reviews`; responder: `PUT .../reviews/{id}/reply`
- Login: OAuth com o escopo `business.manage` (o dono do perfil autoriza uma vez)

## ⚠️ Barreira de entrada (o que mais pesa)

O Google **não libera a API pra qualquer um**. Precisa (fonte 3):
1. Projeto no Google Cloud
2. Formulário "Application for Basic API Access" com o número do projeto
3. **Perfil verificado e ativo há 60+ dias**, com **site cadastrado**, pedido feito pelo e-mail de dono/gerente
4. Aprovado = cota de 300 consultas/min (0 = negado). Prazo de análise não informado.

→ Primeira ação real do projeto: conferir se o perfil "Adriano Souza | Direcional Mídia" já tem 60 dias verificado e fazer o pedido.

## Telas do Privo Post (fase 1, proposta)

| ID | tela | pra que serve |
| --- | --- | --- |
| P01 | Login | mesmo login da Privo Central / PrivoMind |
| P02 | Perfis conectados | botão "Conectar Google", lista de perfis (meu + clientes) |
| P03 | Novo post | texto (contador 1.500), foto, botão (Saiba mais/Ligar/WhatsApp), perfil, publicar agora ou agendar |
| P04 | Calendário / fila | posts agendados, publicados, com erro |
| P05 | Avaliações | avaliações sem resposta, resposta sugerida pelo Claude, publicar após aprovação |

## Arquitetura (proposta, igual ao PrivoMind)

Site `/post` (HTML) + Supabase (login, tabelas `perfis`, `posts`, tokens guardados com segurança) + **Edge Function** que chama a API do Google + agendador (cron do Supabase) para os posts agendados.

## Fora da fase 1

Instagram, Facebook e demais redes (cada uma tem sua aprovação: app da Meta etc.), métricas, webhooks, cobrança de terceiros.
