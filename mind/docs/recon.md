# Mapa de reconhecimento: MindMeister (web)

Recorte: editor de mapa mental (o "coração" do app) + modo tópicos + apresentação + exportação + compartilhamento
Para: **a confirmar com o Adriano** (uso próprio? integrar na Central de Projetos? produto pra vender?)
Data: 2026-10-19
Status: **v1 — só fontes públicas.** Telas e fluxos marcados como "inferido" precisam ser conferidos clicando no app (conta grátis do Adriano).

## Fontes

| # | fonte | URL | o que deu |
| --- | --- | --- | --- |
| 1 | site oficial (PT) | https://www.mindmeister.com/pt | lista de funções, casos de uso, integrações |
| 2 | página de preços | https://www.mindmeister.com/pt/pricing | o que o plano grátis libera e o que trava |
| 3 | preços dos planos pagos | https://toolradar.com/tools/mindmeister/pricing | valores Personal/Pro/Business (verificado out/2026) |
| 4 | avaliações Capterra | https://www.capterra.com/p/141357/MindMeister/ | nota, prós, reclamações |
| 5 | comunidade Meister | https://community.meister.co/discussion/1849/why-doesnt-mindmeister-have-these-features | funções que usuários sentem falta |
| 6 | comunidade (atalhos) | https://community.meister.co/discussion/comment/653/ | atalhos de teclado são parte central do uso |
| — | conta do Adriano | — | **pendente** |
| — | termos de uso | — | **não verifiquei**; por isso, por enquanto, só fontes públicas |

## Conferido na conta do Adriano (2026-10-19)

- **Início:** botões Criar / Navegue pelos modelos / Importar; caixa de IA ("descreva seu mapa ou faça upload", limite de 5000 caracteres) com sugestões prontas; lista de mapas recentes (grade ou lista) com busca.
- **Todos os mapas:** ordenar por última modificação, busca, favoritos (estrela), menu "..." por mapa, seleção em massa.
- **Visões do mapa:** Vista do mapa, **Esboço** (lista recuada com setas pra recolher) e **Modo Foco**; zoom com + / − e porcentagem; botão de camadas.
- **Modo leitor ("Visualizador"):** menu reduzido (procurar, ajuda, novidades, sair). Mapa com tema escuro e galhos coloridos por ramo.
- **Situação da conta:** 21 mapas. **17 são de outras pessoas, compartilhados com ele só pra ver.** Os mapas próprios aparecem apagados na lista (bloqueados pelo limite do plano grátis).
- **Não deu pra ver o editor em modo edição** sem criar mapa novo (limite do grátis). Detalhes de edição seguem das fontes públicas.

Consequência pro projeto: o PrivoMind resolve os **mapas dele**. Os mapas que outras pessoas compartilham **continuam no MindMeister** (ver é grátis lá).

## O coração do app (core loop)

Criar um mapa mental rápido pelo teclado (Enter = tópico irmão, Tab = tópico filho), organizar arrastando e recolhendo galhos, e depois **mostrar** (apresentação) ou **levar pra fora** (exportar / compartilhar).

## Como o MindMeister ganha dinheiro (o que ele trava)

| Plano | Preço | O que libera |
| --- | --- | --- |
| Grátis | €0 | **até 3 mapas**, apresentação, modo tópicos, temas, apps mobile |
| Personal | €6/usuário/mês | mapas ilimitados, mapas privados, exportar/imprimir, histórico de 7 dias |
| Pro | €10/usuário/mês | anexos ilimitados, histórico completo, exportar pra Office, marca própria |
| Business | €15/usuário/mês | SSO, backups, compartilhamento em grupo |

Leitura: o que faz as pessoas pagarem é **quantidade de mapas + exportação + histórico**. A IA está em Beta e liberada no grátis.

## Telas

| ID | tela | como chega | pra que serve | componentes principais | estados |
| --- | --- | --- | --- | --- | --- |
| S01 | Login / cadastro | entrada do app | entrar (e-mail ou Google) | formulário, botão Google | erro, carregando |
| S02 | Painel de mapas | após login | listar, criar, abrir, buscar mapas | grade/lista de mapas, botão "novo", busca, pastas | **vazio**, cheio, limite de 3 atingido |
| S03 | Escolher modelo | "novo mapa" | começar do zero ou de um modelo | galeria de modelos | — |
| S04 | **Editor do mapa** | abrir mapa | criar e organizar tópicos | tela infinita, tópico central, galhos, barra de ferramentas, zoom | vazio (só tópico central), cheio, editando texto, salvando |
| S05 | Painel lateral do tópico | selecionar tópico | estilo, ícone/emoji, link, nota, imagem, anexo | abas, seletor de cor/fonte | sem seleção, 1 tópico, vários tópicos |
| S06 | Modo tópicos (lista) | alternar visão no editor | ver/editar o mapa como lista recuada | lista hierárquica | — |
| S07 | Modo apresentação | botão "apresentar" | mostrar o mapa slide a slide | slides, navegação | editando slides, apresentando |
| S08 | Compartilhar | botão "compartilhar" | convidar pessoas, link público, permissões | campo de e-mail, nível de acesso, link | — |
| S09 | Comentários | ícone no tópico | conversar com @menção | fio de comentários | sem comentários, com comentários |
| S10 | Exportar | menu | PDF, imagem, Word, PowerPoint | lista de formatos | bloqueado no grátis |
| S11 | Histórico de versões | menu | voltar a uma versão antiga | linha do tempo | bloqueado no grátis |
| S12 | Gerar com IA | botão IA | criar mapa a partir de tema ou arquivo | campo de texto, upload | gerando, erro |
| S13 | Temas / estilo do mapa | menu de estilo | trocar visual do mapa todo | galeria de temas e layouts | — |

