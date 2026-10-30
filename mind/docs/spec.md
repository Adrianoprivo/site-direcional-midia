# PrivoMind — Especificação (spec)

**Versão:** 2.2 · **Data:** 2026-10-30 (v2.0 de 2026-10-19) · **Dono:** Adriano · **Status:** aprovada em conversa (itens e decisões abaixo)

Este documento diz **o que** o PrivoMind faz e **como deve se comportar**. Todo ajuste novo entra aqui antes de virar código. Cada função tem um código (ex.: `ARR-03`) para facilitar falar dela e testar.

Legenda de status: ✅ pronto · 🆕 entra nesta versão · ⏳ depois

---

## 1. Visão geral

- Mapa mental próprio em `direcionalmidia.com.br/mind`, inspirado nas funções do MindMeister (sem copiar código, marca ou textos).
- Uso pessoal do Adriano, sem limite de mapas. Compartilhar com outras pessoas vem depois (fase 3).
- Uma página só (`mind/index.html`), sem servidor próprio. Banco e login no Supabase (projeto "central de projetos"), mesma conta da Privo Central.
- Funciona no computador (mouse + teclado) e no celular (toque).

## 2. Princípios (valem pra tudo)

1. **Nunca perder trabalho.** Toda mudança salva sozinha em até 1 segundo; se a internet cair, tenta de novo e avisa.
2. **O mapa sempre fica em ordem.** Nada encosta em nada nem fica perdido no meio do caminho: a estrutura se reorganiza sozinha.
3. **Simples primeiro.** Teclado pra quem é rápido, botões pra quem prefere clicar, toque no celular.
4. **Tudo em português**, palavras do dia a dia.
5. **Só o dono vê os próprios mapas e imagens** (regras de acesso no banco e no armazenamento).

---

## 3. Acesso e lista de mapas ✅

| Código | Função | Comportamento |
| --- | --- | --- |
| ACE-01 | Entrar | E-mail e senha (Supabase Auth). Senha errada: "E-mail ou senha incorretos." |
| ACE-02 | Sair | Botão "Sair" na lista. |
| LIS-01 | Lista | Mapas do mais recente pro mais antigo; favoritos no topo. Mostra "Editado hoje, 21:30". |
| LIS-02 | Buscar | Filtra pelo nome enquanto digita. Sem resultado: "Nada encontrado para …". |
| LIS-03 | Criar | "Novo mapa" cria e abre o editor. |
| LIS-04 | Favoritar / renomear / apagar | Apagar pede confirmação ("Isso não tem volta"). Renomear muda também o centro do mapa. |

## 4. Editor — estrutura do mapa

| Código | Função | Comportamento |
| --- | --- | --- |
| EST-01 ✅ | Centro (raiz) | Um tópico central por mapa. O texto dele é o nome do mapa. |
| EST-02 🆕 | **Criar sempre à direita** | Todo tópico novo criado a partir do centro (Tab, Enter, "+" da direita, botão do celular) vai para o **lado direito**. Só vai para a esquerda se o usuário clicar no **"+" da esquerda** do centro (ou no botão "Esquerda" do celular). |
| EST-03 ✅ | Filho / irmão / pai | Tab = filho, Enter = irmão embaixo, Ctrl+Enter = pai. Irmão fica no mesmo lado do original. |
| EST-04 ✅ | Abrir / fechar galho | Bolinha no fim do tópico. |
| EST-05 ✅ | Ligar (seta) e resumo (chave) | Pelo botão direito (PC) ou barra (celular). Seta nasce sem texto. |
| EST-06 ✅ | Foco | Mostra só um galho; botão "Sair do foco". |
| EST-07 ✅ | Desfazer / refazer | Ctrl+Z / Ctrl+Y, inclusive depois de arrastar, formatar e pôr imagem. |

## 5. Editor — arrastar (modelo novo) 🆕

**Decisão (2026-10-19):** o tópico arrastado **se encaixa na estrutura**, igual ao MindMeister. Acabou a posição livre nos sub-tópicos. A posição livre continua só nos **galhos principais** (os que saem direto do centro).

