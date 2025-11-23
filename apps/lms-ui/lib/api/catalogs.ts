import JsonRpcClient from '../api-client';
import type { Item, ItemCreate, ItemUpdate, Copy, Page } from '../schemas';

const jsonRpcClient = new JsonRpcClient('catalogs');

export const itemsApi = {
  list: async (): Promise<Page<Item>> => {
    return jsonRpcClient.call<Page<Item>>('Items.list');
  },

  get: async (itemId: string): Promise<Item> => {
    return jsonRpcClient.call<Item>('Items.get', { item_id: itemId });
  },

  create: async (data: ItemCreate): Promise<Item> => {
    return jsonRpcClient.call<Item>('Items.create', { item: data });
  },

  update: async (itemId: string, data: ItemUpdate): Promise<Item> => {
    return jsonRpcClient.call<Item>('Items.update', { item_id: itemId, item: data });
  },

  delete: async (itemId: string): Promise<boolean> => {
    return jsonRpcClient.call<boolean>('Items.delete', { item_id: itemId });
  },
};

export const copiesApi = {
  list: async (): Promise<Page<Copy>> => {
    return jsonRpcClient.call<Page<Copy>>('Copies.list');
  },

  get: async (copyId: string): Promise<Copy> => {
    return jsonRpcClient.call<Copy>('Copies.get', { copy_id: copyId });
  },
};
