# Privo Post — Especificação (spec)

**Versão:** 0.1 · **Data:** 2026-10-27 · **Dono:** Adriano · **Status:** fase 1 aprovada em conversa (27/10/2026)

Este documento diz **o que** o Privo Post faz e **como deve se comportar**. Todo ajuste novo entra aqui antes de virar código. Cada função tem um código (ex.: `CON-02`) para facilitar falar dela e testar.

Legenda de status: ✅ pronto · 🆕 entra nesta versão · ⏳ depois

---

## 1. Visão geral

- Ferramenta própria para publicar e agendar posts e responder avaliações no **Perfil da Empresa no Google**, em `direcionalmidia.com.br/post`. Base: [recon.md](recon.md).
- Uso próprio da Direcional Mídia (o perfil do Adriano e, depois, os perfis de clientes).
- Uma página só (`post/index.html`), sem servidor próprio. Login e banco no Supabase (projeto "central de projetos"), a **mesma conta** da Privo Central e do PrivoMind.
- A conversa com o Google acontece só em **funções do Supabase** (Edge Functions). A chave secreta do Google nunca vai para o navegador nem para o GitHub.
- Projeto Google Cloud: **Privo Post** (nº 11036189149). Acesso à API aprovado em 27/10/2026 (caso 7-2608000041450), cota de 300 consultas/min.

## 2. Princípios (valem pra tudo)

1. **Segredo fica no servidor.** Chave secreta e tokens do Google só existem dentro do Supabase, nunca na página.
2. **Só o dono vê o que é dele.** Cada conexão do Google pertence a um usuário do Supabase; ninguém lê a de outro.
3. **Nada público muda sem aprovação.** Publicar post ou responder avaliação só depois de o Adriano conferir (fase 2 em diante).
4. **Perfis de clientes são intocáveis até ordem dele.** O perfil "LS Caixas de Papelão" aparece na lista, mas não é usado para nada.
5. **Tudo em português**, palavras do dia a dia.

---

## 3. Fase 1 — Conectar o Google 🆕

Objetivo: entrar, conectar a conta do Google uma vez e ver a lista de perfis. **Só leitura**, nada é publicado nem alterado no Google.

| Código | Função | Comportamento |
| --- | --- | --- |
| ACE-01 | Entrar | E-mail e senha (Supabase Auth), a mesma da Central. Senha errada: "E-mail ou senha incorretos." |
| ACE-02 | Sair | Botão "Sair" no topo. |
| CON-01 | Estado da conexão | Ao abrir, mostra "Google não conectado" (botão **Conectar com o Google**) ou "Conectado como fulano@gmail.com" (botões **Atualizar lista** e **Desconectar**). |
| CON-02 | Conectar | Botão leva à tela de permissão do Google (app "Privo Post", permissão `business.manage`). Depois de "Permitir", o Google volta ao Supabase, que guarda a autorização e devolve para `/post` com a mensagem "Google conectado". |
| CON-03 | Cancelou ou deu erro | Se a pessoa clicar em "Cancelar" no Google ou algo falhar, volta para `/post` com a mensagem em português ("Conexão cancelada" / "Não deu para conectar, tente de novo") e nada é guardado. |
| CON-04 | Proteção do retorno | Cada pedido de conexão leva um código único que vale 10 minutos e é usado uma vez só. Retorno sem esse código, vencido ou repetido é recusado. |
| CON-05 | Continua conectado | A autorização fica guardada; o Adriano não precisa reconectar a cada visita. O Supabase renova o acesso sozinho quando vence (cerca de 1 hora). |
| CON-06 | Desconectar | Pede confirmação, avisa o Google para cancelar a autorização e apaga os tokens guardados. |
| PER-01 | Lista de perfis | Mostra as contas do Google e, em cada uma, os perfis (nome da empresa e endereço). Ex.: "Adriano Souza \| Direcional Mídia". |
| PER-02 | Perfil de cliente | Só perfis com "Direcional Mídia" no nome ganham a etiqueta **Seu perfil**; todos os outros aparecem como **Cliente — não usar** até o Adriano liberar (ex.: LS Caixas de Papelão). |
| PER-03 | Erros da API | Cota estourada, acesso negado ou API desligada aparecem em português, com o que fazer. |

## 4. Fase 2 — Posts ⏳

Depende da **Google My Business API (v4)**, que ainda não abre no Console (27/10). Telas P03 e P04 do recon: novo post (texto até 1.500, foto, botão), publicar agora ou agendar, fila com publicados e erros.

## 5. Fase 3 — Avaliações ⏳

Tela P05 do recon: avaliações sem resposta, resposta sugerida, publica só depois da aprovação do Adriano.

## 6. Fora do Privo Post por enquanto

Instagram, Facebook e outras redes, métricas, cobrança de terceiros.