| Código | Função | Comportamento |
| --- | --- | --- |
| ARR-01 | Arrastar leva o galho junto | Ao arrastar um tópico, ele e **tudo que está pendurado nele** acompanham o ponteiro, com as linhas acompanhando. |
| ARR-02 | Prévia de onde vai cair | Enquanto arrasta, aparece onde o tópico vai entrar: **linha grossa acima** = vira irmão antes; **linha grossa abaixo** = vira irmão depois; **contorno tracejado + linha curva** = vira filho. |
| ARR-03 | Zonas do alvo | Em cima de outro tópico: terço de cima = antes, terço de baixo = depois, meio = dentro (filho). Perto de um tópico (até ~60 px): acima = antes, abaixo = depois, do lado de fora do galho = filho. O centro só aceita "filho". |
| ARR-04 | Soltar = reorganiza | Ao soltar sobre uma prévia, o tópico muda de lugar/galho e **o mapa inteiro se reorganiza sozinho**, sem sobrepor nada. |
| ARR-05 | Troca de lado | Se o tópico cair num galho do outro lado do centro (ou no centro, do outro lado), **ele e todos os filhos passam a apontar para aquele lado**. |
| ARR-06 | Soltar no vazio | Sub-tópico: volta pro lugar de onde saiu. Galho principal: fica onde soltou (posição livre, salva); se soltou do **outro lado do centro**, passa pra aquele lado em posição automática. |
| ARR-07 | Centro | Arrastar o centro ou o fundo vazio move a tela (não muda o mapa). |
| ARR-08 | Cancelar | Esc durante o arraste cancela e devolve o tópico. |
| ARR-09 | Mapas antigos | Ao abrir, posições livres antigas de sub-tópicos são descartadas (o mapa volta a ficar em ordem). Galhos principais mantêm a posição. |
| ARR-10 | "Realinhar" | Botão direito em galho principal movido: volta à posição automática. |
| ARR-11 | Bolinhas "+" no arraste | As bolinhas "+" e a barra de formatação **somem durante o arraste** (o mesmo ao arrastar o fundo) e reaparecem no lugar novo ao soltar. Nada fica parado pra trás. |

## 6. Editor — visual e aparência 🆕

| Código | Função | Comportamento |
| --- | --- | --- |
| VIS-01 | Cursor | **Setinha** em todo o mapa (sem mãozinha). Na caixa de texto em edição, cursor de texto. |
| VIS-02 | Temas de cor sólida | 5 temas, escolhidos **por mapa** no painel "Aparência": **Direcional** (roxo da marca, padrão), **Clássico**, **Grafite**, **Oceano**, **Terra**. Centro com cor sólida (sem gradiente). Galhos principais preenchidos com a cor do galho. Cada tema tem versão clara e escura (segue o aparelho). |
| VIS-03 | Estilo do tópico | Também por mapa: **Linha** (texto com a linha do galho embaixo — o atual) ou **Caixa** (sub-tópico dentro de uma caixinha com borda da cor do galho, linha chegando no meio da caixa). |
| VIS-04 | Bolinha de abrir/fechar refinada | Aberto: anel pequeno e discreto na cor do galho. Fechado: bolinha cheia com o **número de tópicos escondidos**. Cresce um pouco ao passar o mouse. |
| VIS-05 | Edição do centro | Ao editar o centro, o texto aparece **legível** (texto escuro em fundo claro, ou o contrário no escuro). *Corrige o bug "o nome some".* |
| VIS-06 | Fundo | Pontilhado leve, igual hoje. |
| VIS-07 | **Cor do galho** | No botão de cor (barra de formatação): "Cor do galho" com as cores do tema + Automática. A cor vale pra linha do tópico **e tudo que sai dele**. No galho principal muda também o preenchimento. Não existe no centro. Decisão (2026-10-19): cor por galho, não por linha solta, pra o mapa não perder a leitura de "qual assunto é esse". |
| VIS-08 | Lados estáveis | Trocar tema, estilo, foco ou criar rápido nunca muda o lado dos galhos. O mapa é sempre gravado no modo "dos dois lados"; mapa gravado errado é consertado ao abrir. |

Onde guarda: `dados.meta.privo = { tema, estilo }`. Mapa sem isso abre com Direcional + Linha.

## 7. Editor — texto, links e imagens 🆕

