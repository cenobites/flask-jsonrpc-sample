import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

interface JsonRpcRequest {
  jsonrpc: '2.0';
  method: string;
  params?: any;
  id: number | string;
}

interface JsonRpcResponse<T = any> {
  jsonrpc: '2.0';
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
  id: number | string;
}

class JsonRpcClient {
  private requestId = 1;
  private endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  async call<T = any>(method: string, params?: any): Promise<T> {
    const request: JsonRpcRequest = {
      jsonrpc: '2.0',
      method,
      params: params || [],
      id: this.requestId++,
    };

    try {
      const response = await axios.post<JsonRpcResponse<T>>(`${API_BASE_URL}/${this.endpoint}`, request, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.data.error) {
        throw new Error(response.data.error.message || 'JSON-RPC Error');
      }

      return response.data.result as T;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<JsonRpcResponse>;
        if (axiosError.response?.data?.error) {
          throw new Error(axiosError.response.data.error.message);
        }
        throw new Error(axiosError.message || 'Network error');
      }
      throw error;
    }
  }
}

export default JsonRpcClient;
