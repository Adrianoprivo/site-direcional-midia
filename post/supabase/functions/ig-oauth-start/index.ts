// IG-CON-02 / IG-CON-04: cria o código de proteção e devolve o endereço da tela de permissão do Instagram.
import { admin, cors, env, json, usuario } from "../_shared/comum.ts";

const ESCOPOS_IG = "instagram_business_basic,instagram_business_content_publish,instagram_business_manage_insights";

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors(req) });
  if (req.method !== "POST") return json(req, { erro: "Método não permitido." }, 405);
  try {
    const uid = await usuario(req);
    if (!uid) return json(req, { erro: "Entre de novo para continuar." }, 401);

    const bytes = crypto.getRandomValues(new Uint8Array(32));
    const estado = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
    const db = admin();
    await db.from("ig_oauth_estados").delete().eq("user_id", uid).lt("expira_em", new Date().toISOString());
    const { error } = await db.from("ig_oauth_estados").insert({
      estado,
      user_id: uid,
      expira_em: new Date(Date.now() + 10 * 60 * 1000).toISOString(),
    });
    if (error) throw error;

    const p = new URLSearchParams({
      client_id: env("IG_APP_ID"),
      redirect_uri: `${env("SUPABASE_URL")}/functions/v1/ig-oauth-callback`,
      response_type: "code",
      scope: ESCOPOS_IG,
      state: estado,
      enable_fb_login: "false",
    });
    return json(req, { url: `https://www.instagram.com/oauth/authorize?${p}` });
  } catch (e) {
    console.error("ig-oauth-start", e);
    return json(req, { erro: "Não deu para iniciar a conexão com o Instagram. Tente de novo." }, 500);
  }
});