| Código | Função | Comportamento |
| --- | --- | --- |
| TXT-01 | Barra de formatação | No PC: barrinha fixa no topo do mapa (centralizada, aparece com um tópico selecionado ou em edição; fixa pra não cobrir tópicos nem as bolinhas "+") com **N** (negrito), *I* (itálico), <u>S</u> (sublinhado), ~~R~~ (riscado), **cor do texto**, **link**, **imagem**. No celular: botão "Formato" na barra de baixo abre as mesmas opções. |
| TXT-02 | Formatar o tópico inteiro | Com o tópico selecionado (sem editar), os botões aplicam no **tópico todo**. Clicar de novo tira. |
| TXT-03 | Formatar parte do texto | Editando o texto, selecionar um trecho e apertar o botão (ou **Ctrl+B / Ctrl+I / Ctrl+U**) aplica **só no trecho**. Por baixo, o texto guarda marcações (`**negrito**`, `_itálico_`, `++sublinhado++`, `~~riscado~~`) que aparecem só durante a edição. |
| TXT-04 | Cor do texto | 7 opções: padrão + 6 cores do tema. |
| TXT-05 | Nome do mapa | O nome na lista e no topo nunca mostra as marcações (`**`, etc.). |
| LNK-01 | Pôr link | Botão de link → caixinha "Cole o link" → Salvar. Sem `http`, completa com `https://`. Endereço inválido: "Esse link não parece válido." |
| LNK-02 | Abrir link | Ícone de link no fim do tópico; clicar abre em **nova aba**. |
| LNK-03 | Tirar / trocar link | Mesma caixinha, botões "Trocar" e "Remover". |
| IMG-01 | Pôr imagem — 3 jeitos | (a) **Colar** (Ctrl+V) uma imagem copiada com o tópico selecionado; (b) **arrastar um arquivo** de imagem e soltar em cima do tópico; (c) botão de imagem → "Escolher arquivo" ou "Colar link da imagem". |
| IMG-02 | Envio | Imagem é reduzida no próprio aparelho (lado maior até 1600 px, WEBP; GIF sobe como está) antes de subir. Limite: 10 MB no arquivo original. Formatos: JPG, PNG, WEBP, GIF. Enquanto sobe: aviso "Enviando imagem…". Erro: aviso "Não consegui enviar a imagem. Confira a internet e tente de novo." (fica uns segundos no topo) |
| IMG-03 | Onde fica | Supabase Storage, pasta **privada** `mapas-imagens/<usuário>/<mapa>/…`. Só o dono acessa. Ao abrir o mapa, gera links temporários de acesso. |
| IMG-04 | Tamanho | Botões **P / M / G** (120 / 220 / 360 px de largura). Padrão M. |
| IMG-05 | Tirar imagem | Botão "Remover imagem" tira do tópico (Ctrl+Z traz de volta). O arquivo fica guardado pra o desfazer funcionar; limpeza de arquivos sem uso fica pra depois (⏳). Ao apagar o mapa inteiro, as imagens dele são apagadas. |
| LRG-01 | Largura da caixa (2026-10-23) | Com o tópico selecionado aparece uma **alça** na borda de fora (direita nos galhos da direita, esquerda nos da esquerda). **Arrastar** estreita ou alarga a caixa livremente (60 a 900 px), o texto quebra em várias linhas. Vale no estilo **linha** e **caixa**. A largura fica salva no tópico (`style.width`). **Duplo clique** na alça volta ao automático. |

## 8. Editor — rodapé, zoom e vistas 🆕

| Código | Função | Comportamento |
| --- | --- | --- |
| ROD-01 | Rodapé | Barrinha no canto de baixo à direita: **[Vista do mapa ▾] · [− 80% +] · [centralizar] · [Aparência]**. No celular fica acima da barra de botões, compacta. |
| ROD-02 | Zoom | "−" e "+" mudam 10% por clique (20% a 200%). O número no meio mostra o zoom atual; clicar nele volta pra 100%. Atualiza também quando o zoom muda pela rodinha do mouse ou pinça. |
| ROD-03 | Centralizar | Leva o centro do mapa pro meio da tela (igual F1). |
| ROD-04 | Aparência | Abre o painel de tema (VIS-02) e estilo do tópico (VIS-03). Muda na hora e salva. |
| VIS-L1 | **Vista em lista** | Menu "Vista" troca entre **Mapa** e **Lista**. A lista mostra o mesmo conteúdo em tópicos recuados. |
| VIS-L2 | Editar na lista | Clicar no texto edita. **Enter** = novo tópico embaixo; **Tab** = vira filho do de cima; **Shift+Tab** = sobe um nível; **Backspace** em linha vazia = apaga (se não tiver filhos); setas ↑/↓ andam entre linhas. Triângulo à esquerda abre/fecha. |
| VIS-L3 | Volta pro mapa | Tudo que mudou na lista aparece no mapa. Salva igual ao mapa. |

