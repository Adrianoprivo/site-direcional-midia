// IG-CON-01 / IG-CON-05 / IG-CON-06 / IG-MET-01..09: status, perfil (com bio), posts com métricas, métricas da conta, desconectar.
// Só leitura no Instagram nesta etapa.
import { admin, cors, json, usuario } from "../_shared/comum.ts";

const G = "https://graph.instagram.com";
type Conexao = { user_id: string; username: string | null; access_token: string; obtido_em: string; expira_em: string | null };

class ErroIG extends Error {
  constructor(public status: number, public codigo: number | null, public motivo: string) { super(motivo); }
}

async function ig(caminho: string, token: string, params: Record<string, string> = {}) {
  const r = await fetch(`${G}/${caminho}?${new URLSearchParams({ ...params, access_token: token })}`);
  const corpo = await r.json().catch(() => ({}));
  if (!r.ok) {
    console.error("instagram", r.status, caminho.split("/")[0], corpo?.error?.code, corpo?.error?.message);
    throw new ErroIG(r.status, corpo?.error?.code ?? null, corpo?.error?.type ?? "erro");
  }
  return corpo;
}

/** IG-CON-05: renova o token de 60 dias quando já tem mais de 24 h e faltam menos de 20 dias. */
async function tokenValido(c: Conexao): Promise<string> {
  const idade = Date.now() - new Date(c.obtido_em).getTime();
  const falta = c.expira_em ? new Date(c.expira_em).getTime() - Date.now() : 0;
  if (falta <= 0) throw new ErroIG(401, 190, "reconectar");
  if (idade > 24 * 3600e3 && falta < 20 * 24 * 3600e3) {
    try {
      const n = await ig("refresh_access_token", c.access_token, { grant_type: "ig_refresh_token" });
      const agora = Date.now();
      await admin().from("ig_conexoes").update({
        access_token: n.access_token,
        obtido_em: new Date(agora).toISOString(),
        expira_em: new Date(agora + Number(n.expires_in ?? 5184000) * 1000).toISOString(),
        atualizado_em: new Date(agora).toISOString(),
      }).eq("user_id", c.user_id);
      return n.access_token;
    } catch (e) {
      console.error("refresh", e);
    }
  }
  return c.access_token;
}

const METRICAS_POST = ["views", "reach", "likes", "comments", "shares", "saved", "total_interactions"];

async function metricasDoPost(id: string, token: string) {
  // Nem todo tipo de post aceita todas as métricas; se o lote falhar, tenta uma a uma.
  const ler = (lista: string[]) => ig(`${id}/insights`, token, { metric: lista.join(",") });
  const saida: Record<string, number> = {};
  const juntar = (r: { data?: { name: string; values?: { value: number }[]; total_value?: { value: number } }[] }) => {
    for (const m of r.data ?? []) saida[m.name] = m.total_value?.value ?? m.values?.[0]?.value ?? 0;
  };
  try {
    juntar(await ler(METRICAS_POST));
  } catch {
    for (const m of METRICAS_POST) {
      try { juntar(await ler([m])); } catch { /* métrica não disponível para este post */ }
    }
  }
  return saida;
}

async function perfil(token: string) {
  const f = await ig("me", token, {
    fields: "user_id,username,name,account_type,profile_picture_url,biography,website,followers_count,follows_count,media_count",
  });
  return {
    usuario: f.username, nome: f.name, tipo: f.account_type, foto: f.profile_picture_url,
    bio: f.biography ?? "", site: f.website ?? "",
    seguidores: f.followers_count, seguindo: f.follows_count, posts: f.media_count,
  };
}

async function posts(token: string, limite = 12, depois?: string) { // deno-lint-ignore no-explicit-any
  const midia = await ig("me/media", token, {
    fields: "id,caption,media_type,media_product_type,permalink,thumbnail_url,media_url,timestamp,like_count,comments_count,children{media_type,media_url,thumbnail_url}",
    limit: String(limite),
    ...(depois ? { after: depois } : {}),
  });
  const lista = await Promise.all((midia.data ?? []).map(async (m: any) => ({
    id: m.id,
    legenda: (m.caption ?? "").slice(0, 200),
    tipo: m.media_product_type ?? m.media_type,
    link: m.permalink,
    formato: m.media_type, // IMAGE, VIDEO ou CAROUSEL_ALBUM
    // capa: vídeo usa a miniatura; foto usa a própria imagem; carrossel usa a 1ª foto (ou a miniatura do 1º vídeo)
    capa: m.thumbnail_url ?? (m.media_type !== "VIDEO" ? m.media_url : null) ??
      (m.children?.data?.[0] ? (m.children.data[0].thumbnail_url ?? (m.children.data[0].media_type !== "VIDEO" ? m.children.data[0].media_url : null)) : null) ?? null,
    data: m.timestamp,
    metricas: { likes: m.like_count ?? 0, comments: m.comments_count ?? 0, ...(await metricasDoPost(m.id, token)) },
  })));
  return { lista, proximo: midia.paging?.next ? (midia.paging?.cursors?.after ?? null) : null };
}

