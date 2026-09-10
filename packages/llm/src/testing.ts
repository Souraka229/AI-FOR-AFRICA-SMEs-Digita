import { MockLanguageModelV3 } from "ai/test";

export function mockStructuredModel(
  output: unknown,
  usage: { input?: number; output?: number; cacheRead?: number } = {},
) {
  const input = usage.input ?? 12;
  const outputTokens = usage.output ?? 8;
  const cacheRead = usage.cacheRead ?? 0;
  return new MockLanguageModelV3({
    doGenerate: async () => ({
      content: [{ type: "text", text: JSON.stringify(output) }],
      finishReason: { unified: "stop", raw: undefined },
      usage: {
        inputTokens: {
          total: input,
          noCache: input - cacheRead,
          cacheRead,
          cacheWrite: undefined,
        },
        outputTokens: {
          total: outputTokens,
          text: outputTokens,
          reasoning: undefined,
        },
      },
      warnings: [],
    }),
  });
}

export function mockStructuredSequence(outputs: unknown[]) {
  let index = 0;
  return new MockLanguageModelV3({
    doGenerate: async () => {
      const value = outputs[Math.min(index, outputs.length - 1)];
      index += 1;
      return {
        content: [
          {
            type: "text" as const,
            text: typeof value === "string" ? value : JSON.stringify(value),
          },
        ],
        finishReason: { unified: "stop" as const, raw: undefined },
        usage: {
          inputTokens: {
            total: 5,
            noCache: 5,
            cacheRead: undefined,
            cacheWrite: undefined,
          },
          outputTokens: {
            total: 5,
            text: 5,
            reasoning: undefined,
          },
        },
        warnings: [],
      };
    },
  });
}
