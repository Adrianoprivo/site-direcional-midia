# PrivoMind — documentos do projeto

Mapa mental próprio do Adriano em **direcionalmidia.com.br/mind**, inspirado nas funções do MindMeister (sem copiar código, marca ou textos). Uso pessoal, sem limite de mapas; depois pode compartilhar com outras pessoas.

**Última atualização:** 2026-10-19 · **Placar vs MindMeister:** 70/100, 13 de 13 funções essenciais feitas (`features.csv`)

| Arquivo | O que é |
| --- | --- |
| `recon.md` | Mapeamento do MindMeister: telas, fluxos, dados, o que não copiar |
| `features.csv` | Funções com prioridade (must/should/could/skip) e status (`yes`/`partial`/`no`) |
| `architecture.md` | Plano técnico original (fases, banco) |
| `testes/` | Testes automáticos com banco simulado (como rodar no `testes/README.md`) |

## Como funciona hoje

- **Página única** `mind/index.html`, mesmo molde da Privo Central. Publicar = entrar na `main` (EasyPanel publica sozinho).
- **Login:** Supabase Auth do projeto "central de projetos" (`ftahvdzbyqnvarukytws`), mesma conta da Central.
- **Dados:** tabela `public.mapas` (`id, user_id, titulo, dados jsonb, favorito, criado_em, atualizado_em`), RLS por dono, gatilho atualiza `atualizado_em`. O mapa inteiro fica em `dados` (formato Mind Elixir, sem `theme`).
- **Editor:** Mind Elixir **5.15.1** (MIT) via CDN, arquivo `MindElixir.iife.js` (global `MindElixir.default`). Não usar a tag `latest` do npm: ela aponta para versão de teste (6.0.0-next).

## O que o usuário tem (2026-10-19)

- Lista de mapas: busca, favoritos, renomear, apagar, criar.
- Editor: Tab (filho), Enter (irmão), F2/2 cliques (editar), Delete, setas, Ctrl+Z/Y, salvar automático, exportar PNG, claro/escuro automático.
- **Arrastar:** fundo vazio ou centro → move o mapa; qualquer tópico → vai livre com os filhos (posição salva); perto de outro tópico → **ímã** (linha tracejada) e cola nele ao soltar.
- **Bolinhas "+"** ao passar o mouse: na frente = filho, embaixo = irmão; no centro, uma de cada lado (escolhe o lado do galho).
- **Bolinha de abrir/fechar galho** sempre visível, na cor do galho.
- **Botão direito:** pai, subir, descer, ligar (seta), resumo (chave), foco, realinhar posição.
- **Celular:** barra de botões fixa embaixo (filho, irmão, pai, subir, descer, ligar, resumo, foco, desfazer, editar, apagar).
- Visual: cores vivas, centro em gradiente roxo→ciano, galhos principais preenchidos, fundo pontilhado.

## Decisões e pegadinhas técnicas (ler antes de mexer)

1. **Posição livre** fica em `nodeObj.metadata.pos = {x,y}`. Galho principal é deslocado com `position:relative; left/top`. Sub-tópico é deslocado com **margens que se anulam** (`margin: y -x -y x`) — se usar `position:relative` em sub-tópico, a biblioteca mede errado e a linha não acompanha. Reaplicado a cada evento `linkDiv` (com trava `reaplicando` pra não entrar em laço).
2. **Arrastar é nosso, não da biblioteca** (`draggable:false`). Nosso `pointerdown` em captura no `#mapa` para a propagação nos tópicos.
3. **Fundo arrasta com botão esquerdo** porque `mouseSelectionButton:2` (a biblioteca inverte: seleção em caixa vai pro direito).
4. **Criar galho num lado escolhido:** `addChild` ignora `direction`; usamos `getData` → empurra o nó com `direction` → `refresh` → `beginEdit` (`novoNoLado`).
5. **Setas novas** vêm com o texto "Custom Link" (inglês); `limparRotulos()` apaga.
6. **Duplo clique** às vezes não abre edição na biblioteca (tópico já selecionado); há um reforço que chama `beginEdit`.
7. **Resumo** abre um campo de texto ao criar; enquanto um texto está em edição, o arrastar fica travado de propósito.
8. **Cache do navegador:** depois de publicar, o navegador pode mostrar a versão antiga. Pedir **Ctrl+F5** (celular: fechar e abrir a aba).
9. Repositório é **público**: a chave no código é a pública do Supabase; toda tabela nova precisa de RLS.

## Pendências e próximos passos

- Pendente com o usuário: lista de melhorias que ele vai mandar na próxima conversa.
- Fase 2 sugerida (do `features.csv`): cor/ícone/emoji no tópico, notas e links, imagem no tópico, modo Esboço (lista), exportar PDF.
- Fase 3: compartilhar com outra pessoa, apresentação, histórico de versões.
- Segurança: ligar "proteção contra senha vazada" no painel do Supabase (aviso do Supabase em 2026-10-19).

## Como o Adriano gosta de trabalhar neste projeto

- Ele testa e manda ajustes por mensagem/print; não é programador.
- Revisar e testar antes de entregar; se aparecer erro ou decisão de design, apresentar pra decidir junto antes de seguir.
- Publicar direto na `main` está autorizado para ajustes do PrivoMind (pasta isolada, só ele acessa).
