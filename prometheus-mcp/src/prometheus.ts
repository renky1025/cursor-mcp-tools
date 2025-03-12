import axios from 'axios';
import { Config } from './config';
import { PrometheusQuery, PrometheusResponse } from './types';

export class PrometheusClient {
  private readonly baseUrl: string;
  private readonly timeout: number;
  private readonly headers: Record<string, string>;

  constructor(config: Config) {
    console.error('Initializing PrometheusClient with config:', {
      url: config.prometheusUrl,
      timeout: config.timeout,
      headers: config.headers
    });
    
    this.baseUrl = config.prometheusUrl;
    this.timeout = config.timeout;
    this.headers = {
      'Accept': 'application/json',
      ...config.headers || {}
    };

    console.error('Initialized client with:', {
      baseUrl: this.baseUrl,
      timeout: this.timeout,
      headers: this.headers
    });
  }

  async query(params: PrometheusQuery): Promise<PrometheusResponse> {
    try {
      console.error('Query params received:', params);

      const endpoint = params.type === 'instant' ? 'query' : 'query_range';
      const queryParams: Record<string, string> = {
        query: params.query,
      };

      if (params.type === 'range') {
        if (!params.start || !params.end || !params.step) {
          throw new Error('Range queries require start, end, and step parameters');
        }
        queryParams.start = params.start;
        queryParams.end = params.end;
        queryParams.step = params.step;
      }

      const url = `${this.baseUrl}/api/v1/${endpoint}`;
      console.error('Making request to:', {
        url,
        params: queryParams,
        timeout: this.timeout,
        headers: this.headers
      });

      const response = await axios.get<PrometheusResponse>(url, {
        params: queryParams,
        timeout: this.timeout,
        headers: this.headers,
        validateStatus: null // 允许所有状态码
      });

      console.error('Response received:', {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        data: response.data
      });

      if (response.status >= 400) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.data;
    } catch (error) {
      console.error('Error occurred in query:', error);

      if (axios.isAxiosError(error)) {
        console.error('Detailed error information:', {
          message: error.message,
          code: error.code,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          config: {
            url: error.config?.url,
            method: error.config?.method,
            headers: error.config?.headers,
            params: error.config?.params,
            timeout: error.config?.timeout
          }
        });
        
        return {
          status: 'error',
          error: `Network error: ${error.message}`,
          errorType: 'network_error',
        };
      }

      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        errorType: 'unknown',
      };
    }
  }
}