import JsonRpcClient from '../api-client';
import type { Branch, BranchCreate, BranchUpdate, Staff, StaffCreate, StaffUpdate, Page } from '../schemas';

const jsonRpcClient = new JsonRpcClient('organizations');

export const branchesApi = {
  list: async (): Promise<Page<Branch>> => {
    return jsonRpcClient.call<Page<Branch>>('Branches.list');
  },

  get: async (branchId: string): Promise<Branch> => {
    return jsonRpcClient.call<Branch>('Branches.get', { branch_id: branchId });
  },

  create: async (data: BranchCreate): Promise<Branch> => {
    return jsonRpcClient.call<Branch>('Branches.create', { branch: data });
  },

  update: async (branchId: string, data: BranchUpdate): Promise<Branch> => {
    return jsonRpcClient.call<Branch>('Branches.update', { branch_id: branchId, branch: data });
  },

  delete: async (branchId: string): Promise<boolean> => {
    return jsonRpcClient.call<boolean>('Branches.delete', { branch_id: branchId });
  },
};

export const staffApi = {
  list: async (): Promise<Page<Staff>> => {
    return jsonRpcClient.call<Page<Staff>>('Staff.list');
  },

  get: async (staffId: string): Promise<Staff> => {
    return jsonRpcClient.call<Staff>('Staff.get', { staff_id: staffId });
  },

  create: async (data: StaffCreate): Promise<Staff> => {
    return jsonRpcClient.call<Staff>('Staff.create', { staff: data });
  },

  update: async (staffId: string, data: StaffUpdate): Promise<Staff> => {
    return jsonRpcClient.call<Staff>('Staff.update', { staff_id: staffId, staff: data });
  },

  delete: async (staffId: string): Promise<boolean> => {
    return jsonRpcClient.call<boolean>('Staff.delete', { staff_id: staffId });
  },
};
