import { gateway } from "ai";
import { starterCatalog } from "./catalog";

async function main() {
  const catalog = starterCatalog();
  console.log("Alias de démarrage (env ou docs Gateway, non vérifiés live) :");
  console.log(JSON.stringify(catalog, null, 2));

  if (!process.env.AI_GATEWAY_API_KEY && !process.env.VERCEL_OIDC_TOKEN) {
    console.log(
      "Découverte live impossible : ajoute AI_GATEWAY_API_KEY ou lance `vercel env pull` (VERCEL_OIDC_TOKEN).",
    );
    console.log("Aucune des 10 API « gratuites » n’est câblée en SDK direct.");
    process.exit(2);
  }

  const available = await gateway.getAvailableModels();
  const ids = available.models.map((model) => model.id).sort();
  console.log(`Modèles Gateway disponibles : ${ids.length}`);
  for (const capability of ["light", "reasoning", "code"] as const) {
    const wanted = [catalog[capability].primary, ...catalog[capability].fallbacks];
    for (const id of wanted) {
      const ok = ids.includes(id);
      console.log(`  ${capability} ${id} : ${ok ? "OK" : "ABSENT du catalogue live"}`);
    }
  }
}

void main();
