import { z } from 'zod';

export const BlueprintTypeSchema = z.enum(['commerce', 'restaurant', 'services']);
export type BlueprintType = z.infer<typeof BlueprintTypeSchema>;

export const HealthCheckResponseSchema = z.object({
  status: z.string(),
  service: z.string(),
  timestamp: z.string(),
});
export type HealthCheckResponse = z.infer<typeof HealthCheckResponseSchema>;
