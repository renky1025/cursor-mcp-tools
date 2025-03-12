import { z } from 'zod';

export interface Config {
  prometheusUrl: string;
  timeout: number;
  headers?: Record<string, string>;
}

const ConfigSchema = z.object({
  prometheusUrl: z.string().url(),
  timeout: z.number().positive().default(30000),
  headers: z.record(z.string()).optional(),
});

export function loadConfig(): Config {
  const headers: Record<string, string> = {
    'Accept': 'application/json',
  };

  if (process.env.PROMETHEUS_AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${process.env.PROMETHEUS_AUTH_TOKEN}`;
  }

  const config = {
    prometheusUrl: process.env.PROMETHEUS_URL || 'http://10.100.0.4:32002',
    timeout: parseInt(process.env.PROMETHEUS_TIMEOUT || '30000'),
    headers,
  };

  return ConfigSchema.parse(config);
}