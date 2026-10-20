# Testes do PrivoMind

Rodam a página de verdade num navegador sem tela (Playwright), com um **banco simulado** (`mock-supabase.js`), sem usar senha nem tocar no Supabase real.

## Preparar (uma vez)

```bash
pip install playwright && python -m playwright install chromium
mkdir -p /tmp/me && cd /tmp/me && npm pack mind-elixir@5.15.1 && tar xzf mind-elixir-5.15.1.tgz   # vira /tmp/me/package
```

## Rodar (de dentro desta pasta)

```bash
mkdir -p out
python3 base_lista_editor.py <raiz-do-repo> /tmp/me/package out   # login, lista, criar, salvar, recarregar, buscar, apagar, modo escuro
python3 duplo_clique.py      <raiz-do-repo> /tmp/me/package out   # duplo clique sempre abre edição
python3 arrastar.py          <raiz-do-repo> /tmp/me/package out   # arrastar livre, centro move o mapa, ímã troca de galho, recarregar
python3 bolinhas.py          <raiz-do-repo> /tmp/me/package out   # bolinhas +, lado certo, barra escondida no PC, arrastar o fundo
python3 celular.py           <raiz-do-repo> /tmp/me/package out   # iPhone simulado com a barra de baixo
```

Resultado esperado: cada linha impressa confirma um comportamento e `ERROS: []` no fim. Capturas de tela vão para `out/`.
O aviso `Failed to load resource` é normal (as fontes do Google são bloqueadas de propósito no teste).
