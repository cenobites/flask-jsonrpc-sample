import JsonRpcClient from '../api-client';
import type { Patron, PatronCreate, PatronUpdate, Page } from '../schemas';

const jsonRpcClient = new JsonRpcClient('patrons');

export const patronsApi = {
  list: async (): Promise<Page<Patron>> => {
    return jsonRpcClient.call<Page<Patron>>('Patrons.list');
  },

  get: async (patronId: string): Promise<Patron> => {
    return jsonRpcClient.call<Patron>('Patrons.get', { patron_id: patronId });
  },

  create: async (data: PatronCreate): Promise<Patron> => {
    return jsonRpcClient.call<Patron>('Patrons.create', { patron: data });
  },

  update: async (patronId: string, data: PatronUpdate): Promise<Patron> => {
    return jsonRpcClient.call<Patron>('Patrons.update', { patron_id: patronId, patron: data });
  },

  delete: async (patronId: string): Promise<boolean> => {
    return jsonRpcClient.call<boolean>('Patrons.delete', { patron_id: patronId });
  },
};
