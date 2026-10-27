// CON-02 / CON-04: cria o código de proteção e devolve o endereço da tela de permissão do Google.
import { admin, cors, env, ESCOPOS, json, urlRetorno, usuario } from "../_shared/comum.ts";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors(req) });
  if (req.method !== "POST") return json(req, { erro: "Método não permitido." }, 405);
  try {
    const uid = await usuario(req);
    if (!uid) return json(req, { erro: "Entre de novo para continuar." }, 401);

    const bytes = crypto.getRandomValues(new Uint8Array(32));
    const estado = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
    const db = admin();
    // limpa códigos vencidos deste usuário
    await db.from("gbp_oauth_estados").delete().eq("user_id", uid).lt("expira_em", new Date().toISOString());
    const { error } = await db.from("gbp_oauth_estados").insert({
      estado,
      user_id: uid,
      expira_em: new Date(Date.now() + 10 * 60 * 1000).toISOString(),
    });
    if (error) throw error;

    const p = new URLSearchParams({
      client_id: env("GOOGLE_CLIENT_ID"),
      redirect_uri: urlRetorno(),
      response_type: "code",
      scope: ESCOPOS,
      access_type: "offline",
      prompt: "consent",
      include_granted_scopes: "true",
      state: estado,
    });
    return json(req, { url: `https://accounts.google.com/o/oauth2/v2/auth?${p}` });
  } catch (e) {
    console.error("gbp-oauth-start", e);
    return json(req, { erro: "Não deu para iniciar a conexão. Tente de novo." }, 500);
  }
});
