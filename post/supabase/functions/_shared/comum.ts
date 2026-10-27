// Código comum das funções do Privo Post (fase 1). Ver post/docs/architecture.md.
import { createClient, type SupabaseClient } from "jsr:@supabase/supabase-js@2";

export const SITE = "https://direcionalmidia.com.br";
export const PAGINA = `${SITE}/post/`;
export const ESCOPOS = "https://www.googleapis.com/auth/business.manage openid email";
const ORIGENS = [SITE, "https://www.direcionalmidia.com.br", "http://localhost:8080"];

export function env(nome: string): string {
  const v = Deno.env.get(nome);
  if (!v) throw new Error(`Falta o segredo ${nome}`);
  return v;
}

export function urlRetorno(): string {
  return `${env("SUPABASE_URL")}/functions/v1/gbp-oauth-callback`;
}

export function cors(req: Request): Record<string, string> {
  const o = req.headers.get("Origin") ?? "";
  return {
    "Access-Control-Allow-Origin": ORIGENS.includes(o) ? o : SITE,
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

export function json(req: Request, corpo: unknown, status = 200): Response {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { ...cors(req), "Content-Type": "application/json; charset=utf-8" },
  });
}

/** Cliente com a chave de serviço: único que lê/grava gbp_conexoes e gbp_oauth_estados. */
export function admin(): SupabaseClient {
  return createClient(env("SUPABASE_URL"), env("SUPABASE_SERVICE_ROLE_KEY"), {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}

/** Confere o login do Supabase enviado pela página e devolve o id do usuário (ou null). */
export async function usuario(req: Request): Promise<string | null> {
  const auth = req.headers.get("Authorization") ?? "";
  const token = auth.replace(/^Bearer\s+/i, "");
  if (!token) return null;
  const { data, error } = await admin().auth.getUser(token);
  if (error || !data?.user) return null;
  return data.user.id;
}
