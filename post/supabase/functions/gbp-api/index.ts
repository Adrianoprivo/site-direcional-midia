// CON-01 / CON-05 / CON-06 / PER-01..03: status, lista de perfis e desconectar. Só leitura no Google.
import { admin, cors, env, json, usuario } from "../_shared/comum.ts";

type Conexao = { user_id: string; google_email: string; refresh_token: string; access_token: string | null; expira_em: string | null };

class ErroGoogle extends Error {
  constructor(public status: number, public motivo: string) { super(motivo); }
}

async function acessoValido(c: Conexao): Promise<string> {
  if (c.access_token && c.expira_em && new Date(c.expira_em).getTime() > Date.now()) return c.access_token;
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: env("GOOGLE_CLIENT_ID"),
      client_secret: env("GOOGLE_CLIENT_SECRET"),
      refresh_token: c.refresh_token,
      grant_type: "refresh_token",
    }),
  });
  const t = await r.json();
  if (!r.ok) throw new ErroGoogle(401, t?.error === "invalid_grant" ? "reconectar" : "token");
  await admin().from("gbp_conexoes").update({
    access_token: t.access_token,
    expira_em: new Date(Date.now() + (Number(t.expires_in) - 60) * 1000).toISOString(),
    atualizado_em: new Date().toISOString(),
  }).eq("user_id", c.user_id);
  return t.access_token;
}

async function google(url: string, token: string) {
  const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  const corpo = await r.json().catch(() => ({}));
  if (!r.ok) {
    console.error("google", r.status, url.split("?")[0], corpo?.error?.status, corpo?.error?.message);
    throw new ErroGoogle(r.status, corpo?.error?.status ?? "erro");
  }
  return corpo;
}

const SEU_PERFIL = /direcional\s*m[ií]dia/i; // PER-02: o resto é cliente até o Adriano liberar

function endereco(a?: { addressLines?: string[]; locality?: string; administrativeArea?: string }) {
  if (!a) return "";
  return [...(a.addressLines ?? []), a.locality, a.administrativeArea].filter(Boolean).join(", ");
}

async function listarPerfis(token: string) {
  const contas: unknown[] = [];
  let pg = "";
  do {
    const r = await google(`https://mybusinessaccountmanagement.googleapis.com/v1/accounts?pageSize=20${pg ? `&pageToken=${pg}` : ""}`, token);
    contas.push(...(r.accounts ?? []));
    pg = r.nextPageToken ?? "";
  } while (pg);

  const saida = [];
  for (const c of contas as { name: string; accountName?: string; type?: string }[]) {
    const perfis = [];
    let p = "";
    do {
      const r = await google(
        `https://mybusinessbusinessinformation.googleapis.com/v1/${c.name}/locations?readMask=name,title,storefrontAddress&pageSize=100${p ? `&pageToken=${p}` : ""}`,
        token,
      );
      for (const l of r.locations ?? []) {
        perfis.push({ id: l.name, nome: l.title ?? "(sem nome)", endereco: endereco(l.storefrontAddress), cliente: !SEU_PERFIL.test(l.title ?? "") });
      }
      p = r.nextPageToken ?? "";
    } while (p);
    saida.push({ id: c.name, nome: c.accountName ?? c.name, tipo: c.type ?? "", perfis });
  }
  return saida;
}

const MSG: Record<string, string> = {
  reconectar: "A autorização do Google venceu ou foi cancelada. Clique em Desconectar e conecte de novo.",
  RESOURCE_EXHAUSTED: "O Google limitou as consultas por um momento (cota). Espere 1 minuto e tente de novo.",
  PERMISSION_DENIED: "O Google negou o acesso. Confira se as APIs do Perfil da Empresa estão ativadas no projeto Privo Post.",
  UNAUTHENTICATED: "A autorização do Google não vale mais. Desconecte e conecte de novo.",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors(req) });
  if (req.method !== "POST") return json(req, { erro: "Método não permitido." }, 405);
  try {
    const uid = await usuario(req);
    if (!uid) return json(req, { erro: "Entre de novo para continuar." }, 401);
    const { acao } = await req.json().catch(() => ({}));
    const db = admin();
    const { data: c } = await db.from("gbp_conexoes")
      .select("user_id,google_email,refresh_token,access_token,expira_em").eq("user_id", uid).maybeSingle();

    if (acao === "status") return json(req, c ? { conectado: true, email: c.google_email } : { conectado: false });
    if (!c) return json(req, { erro: "Google não conectado." }, 409);

    if (acao === "perfis") return json(req, { contas: await listarPerfis(await acessoValido(c as Conexao)) });

    if (acao === "desconectar") {
      await fetch(`https://oauth2.googleapis.com/revoke?token=${encodeURIComponent(c.refresh_token)}`, {
        method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }).catch((e) => console.error("revoke", e));
      await db.from("gbp_conexoes").delete().eq("user_id", uid);
      return json(req, { conectado: false });
    }
    return json(req, { erro: "Ação desconhecida." }, 400);
  } catch (e) {
    if (e instanceof ErroGoogle) return json(req, { erro: MSG[e.motivo] ?? `O Google respondeu com erro (${e.status}). Tente de novo em instantes.` }, 502);
    console.error("gbp-api", e);
    return json(req, { erro: "Algo deu errado aqui. Tente de novo." }, 500);
  }
});
