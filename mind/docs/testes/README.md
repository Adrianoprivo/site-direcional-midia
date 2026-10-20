# Testes do PrivoMind

Rodam a página de verdade num navegador sem tela (Playwright), com **banco e armazenamento simulados** (`mock-supabase.js`), sem usar senha nem tocar no Supabase real.

## Preparar (uma vez)

```bash
pip install playwright && python -m playwright install chromium
mkdir -p /tmp/me && cd /tmp/me && npm pack mind-elixir@5.15.1 && tar xzf mind-elixir-5.15.1.tgz   # vira /tmp/me/package
```

## Rodar (de dentro desta pasta)

```bash
mkdir -p out
python3 base_lista_editor.py <raiz-do-repo> /tmp/me/package out   # ACE, LIS: login, lista, criar, salvar, recarregar, buscar, apagar, modo escuro
python3 duplo_clique.py      <raiz-do-repo> /tmp/me/package out   # duplo clique sempre abre edição
python3 arrastar.py          <raiz-do-repo> /tmp/me/package out   # ARR-01..11: encaixar antes/depois/dentro, troca de lado, Esc, desfazer, recarregar
python3 bolinhas.py          <raiz-do-repo> /tmp/me/package out   # bolinhas +, lado certo, barra escondida no PC, arrastar o fundo
python3 aparencia.py         <raiz-do-repo> /tmp/me/package out   # VIS-01..05, EST-02, ROD: setinha, temas, caixa, bolinha com número, zoom, centralizar
python3 formatar.py          <raiz-do-repo> /tmp/me/package out   # TXT, LNK, IMG: negrito no tópico e no trecho, cor, links, imagens (colar/soltar/arquivo)
python3 lista.py             <raiz-do-repo> /tmp/me/package out   # VIS-L: vista em lista (Enter, Tab, Shift+Tab, Backspace, setas) e volta pro mapa
python3 lados.py            <raiz-do-repo> /tmp/me/package out   # VIS-08: tema/estilo/foco/cliques rápidos nunca mudam o lado dos galhos
python3 celular.py           <raiz-do-repo> /tmp/me/package out   # iPhone simulado com a barra de baixo
```

Resultado esperado: linhas `OK` (nenhuma `FALHOU`) e `ERROS: []` no fim. Os códigos (ARR-03 etc.) são os da `spec.md`. Capturas de tela vão para `out/`.
O aviso `Failed to load resource` é normal (as fontes do Google são bloqueadas de propósito no teste).
