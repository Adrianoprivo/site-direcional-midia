// IG-CON-01 / IG-CON-05 / IG-CON-06 / IG-MET-01..04: status, perfil (com bio), posts com métricas, métricas da conta, desconectar.
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

async function posts(token: string, limite = 12) {
  const midia = await ig("me/media", token, {
    fields: "id,caption,media_type,media_product_type,permalink,thumbnail_url,media_url,timestamp,like_count,comments_count",
    limit: String(limite),
  });
  const lista = await Promise.all((midia.data ?? []).map(async (m: Record<string, string & number>) => ({
    id: m.id,
    legenda: (m.caption ?? "").slice(0, 200),
    tipo: m.media_product_type ?? m.media_type,
    link: m.permalink,
    capa: m.thumbnail_url ?? (m.media_type === "IMAGE" ? m.media_url : null),
    data: m.timestamp,
    metricas: { likes: m.like_count ?? 0, comments: m.comments_count ?? 0, ...(await metricasDoPost(m.id, token)) },
  })));
  return lista;
}

// IG-MET-04: métricas da conta. Regra do Adriano: "últimos N dias" = N dias corridos SEM o dia de hoje (fuso de São Paulo).
const METRICAS_CONTA = ["views", "reach", "accounts_engaged", "total_interactions", "likes", "comments", "shares", "saves", "profile_links_taps", "follows_and_unfollows"];
const FUSO = -3 * 3600; // São Paulo, sem horário de verão

function janela(dias: number) {
  const agoraLocal = Math.floor(Date.now() / 1000) + FUSO;
  const hojeLocal0 = agoraLocal - (agoraLocal % 86400); // 00:00 de hoje (local) em "segundos locais"
  const until = hojeLocal0 - FUSO - 1;                  // 23:59:59 de ontem, em UTC
  const since = hojeLocal0 - dias * 86400 - FUSO;       // 00:00 de N dias atrás, em UTC
  return { since, until };
}

async function metricasConta(token: string, dias: number) {
  const { since, until } = janela(dias);
  const base = { period: "day", metric_type: "total_value", since: String(since), until: String(until) };
  const saida: Record<string, number> = {};
  const juntar = (r: { data?: { name: string; total_value?: { value: number; breakdowns?: { results?: { dimension_values: string[]; value: number }[] }[] } }[] }) => {
    for (const m of r.data ?? []) {
      if (m.total_value?.breakdowns?.length) {
        for (const b of m.total_value.breakdowns[0].results ?? []) saida[`${m.name}:${b.dimension_values.join("|")}`] = b.value;
      } else saida[m.name] = m.total_value?.value ?? 0;
    }
  };
  try {
    juntar(await ig("me/insights", token, { ...base, metric: METRICAS_CONTA.join(",") }));
  } catch {
    for (const m of METRICAS_CONTA) {
      try { juntar(await ig("me/insights", token, { ...base, metric: m })); } catch { /* indisponível */ }
    }
  }
  try { // seguidores ganhos x perdidos
    juntar(await ig("me/insights", token, { ...base, metric: "follows_and_unfollows", breakdown: "follow_type" }));
  } catch { /* indisponível */ }
  return {
    dias,
    de: new Date((since - FUSO) * 1000).toISOString().slice(0, 10),
    ate: new Date((until - FUSO) * 1000).toISOString().slice(0, 10),
    m: {
      views: saida.views ?? null, reach: saida.reach ?? null, accounts_engaged: saida.accounts_engaged ?? null,
      total_interactions: saida.total_interactions ?? null, likes: saida.likes ?? null, comments: saida.comments ?? null,
      shares: saida.shares ?? null, saves: saida.saves ?? null, profile_links_taps: saida.profile_links_taps ?? null,
      seguiram: saida["follows_and_unfollows:FOLLOWER"] ?? null, deixaram: saida["follows_and_unfollows:NON_FOLLOWER"] ?? null,
    },
    quebras: Object.fromEntries(Object.entries(saida).filter(([k]) => k.includes(":"))), // conferência dos nomes da quebra
  };
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
    const { acao } = await req.json().catch(() => ({}));
    const db = admin();
    const { data: c } = await db.from("ig_conexoes")
      .select("user_id,username,access_token,obtido_em,expira_em").eq("user_id", uid).maybeSingle();

    if (acao === "status") {
      return json(req, c ? { conectado: true, usuario: c.username, expira_em: c.expira_em } : { conectado: false });
    }
    if (!c) return json(req, { erro: "Instagram não conectado." }, 409);

    if (acao === "perfil") return json(req, await perfil(await tokenValido(c as Conexao)));
    if (acao === "posts") return json(req, { posts: await posts(await tokenValido(c as Conexao)) });
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
