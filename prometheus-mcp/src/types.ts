import { z } from 'zod';

export const QueryType = z.enum(["instant", "range"]);

export interface PrometheusQuery {
  query: string;
  type: "instant" | "range";
  start?: string;
  end?: string;
  step?: string;
}

export interface PrometheusResponse {
  status: 'success' | 'error';
  data?: {
    resultType: string;
    result: Array<{
      metric: Record<string, string>;
      value?: [number, string];
      values?: [number, string][];
    }>;
  };
  error?: string;
  errorType?: string;
}

export const PrometheusQuerySchema = {
  query: z.string(),
  type: QueryType,
  start: z.string().optional(),
  end: z.string().optional(),
  step: z.string().optional(),
} as const;