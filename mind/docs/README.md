# PrivoMind — documentos do projeto

Mapa mental próprio do Adriano em **direcionalmidia.com.br/mind**, inspirado nas funções do MindMeister (sem copiar código, marca ou textos). Uso pessoal, sem limite de mapas; depois pode compartilhar com outras pessoas.

**Última atualização:** 2026-10-19 (v2) · **Funções (`features.csv`):** essenciais 13 de 13 · importantes 7 de 11 feitas + 3 em parte

| Arquivo | O que é |
| --- | --- |
| `spec.md` | **Especificação** — o que o PrivoMind faz e como se comporta. Toda mudança nova entra aqui antes do código |
| `recon.md` | Mapeamento do MindMeister: telas, fluxos, dados, o que não copiar |
| `features.csv` | Funções com prioridade (must/should/could/skip) e status (`yes`/`partial`/`no`) |
| `architecture.md` | Plano técnico (fases, banco, armazenamento) |
| `testes/` | Testes automáticos com banco e armazenamento simulados (como rodar no `testes/README.md`) |

## Como funciona hoje

- **Página única** `mind/index.html`, mesmo molde da Privo Central. Publicar = entrar na `main` (EasyPanel publica sozinho).
- **Login:** Supabase Auth do projeto "central de projetos" (`ftahvdzbyqnvarukytws`), mesma conta da Central.
- **Dados:** tabela `public.mapas` (`id, user_id, titulo, dados jsonb, favorito, criado_em, atualizado_em`), RLS por dono. O mapa inteiro fica em `dados` (formato Mind Elixir, sem `theme`) + `dados.meta.privo = {tema, estilo}`.
- **Imagens:** Supabase Storage, pasta **privada** `mapas-imagens/<user_id>/<mapa_id>/<arquivo>`, 4 regras de acesso (só o dono lê/envia/atualiza/apaga). No tópico: `image.url` (link temporário de 7 dias, refeito ao abrir o mapa) + `metadata.img` (caminho do arquivo).
- **Editor:** Mind Elixir **5.15.1** (MIT) via CDN, arquivo `MindElixir.iife.js` (global `MindElixir.default`). Não usar a tag `latest` do npm: ela aponta para versão de teste (6.0.0-next).

## O que o usuário tem (v2, 2026-10-19)

Tudo detalhado na `spec.md`. Resumo:
- Lista de mapas: busca, favoritos, renomear, apagar (apaga as imagens junto), criar.
- Editor: teclado (Tab, Enter, F2, Delete, setas, Ctrl+Z/Y), salvar automático, PNG, claro/escuro automático.
- **Novo na v2:** criar sempre à direita · arrastar que encaixa na estrutura (antes/depois/dentro, troca de lado, mapa se arruma sozinho) · setinha no lugar da mãozinha · 5 temas de cor sólida + estilo Linha/Caixa por mapa · bolinha de abrir/fechar com número · negrito/itálico/sublinhado/riscado/cor (tópico inteiro ou só o trecho) · links · imagens (colar, soltar arquivo, escolher, link; tamanhos P/M/G) · rodapé com vista, zoom `− % +`, centralizar e aparência · vista em lista editável · cor do galho (VIS-07) · bug do nome do centro sumindo corrigido.

## Decisões e pegadinhas técnicas (ler antes de mexer)

1. **Arrastar é nosso** (`draggable:false`). `pointerdown` em captura no `#mapa`. Durante o arraste o galho é deslocado com `posicionar()` (galho principal: `left/top`; sub-tópico: **margens que se anulam** — `position:relative` em sub-tópico faz a biblioteca medir errado). Ao soltar usa `moveNodeBefore/After/In`.
2. **Posição livre só em galho principal** (`metadata.pos`). Ao abrir, `pos` de sub-tópico é apagado (mapas da v1).
3. **Lado dos galhos:** a biblioteca, no modo `SIDE`, escolhe o lado sozinha (equilibra). Para forçar: trocar `mind.direction` para o lado desejado durante a chamada e, ao mover pro centro, pôr `direction` no nó do centro **antes** da operação — o desfazer tira uma "foto" no evento `operation`, então tudo tem que estar certo antes dele (`moverProCentro`, `novoNoLado`). Depois, **sempre** volta pra `modoNormal()` (SIDE, ou RIGHT no foco), nunca pro valor anterior: com dois cliques rápidos o mapa ficava preso em "tudo à esquerda" e gravava assim (bug de 2026-10-19, teste `lados.py`). Ao abrir e ao salvar, `direction` é forçado pra SIDE.
4. `mind.addChild` é **substituído** na instância: no centro sempre cria à direita (Tab, Enter, menu). O original fica em `addOriginal`.
5. Mudanças que não são operação da biblioteca (posição livre) disparam `bus.fire('operation',{name:'moverLivre'})` para entrar no desfazer e no salvar.
6. **Formatação em trecho** usa a opção `markdown` da biblioteca com o nosso `md()` (escapa HTML antes): `**negrito**`, `_itálico_`, `++sublinhado++`, `~~riscado~~`. Título do mapa passa por `semMarcas()`.
7. **Estilo Caixa** = tema com `generateSubBranch: linhaCaixa`. Cada sub-tópico tem respiro de `--node-gap-x` (34px) dos lados; o galho principal não (`isFirst`).
8. **Caixa de edição** (`#input-box`) herda a cor do tópico; forçamos texto escuro/fundo claro (era o bug "nome do centro some").
9. Barra de formatação no PC fica **fixa no topo do mapa** (flutuando no tópico ela cobria as bolinhas "+").
10. Ctrl+Z da biblioteca só funciona com foco no mapa; temos um reforço que chama `undo/redo` quando o foco está em painel/rodapé.
11. `crypto.randomUUID` só existe em https; há alternativa para o teste local.
12. **Cache do navegador:** depois de publicar, pedir **Ctrl+F5** (celular: fechar e abrir a aba).
13. Repositório é **público**: a chave no código é a pública do Supabase; toda tabela e pasta nova precisa de regra de acesso.

## Pendências e próximos passos

- Ainda não testado com o Supabase de verdade (só no simulado): envio de imagem e exportar PNG com imagem. Conferir na primeira vez.
- Fora desta versão (ver `spec.md` §11): API para mandar mensagem e ele executar (junto com o agente de WhatsApp), notas, ícones/emoji, PDF, modelos, compartilhar, apresentação, histórico.
- Limpar imagens sem uso no armazenamento (removidas de tópicos).
- Segurança: ligar "proteção contra senha vazada" no painel do Supabase (aviso continua ativo em 2026-10-19).

## Como o Adriano gosta de trabalhar neste projeto

- Ele testa e manda ajustes por mensagem/print; não é programador.
- Mudança nova → primeiro entra na `spec.md`, depois código, depois teste automático.
- Revisar e testar antes de entregar; se aparecer erro ou decisão de design, apresentar pra decidir junto antes de seguir.
- Publicar direto na `main` está autorizado para ajustes do PrivoMind (pasta isolada, só ele acessa).