// IG-MET-04/06: métricas da conta. Regra do Adriano: "últimos N dias" = N dias corridos SEM o dia de hoje (fuso de São Paulo).
// O Instagram guarda as métricas da conta por 90 dias. Cada consulta vai em janelas de até 30 dias.
const METRICAS_CONTA = ["views", "reach", "accounts_engaged", "total_interactions", "likes", "comments", "shares", "saves", "profile_links_taps", "follows_and_unfollows"];
const UNICAS = new Set(["reach", "accounts_engaged"]); // contas únicas: somar janelas superestima
const FUSO = -3 * 3600; // São Paulo, sem horário de verão
const DIA = 86400;

/** "AAAA-MM-DD" (data local de SP) -> segundos UTC do início desse dia */
function inicioDia(d: string) { return Math.floor(Date.parse(d + "T00:00:00Z") / 1000) - FUSO; }
function dataLocal(seg: number) { return new Date((seg + FUSO) * 1000).toISOString().slice(0, 10); }
function hojeLocal() { return dataLocal(Math.floor(Date.now() / 1000)); }

function janela(dias: number) {
  const hoje0 = inicioDia(hojeLocal());
  return { since: hoje0 - dias * DIA, until: hoje0 - 1 };
}

async function totaisJanela(token: string, since: number, until: number) {
  const base = { period: "day", metric_type: "total_value", since: String(since), until: String(until) };
  const saida: Record<string, number> = {};
  const juntar = (r: { data?: { name: string; total_value?: { value: number; breakdowns?: { results?: { dimension_values: string[]; value: number }[] }[] } }[] }, pref = "") => {
    for (const m of r.data ?? []) {
      if (m.total_value?.breakdowns?.length) {
        for (const b of m.total_value.breakdowns[0].results ?? []) saida[`${pref}${m.name}:${b.dimension_values.join("|")}`] = b.value;
      } else saida[pref + m.name] = m.total_value?.value ?? 0;
    }
  };
  try {
    juntar(await ig("me/insights", token, { ...base, metric: METRICAS_CONTA.join(",") }));
  } catch {
    for (const m of METRICAS_CONTA) {
      try { juntar(await ig("me/insights", token, { ...base, metric: m })); } catch { /* indisponível */ }
    }
  }
  try { juntar(await ig("me/insights", token, { ...base, metric: "follows_and_unfollows", breakdown: "follow_type" })); } catch { /* indisponível */ }
  // IG-MET-07: por formato (Reels, posts, stories…)
  try {
    juntar(await ig("me/insights", token, { ...base, metric: "views,reach,likes,comments,shares,saves,total_interactions", breakdown: "media_product_type" }), "fmt:");
  } catch { /* indisponível */ }
  return saida;
}

async function metricasPeriodo(token: string, since: number, until: number) {
  const agora = Math.floor(Date.now() / 1000);
  const limite = inicioDia(hojeLocal()) - 90 * DIA;
  since = Math.max(since, limite);
  until = Math.min(until, agora);
  const janelas: [number, number][] = [];
  for (let a = since; a <= until; a += 30 * DIA) janelas.push([a, Math.min(a + 30 * DIA - 1, until)]);
  const partes = await Promise.all(janelas.map(([a, b]) => totaisJanela(token, a, b)));
  const soma: Record<string, number> = {};
  for (const p of partes) for (const [k, v] of Object.entries(p)) soma[k] = (soma[k] ?? 0) + v;
  const tem = (k: string) => partes.some((p) => k in p);
  const v = (k: string) => (tem(k) ? soma[k] : null);
  const formatos: Record<string, Record<string, number>> = {};
  for (const [k, val] of Object.entries(soma)) {
    if (!k.startsWith("fmt:")) continue;
    const [met, tipo] = k.slice(4).split(":");
    (formatos[tipo] ??= {})[met] = val;
  }
  return {
    de: dataLocal(since), ate: dataLocal(until), dias: Math.round((until - since + 1) / DIA),
    aproximado: janelas.length > 1 ? [...UNICAS] : [],
    m: {
      views: v("views"), reach: v("reach"), accounts_engaged: v("accounts_engaged"), total_interactions: v("total_interactions"),
      likes: v("likes"), comments: v("comments"), shares: v("shares"), saves: v("saves"), profile_links_taps: v("profile_links_taps"),
      seguiram: v("follows_and_unfollows:FOLLOWER"), deixaram: v("follows_and_unfollows:NON_FOLLOWER"),
    },
    formatos,
  };
}

