// IG-CON-02 / IG-CON-03 / IG-CON-04: o Instagram chama aqui depois do "Permitir". Pública (verify_jwt = false):
// a proteção é o código de estado de uso único criado por ig-oauth-start.
import { admin, env, PAGINA } from "../_shared/comum.ts";

const volta = (r: string) => new Response(null, { status: 302, headers: { Location: `${PAGINA}?instagram=${r}` } });

Deno.serve(async (req) => {
  const u = new URL(req.url);
  const estado = u.searchParams.get("state");
  const code = (u.searchParams.get("code") ?? "").replace(/#_$/, "");
  const erro = u.searchParams.get("error");
  if (!estado) return volta("erro");

  const db = admin();
  try {
    const { data: linha, error: e1 } = await db
      .from("ig_oauth_estados")
      .update({ usado_em: new Date().toISOString() })
      .eq("estado", estado)
      .is("usado_em", null)
      .gt("expira_em", new Date().toISOString())
      .select("user_id")
      .maybeSingle();
    if (e1) throw e1;
    if (!linha) return volta("expirado");
    if (erro) return volta(erro === "access_denied" ? "cancelado" : "erro");
    if (!code) return volta("erro");

    // 1) código -> token curto (1 h)
    const r1 = await fetch("https://api.instagram.com/oauth/access_token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: env("IG_APP_ID"),
        client_secret: env("IG_APP_SECRET"),
        grant_type: "authorization_code",
        redirect_uri: `${env("SUPABASE_URL")}/functions/v1/ig-oauth-callback`,
        code,
      }),
    });
    const j1 = await r1.json();
    const curto = Array.isArray(j1?.data) ? j1.data[0] : j1; // a doc mostra os dois formatos
    if (!r1.ok || !curto?.access_token) {
      console.error("ig-oauth-callback curto", r1.status, j1?.error_type ?? j1?.error?.type, j1?.error_message ?? j1?.error?.message);
      return volta("erro");
    }
    const permissoes = String(curto.permissions ?? "");
    if (!permissoes.includes("instagram_business_content_publish")) return volta("sem-permissao");

    // 2) token curto -> token longo (60 dias)
    const r2 = await fetch(`https://graph.instagram.com/access_token?${new URLSearchParams({
      grant_type: "ig_exchange_token",
      client_secret: env("IG_APP_SECRET"),
      access_token: curto.access_token,
    })}`);
    const longo = await r2.json();
    if (!r2.ok || !longo?.access_token) {
      console.error("ig-oauth-callback longo", r2.status, longo?.error?.type, longo?.error?.message);
      return volta("erro");
    }

    // 3) nome de usuário (só para mostrar)
    let username: string | null = null;
    try {
      const r3 = await fetch(`https://graph.instagram.com/me?fields=user_id,username&access_token=${encodeURIComponent(longo.access_token)}`);
      const me = await r3.json();
      if (r3.ok) username = me.username ?? null;
    } catch (_) { /* segue sem o nome */ }

    const agora = Date.now();
    const { error: e2 } = await db.from("ig_conexoes").upsert({
      user_id: linha.user_id,
      ig_user_id: String(curto.user_id),
      username,
      access_token: longo.access_token,
      obtido_em: new Date(agora).toISOString(),
      expira_em: new Date(agora + Number(longo.expires_in ?? 5184000) * 1000).toISOString(),
      permissoes,
      atualizado_em: new Date(agora).toISOString(),
    });
    if (e2) throw e2;
    return volta("conectado");
  } catch (e) {
    console.error("ig-oauth-callback", e);
    return volta("erro");
  }
});
