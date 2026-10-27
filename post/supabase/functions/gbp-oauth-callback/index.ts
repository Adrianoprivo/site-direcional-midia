// CON-02 / CON-03 / CON-04: o Google chama aqui depois do "Permitir". Pública (verify_jwt = false):
// a proteção é o código de estado de uso único criado por gbp-oauth-start.
import { admin, env, PAGINA, urlRetorno } from "../_shared/comum.ts";

const volta = (r: string) => new Response(null, { status: 302, headers: { Location: `${PAGINA}?google=${r}` } });

function emailDoIdToken(idToken?: string): string | null {
  // O id_token veio direto do endpoint de token do Google (HTTPS), então basta ler o conteúdo.
  if (!idToken) return null;
  try {
    const b64 = idToken.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const p = JSON.parse(atob(b64 + "=".repeat((4 - (b64.length % 4)) % 4)));
    return typeof p.email === "string" ? p.email : null;
  } catch {
    return null;
  }
}

Deno.serve(async (req) => {
  const u = new URL(req.url);
  const estado = u.searchParams.get("state");
  const code = u.searchParams.get("code");
  const erroGoogle = u.searchParams.get("error");
  if (!estado) return volta("erro");

  const db = admin();
  try {
    // Marca o código como usado de forma atômica: só passa se existe, não venceu e nunca foi usado.
    const { data: linha, error: e1 } = await db
      .from("gbp_oauth_estados")
      .update({ usado_em: new Date().toISOString() })
      .eq("estado", estado)
      .is("usado_em", null)
      .gt("expira_em", new Date().toISOString())
      .select("user_id")
      .maybeSingle();
    if (e1) throw e1;
    if (!linha) return volta("expirado");
    if (erroGoogle) return volta(erroGoogle === "access_denied" ? "cancelado" : "erro");
    if (!code) return volta("erro");

    const r = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        code,
        client_id: env("GOOGLE_CLIENT_ID"),
        client_secret: env("GOOGLE_CLIENT_SECRET"),
        redirect_uri: urlRetorno(),
        grant_type: "authorization_code",
      }),
    });
    const t = await r.json();
    if (!r.ok || !t.refresh_token) {
      console.error("gbp-oauth-callback token", r.status, t?.error, t?.error_description);
      return volta("erro");
    }
    if (!String(t.scope ?? "").includes("business.manage")) return volta("sem-permissao");

    const { error: e2 } = await db.from("gbp_conexoes").upsert({
      user_id: linha.user_id,
      google_email: emailDoIdToken(t.id_token) ?? "(e-mail não informado)",
      refresh_token: t.refresh_token,
      access_token: t.access_token,
      expira_em: new Date(Date.now() + (Number(t.expires_in) - 60) * 1000).toISOString(),
      escopos: t.scope,
      atualizado_em: new Date().toISOString(),
    });
    if (e2) throw e2;
    return volta("conectado");
  } catch (e) {
    console.error("gbp-oauth-callback", e);
    return volta("erro");
  }
});
