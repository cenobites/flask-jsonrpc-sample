import JsonRpcClient from '../api-client';
import type { Loan, LoanCreate, Hold, Page } from '../schemas';

const jsonRpcClient = new JsonRpcClient('circulations');

export const loansApi = {
  list: async (): Promise<Page<Loan>> => {
    return jsonRpcClient.call<Page<Loan>>('Loans.list');
  },

  get: async (loanId: string): Promise<Loan> => {
    return jsonRpcClient.call<Loan>('Loans.get', { loan_id: loanId });
  },

  checkout: async (data: LoanCreate): Promise<Loan> => {
    return jsonRpcClient.call<Loan>('Loans.checkout_copy', data);
  },

  checkin: async (loanId: string, staffId: string): Promise<Loan> => {
    return jsonRpcClient.call<Loan>('Loans.checkin_copy', { loan_id: loanId, staff_id: staffId });
  },

  renew: async (loanId: string): Promise<Loan> => {
    return jsonRpcClient.call<Loan>('Loans.renew', { loan_id: loanId });
  },
};

export const holdsApi = {
  list: async (): Promise<Page<Hold>> => {
    return jsonRpcClient.call<Page<Hold>>('Holds.list');
  },

  get: async (holdId: string): Promise<Hold> => {
    return jsonRpcClient.call<Hold>('Holds.get', { hold_id: holdId });
  },

  place: async (patronId: string, itemId: string): Promise<Hold> => {
    return jsonRpcClient.call<Hold>('Holds.place', { patron_id: patronId, item_id: itemId });
  },

  cancel: async (holdId: string): Promise<boolean> => {
    return jsonRpcClient.call<boolean>('Holds.cancel', { hold_id: holdId });
  },
};
