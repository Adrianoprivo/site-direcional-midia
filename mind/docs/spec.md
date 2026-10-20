# PrivoMind — Especificação (spec)

**Versão:** 2.0 · **Data:** 2026-10-19 · **Dono:** Adriano · **Status:** aprovada em conversa (itens e decisões abaixo)

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
- Notas no tópico, ícones/emoji, exportar PDF, modelos prontos.
- Compartilhar com outras pessoas, apresentação, histórico de versões.

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
| `celular.py` | barra de baixo, formato no celular |
| `duplo_clique.py` | edição sempre abre |

Checagem manual do Adriano depois de publicar: Ctrl+F5, abrir um mapa antigo, arrastar, trocar tema, colar uma imagem.