Telas S01 a S13: **inferidas** das fontes 1 e 2. Confirmar na conta.

## Fluxos

```
F01 Criar um mapa do zero (o principal)
    S02 -> S03 -> S04
    caminho feliz: ~3 cliques + só teclado depois disso
    detalhes: Enter cria irmão, Tab cria filho, digitar edita, Del apaga
    cantos: limite de 3 mapas no grátis, texto muito longo, desfazer/refazer

F02 Organizar o mapa
    S04 (arrastar tópico pra outro galho, recolher/expandir galho, mover com setas)
    cantos: arrastar um galho pra dentro dele mesmo, mapa com centenas de tópicos

F03 Enriquecer um tópico
    S04 -> S05 (cor, ícone, link, nota, imagem)

F04 Apresentar
    S04 -> S07

F05 Compartilhar / colaborar
    S04 -> S08 -> (outra pessoa abre) -> S09
    cantos: dois editando o mesmo tópico ao mesmo tempo

F06 Exportar
    S04 -> S10

F07 Criar com IA
    S02 -> S12 -> S04
```

## Componentes

| componente | variações | estados | usado em |
| --- | --- | --- | --- |
| Tópico (nó) | central, principal, sub-tópico, solto | normal, selecionado, editando, recolhido, arrastando | S04, S07 |
| Conector (galho) | curva, reto | normal, destacado | S04 |
| Tela infinita | — | zoom, arrastar a tela | S04 |
| Barra de ferramentas | topo, flutuante | — | S04 |
| Painel lateral | — | aberto, fechado | S05 |
| Card de mapa | grade, lista | normal, hover | S02 |
| Modal | — | aberto, carregando | S03, S08, S10, S12 |
| Seletor de cor / ícone / emoji | — | — | S05, S13 |
| Lista recuada | — | editando | S06 |

## Modelo de dados (palpite)

```
Usuario   id, nome, email, plano
          evidência: S01, página de preços | confiança: alta

Mapa      id, dono_id, titulo, tema, layout, privado (sim/não), criado_em, atualizado_em
          evidência: S02, preços (mapas privados) | confiança: alta

Topico    id, mapa_id, pai_id (vazio = central), ordem, texto, recolhido (sim/não),
          cor, fonte, icone, link, nota, imagem_url, posicao_x/y (só se solto)
          evidência: site (links, notas, emojis, imagens), S04, S05 | confiança: alta

Conexao   id, mapa_id, de_topico_id, para_topico_id   (ligação extra entre tópicos)
          confiança: palpite

Comentario  id, topico_id, autor_id, texto, criado_em | confiança: média
Compartilhamento  mapa_id, usuario_id/email, nivel (ver | editar) | confiança: média
Versao    id, mapa_id, conteudo (json), criado_em | confiança: média
Slide     id, mapa_id, ordem, topico_foco_id | confiança: palpite
```

Relações: Usuario 1-n Mapa, Mapa 1-n Topico, Topico 1-n Topico (árvore), Topico 1-n Comentario, Mapa 1-n Versao.

## O que não dá (ou não deve) copiar

- O nome, a logo, os modelos e os textos do MindMeister.
- Os 40 milhões de usuários e os mapas públicos da galeria ("Universo").
- Integrações com MeisterTask e Microsoft Teams (são parcerias/produtos deles). Dá pra fazer a **sua** integração (ex.: mandar tópico pra Central de Projetos).
- Apps nativos iOS/Android (fora do escopo; versão web responsiva resolve no começo).
- SSO corporativo, backups de conformidade (coisa de empresa grande).

## Tamanho

Telas 13, fluxos 7, entidades 8.

Partes difíceis:
1. **O editor em si**: desenhar o mapa automaticamente (cada galho no lugar certo) e arrastar tópicos sem bagunçar. É 70% do trabalho.
2. **Colaboração em tempo real** (duas pessoas no mesmo mapa). Sozinho isso já é projeto grande.
3. **Exportar** pra PDF/imagem/Word/PowerPoint com boa cara.

Tamanho:
- **Só pra você** (editor + teclado + recolher + estilo + modo lista + exportar imagem/PDF): **M** (algumas semanas).
- **Com colaboração em tempo real + comentários + IA**: **L** (um trimestre).
- **Tudo do MindMeister**: XL — reduzir o escopo.