## 9. Celular ✅ + ajustes

- Barra fixa embaixo com: filho, irmão, pai, subir, descer, ligar, resumo, foco, desfazer, editar, **formato** 🆕, apagar. No centro: Esquerda e Direita.
- Pinça para zoom; arrastar com o dedo move a tela; segurar e arrastar um tópico funciona como no PC (ARR-01..06).

## 10. Salvar e dados

- Tabela `public.mapas` (`id, user_id, titulo, dados jsonb, favorito, criado_em, atualizado_em`), RLS por dono.
- `dados` = formato Mind Elixir (sem `theme`) + `meta.privo` (tema e estilo).
- Por tópico: `style` (negrito, itálico, sublinhado, riscado, cor), `hyperLink`, `image {url,width,height}`, `metadata.img` (caminho do arquivo no armazenamento), `metadata.pos` (só galho principal).
- Salvamento automático 0,7 s depois da última mudança; ao sair da aba, salva na hora.

## 11. Fora desta versão ⏳

- **API para mandar mensagem e ele executar** — junto com o agente de WhatsApp, quando o editor estiver redondo.
- Anexos em tópicos (o clipe do MindMeister), exportar PDF, modelos prontos.
- Compartilhar com outras pessoas, apresentação, histórico de versões.

## 13. Estilo do tópico, fonte, ícones, comentário e menu ⋯ ✅ (2026-10-30)

Pedido do Adriano a partir dos prints do MindMeister. Tudo grátis e sem limite (lá, cor personalizada e imagens ilimitadas são pagas). Fica guardado **no próprio tópico**: `style` (visual), `icons` (ícones/emoji) e `metadata` (`est`, `fonte`, `nota`, `tarefa`, `comentarios`). Nada disso muda o tamanho da caixa depois de desenhada, só o que já nasce no estilo (forma, preenchimento, fonte), então as linhas sempre acompanham.

**Barra do tópico (PC e celular):** Estilo · Fonte · N I S R · cor do texto/galho · Link · Imagem/Ícone/Emoji · Ligar · Comentário · ⋯. No celular a barra rola de lado.

### 13.1 Estilo do tópico (botão balde)

| Código | Função | Comportamento |
| --- | --- | --- |
| EST-S01 | Painel com 3 abas | **Forma · Borda · Linha**. Mudou, aplicou na hora, Ctrl+Z desfaz. |
| PRE-01 | Cor de preenchimento | Automática (do tema) · sem preenchimento · 13 cores · **cor personalizada livre** (seletor do navegador, as últimas 6 ficam na lista). Vale pra **qualquer** tópico. |
| PRE-02 | Texto legível sozinho | Se a pessoa não escolheu cor de texto, a cor vira clara ou escura conforme o fundo. Tirar o preenchimento devolve a cor. Escolher uma cor de texto trava a escolha. |
| PRE-03 | Raiz | O box do centro também aceita cor (laranja, verde…). "Sem preenchimento" no centro deixa o texto escuro/claro conforme o tema. |
| PRE-04 | Galho principal | Aceita cor de preenchimento sem perder a cor da linha do galho. |
| FOR-01 | Formas | **Só a linha embaixo · Retângulo · Retângulo arredondado · Elipse · Nuvem**. Clicar de novo na forma volta ao padrão. |
| LIM-01 | Mostrar como limite | Desenha uma área tracejada, levemente tingida, em volta do tópico e de tudo que sai dele. Desabilitado no centro. |
| BOR-01 | Borda | Cor (automática = cor do galho), espessura (Sem · 1 · 2 · 3 · 4 · 6 px) e estilo (contínua · tracejada · pontilhada). Escolher cor ou estilo já liga a borda (2 px). Com o tópico selecionado, o contorno de seleção aparece por cima. |
| LIN-01 | Linha | Cor (a mesma "cor do galho": vale pro que sai dele), espessura e estilo da **linha que liga este tópico ao pai**. Não existe no centro. |

### 13.2 Fonte (botão A)

| Código | Função | Comportamento |
| --- | --- | --- |
| FNT-01 | 4 fontes | Padrão · Serifada (Lora) · Manuscrita (Caveat) · Técnica (JetBrains Mono). Vale pro tópico todo. |
| FNT-02 | N · I · riscado · sublinhado · sem efeito | Igual aos botões da barra e aos atalhos Ctrl+B/I/U. |
| FNT-03 | Cor do texto | Automática + 13 cores + personalizada. |
| FNT-04 | Durante a edição | O painel abre **sem tirar o cursor do texto**: N, I, riscado e sublinhado valem só pro trecho selecionado. Fonte e cor encerram a edição e valem pro tópico todo. |

