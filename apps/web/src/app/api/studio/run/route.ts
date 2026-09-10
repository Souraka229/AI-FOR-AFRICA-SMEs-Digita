import { runPipeline } from "@/lib/agents/pipeline";
import { guardStudio } from "@/lib/agents/guard";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(request: Request) {
  const denied = guardStudio(request);
  if (denied) return denied;
  const body = (await request.json()) as { prompt?: string };
  const prompt = body.prompt?.trim() ?? "";
  if (prompt.length < 8 || prompt.length > 2_000) {
    return Response.json(
      { error: "Décrivez l’activité en 8 à 2 000 caractères." },
      { status: 400 },
    );
  }

  const encoder = new TextEncoder();
  const abortController = new AbortController();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (payload: unknown) => {
        controller.enqueue(encoder.encode(`${JSON.stringify(payload)}\n`));
      };
      try {
        const result = await runPipeline(prompt, {
          onStep: (event) => send({ type: "step", ...event }),
          abortSignal: abortController.signal,
        });
        if (result.gate1.passed) {
          send({
            type: "step",
            id: "preview",
            status: "blocked",
            data: { reason: "approbation humaine requise" },
          });
        }
        send({ type: "result", ...result });
      } catch (error) {
        send({
          type: "error",
          message:
            error instanceof Error
              ? error.message
              : "La génération LLM a échoué.",
        });
      } finally {
        controller.close();
      }
    },
    cancel() {
      abortController.abort();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "application/x-ndjson; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