async function metricasConta(token: string, dias: number) {
  const { since, until } = janela(dias);
  const r = await metricasPeriodo(token, since, until);
  return { ...r, dias };
}

const MSG: Record<string, string> = {
  reconectar: "A autorização do Instagram venceu ou foi cancelada. Desconecte e conecte de novo.",
  OAuthException: "O Instagram não aceitou a autorização. Desconecte e conecte de novo.",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors(req) });
  if (req.method !== "POST") return json(req, { erro: "Método não permitido." }, 405);
  try {
    const uid = await usuario(req);
    if (!uid) return json(req, { erro: "Entre de novo para continuar." }, 401);
    const { acao, depois, de, ate, comparar, id } = await req.json().catch(() => ({}));
    const db = admin();
    const { data: c } = await db.from("ig_conexoes")
      .select("user_id,username,access_token,obtido_em,expira_em").eq("user_id", uid).maybeSingle();

    if (acao === "status") {
      return json(req, c ? { conectado: true, usuario: c.username, expira_em: c.expira_em } : { conectado: false });
    }
    if (!c) return json(req, { erro: "Instagram não conectado." }, 409);

    if (acao === "perfil") return json(req, await perfil(await tokenValido(c as Conexao)));
    if (acao === "posts") {
      const r = await posts(await tokenValido(c as Conexao), 12, typeof depois === "string" ? depois : undefined);
      return json(req, { posts: r.lista, proximo: r.proximo });
    }
    if (acao === "midia") { // IG-MET-09: vídeo/fotos do post para tocar na própria página (links do Instagram expiram)
      if (typeof id !== "string" || !/^\d{5,30}$/.test(id)) return json(req, { erro: "Post inválido." }, 400);
      const m = await ig(id, await tokenValido(c as Conexao), {
        fields: "id,media_type,media_product_type,media_url,thumbnail_url,permalink,caption,timestamp,children{media_type,media_url,thumbnail_url}",
      });
      const itens = m.children?.data?.length
        ? m.children.data.map((x: Record<string, string>) => ({ tipo: x.media_type, url: x.media_url, capa: x.thumbnail_url ?? null }))
        : [{ tipo: m.media_type, url: m.media_url, capa: m.thumbnail_url ?? null }];
      return json(req, { id: m.id, link: m.permalink, legenda: m.caption ?? "", data: m.timestamp, tipo: m.media_product_type ?? m.media_type, itens });
    }
    if (acao === "periodo") { // IG-MET-06: período escolhido (+ período anterior do mesmo tamanho)
      const ok = (d: unknown) => typeof d === "string" && /^\d{4}-\d{2}-\d{2}$/.test(d);
      if (!ok(de) || !ok(ate)) return json(req, { erro: "Período inválido." }, 400);
      const t = await tokenValido(c as Conexao);
      const since = inicioDia(de), until = inicioDia(ate) + DIA - 1;
      const tam = until - since + 1;
      const [atual, anterior] = await Promise.all([
        metricasPeriodo(t, since, until),
        comparar ? metricasPeriodo(t, since - tam, since - 1) : Promise.resolve(null),
      ]);
      return json(req, { atual, anterior, limite_dias: 90 });
    }
    if (acao === "conta") {
      const t = await tokenValido(c as Conexao);
      const [d7, d14, d30] = await Promise.all([7, 14, 30].map((d) => metricasConta(t, d)));
      return json(req, { periodos: [d7, d14, d30] });
    }

    if (acao === "desconectar") {
      await db.from("ig_conexoes").delete().eq("user_id", uid);
      return json(req, { conectado: false });
    }
    return json(req, { erro: "Ação desconhecida." }, 400);
  } catch (e) {
    if (e instanceof ErroIG) {
      const m = MSG[e.motivo] ?? (e.codigo === 4 || e.codigo === 17 || e.codigo === 32
        ? "O Instagram limitou as consultas por um momento. Espere alguns minutos e tente de novo."
        : `O Instagram respondeu com erro (${e.status}). Tente de novo em instantes.`);
      return json(req, { erro: m }, 502);
    }
    console.error("ig-api", e);
    return json(req, { erro: "Algo deu errado aqui. Tente de novo." }, 500);
  }
});