### 13.3 Imagem · Ícone · Emoji (botão de imagem)

| Código | Função | Comportamento |
| --- | --- | --- |
| ICO-01 | Ícone | Prioridade (①–⑦), progresso (○ ◔ ◑ ◕ ●), marcadores, setas e símbolos. Dá pra pôr vários no mesmo tópico; clicar de novo tira; "Remover ícones do tópico". Ficam depois do texto. |
| EMO-01 | Emoji | 6 categorias (rostos, gestos, negócios, marcas, natureza, lugares). Mesmo comportamento dos ícones. |
| IMG-01..05 | Imagem | Continua igual (seção 7), agora na aba "Imagem". |

### 13.4 Comentário, nota e tarefa

| Código | Função | Comportamento |
| --- | --- | --- |
| COM-01 | Comentário | Botão de balão: lista de comentários do tópico (com data e hora), caixa pra escrever (Ctrl+Enter envia), × apaga um. Selo 💬 com o total no canto do tópico. |
| NOT-01 | Nota | **Alt+Shift+N** ou menu ⋯. Texto livre guardado no tópico. Selo 📝 no tópico; ao passar o mouse mostra o começo da nota. |
| TAR-01 | Tarefa | **Alt+Shift+T** ou menu ⋯. Concluída, prazo, prioridade (🔴 alta · 🟠 média · 🟢 baixa). Selo no canto: `☐ 05/11 🔴`; concluída `✔ feita` (texto riscado); prazo vencido fica vermelho. |

### 13.5 Menu ⋯

| Código | Item | Comportamento |
| --- | --- | --- |
| MEN-01 | Novo tópico filho (Tab) | Cria o filho e já abre a edição. |
| MEN-02 | Criar tarefa / Adicionar nota | Abrem os painéis acima (viram "Editar" quando já existem). |
| MEN-03 | Copiar · Colar (Ctrl+C / Ctrl+V) | Copia o tópico com tudo que sai dele e cola dentro de outro (ids novos). Funciona também entre mapas. |
| MEN-04 | Colar estilo (Ctrl+Alt+V) | Leva só o visual do último tópico copiado (fonte, cores, forma, borda, linha, limite) pro tópico escolhido ou pros vários selecionados. O texto não muda. |
| MEN-05 | Selecione todos os subtópicos (Ctrl+Shift+A) | Seleciona tudo que sai do tópico (só o que está visível). |
| MEN-06 | Mostrar Detalhe [n] | Quantos níveis abaixo do tópico ficam abertos; o resto fecha (a bolinha do galho abre de novo). Começa no número de níveis que estão abertos. |
| MEN-07 | Alinhamento automático | Só nos galhos principais. Ligado = posição automática; desligado = pode arrastar o galho pra onde quiser (é o mesmo "Realinhar" de antes). Nos sub-tópicos fica ligado e desabilitado, porque eles sempre se arrumam. |
| MEN-08 | Exibir este ramo como › | **Mapa mental** (volta ao mapa) ou **Lista** (só este ramo em tópicos recuados, com "Ver o mapa inteiro"). |
| MEN-09 | Copiar link para o tópico | Gera `…/mind/#/mapa/<mapa>/t/<tópico>`. Abrir o link abre o mapa, abre os galhos fechados no caminho e seleciona o tópico. |

### 13.6 Onde fica guardado

- `style.background | borderRadius | padding | boxShadow | border | fontFamily | fontSize | color…` → o visual do tópico (inline, igual ao que já existia pra negrito/cor).
- `icons: ['①','🚀']` → ícones e emoji.
- `metadata.est = { forma, fundo, bCor, bLarg, bTipo, lLarg, lTipo, limite, inkAuto }`; `metadata.fonte`; `metadata.nota`; `metadata.tarefa = { feita, prazo, prio }`; `metadata.comentarios = [{ id, t, d }]`.
- Cor da linha continua em `branchColor`.

### 13.7 Limites conhecidos

- **Nuvem** é uma aproximação (desenhada com SVG esticado), não uma nuvem vetorial perfeita.
- **Anexo (clipe)** ainda não existe. Precisa liberar outros tipos de arquivo na pasta privada do Supabase; fica como próximo passo.
- Comentário é pessoal (sem @menção nem resposta), porque o mapa ainda é de uma pessoa só.
- As fontes Lora e Caveat vêm do Google Fonts; sem internet, o navegador usa uma fonte parecida.

## 14. Tela inicial: menu lateral, lixeira, modelos, importar e colar entre mapas ✅ (2026-10-30)

Pedido do Adriano a partir dos prints do MindMeister. Tudo no mesmo arquivo `mind/index.html`.

| Código | Função | Comportamento |
| --- | --- | --- |
| LAT-01 | Menu lateral | Logo (rosa dos ventos da Direcional Mídia) + **PrivoMind**, e-mail de quem entrou, **Lar · Todos os mapas · Favoritos · Lixeira** e Sair. No celular vira uma barra no topo. Endereços: `#/`, `#/todos`, `#/favoritos`, `#/lixeira`. |
| LAT-02 | Botões do topo | **Novo mapa · Navegue pelos modelos · Importar**. |
| LAT-03 | Lar | Saudação, atalhos para 4 modelos e os 8 mapas mais recentes. |
| LIX-01 | Lixeira | A lixeira do ícone **não apaga**: o mapa ganha `excluido_em` (coluna nova da tabela `mapas`) e some das outras telas. Na Lixeira: **Restaurar**, **Apagar para sempre** (com confirmação, apaga também as imagens) e **Esvaziar lixeira**. Nada é apagado sozinho. |
| MOD-01 | Modelos | Janela "Começar" com 8 categorias (Destaque, Gerenciamento de projetos, Negócios e metas, Educação e Notas, Recursos Humanos, Brainstorming e Análise, Marketing e Conteúdo, Layout), busca e miniaturas. 18 modelos próprios (textos nossos), entre eles Método DEVER, Matriz de decisão, Planejamento de OKR, Análise SWOT e Checklist do Google Meu Negócio. |
| MOD-02 | Prévia | Mostra o mapa de verdade (zoom e arrastar), setas para o modelo anterior/próximo, descrição e **Usar modelo** (cria uma cópia nova e abre). |
| IMP-01 | Importar | Arrastar o arquivo, procurar, ou colar um texto. Lê **texto com recuo e Markdown** (`#`, `-`, `*`, `1.`), **Freemind (.mm)** (lados e links), **OPML** e **JSON do PrivoMind/Mind Elixir**. Cria um mapa novo (limite de 3000 tópicos). Formatos compactados (.xmind, .mind, .mmap, .zip) ainda não: avisa e sugere exportar como texto, Freemind ou OPML. |
| CPY-01 | Colar entre mapas | Selecionar um tópico, **Ctrl+C**, abrir outro mapa, selecionar o destino, **Ctrl+V**: leva o tópico com tudo que sai dele, com ids novos. Imagens ganham um arquivo próprio na pasta do mapa de destino (apagar o mapa de origem não quebra a cópia). Ctrl+C avisa "Copiado". |

Banco: `alter table mapas add column excluido_em timestamptz` (migração `privomind_mapas_lixeira`, aplicada em 2026-10-30).

## 12. Como testar

Testes automáticos em `testes/` (navegador sem tela + banco e armazenamento simulados). Cada código acima tem pelo menos uma checagem:

| Teste | Cobre |
| --- | --- |
| `base_lista_editor.py` | ACE, LIS, salvar e recarregar, modo escuro |
| `arrastar.py` | ARR-01..11 |
| `bolinhas.py` | "+" em hover, lado certo, EST-02 |
| `aparencia.py` | VIS-01..05, ROD-01..04 |
| `formatar.py` | TXT, LNK, IMG |
| `lista.py` | VIS-L1..3 |
| `painel_modelos.py` | seção 14: menu lateral, lixeira, modelos e prévia, importar (texto, md, mm, opml, json), colar entre mapas, celular |
| `estilo_menu.py` | seção 13: estilo (forma, preenchimento, borda, linha, limite), fonte, ícone/emoji, comentário, nota, tarefa, menu ⋯, link do tópico, celular |
| `celular.py` | barra de baixo, formato no celular |
| `duplo_clique.py` | edição sempre abre |

Checagem manual do Adriano depois de publicar: Ctrl+F5, abrir um mapa antigo, arrastar, trocar tema, colar uma imagem.
