import { z } from 'zod';

// Common schemas
export const PageSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    results: z.array(itemSchema),
    count: z.number(),
  });

// Patron schemas
export const PatronSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  card_number: z.string().optional(),
  membership_expiry: z.string().optional(),
  branch_id: z.string(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const PatronCreateSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Valid email is required'),
  branch_id: z.string().min(1, 'Branch is required'),
});

export const PatronUpdateSchema = PatronCreateSchema.partial();

// Branch schemas
export const BranchSchema = z.object({
  id: z.string(),
  name: z.string(),
  address: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const BranchCreateSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  address: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email().optional().or(z.literal('')),
});

export const BranchUpdateSchema = BranchCreateSchema.partial();

// Staff schemas
export const StaffSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  role: z.string().optional(),
  branch_id: z.string(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const StaffCreateSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Valid email is required'),
  role: z.string().optional(),
  branch_id: z.string().min(1, 'Branch is required'),
});

export const StaffUpdateSchema = StaffCreateSchema.partial();

// Catalog Item schemas
export const ItemSchema = z.object({
  id: z.string(),
  title: z.string(),
  author: z.string().optional(),
  isbn: z.string().optional(),
  publication_year: z.number().optional(),
  format: z.string().optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const ItemCreateSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  author: z.string().optional(),
  isbn: z.string().optional(),
  publication_year: z.number().optional(),
  format: z.string().optional(),
});

export const ItemUpdateSchema = ItemCreateSchema.partial();

// Copy schemas
export const CopySchema = z.object({
  id: z.string(),
  item_id: z.string(),
  barcode: z.string(),
  status: z.string(),
  branch_id: z.string(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

// Loan schemas
export const LoanSchema = z.object({
  id: z.string(),
  patron_id: z.string(),
  copy_id: z.string(),
  checkout_date: z.string(),
  due_date: z.string(),
  return_date: z.string().optional().nullable(),
  staff_out_id: z.string(),
  staff_in_id: z.string().optional().nullable(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const LoanCreateSchema = z.object({
  patron_id: z.string().min(1, 'Patron is required'),
  copy_id: z.string().min(1, 'Copy is required'),
  staff_id: z.string().min(1, 'Staff is required'),
});

// Hold schemas
export const HoldSchema = z.object({
  id: z.string(),
  patron_id: z.string(),
  item_id: z.string(),
  hold_date: z.string(),
  expiry_date: z.string().optional().nullable(),
  status: z.string(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

// Types
export type Patron = z.infer<typeof PatronSchema>;
export type PatronCreate = z.infer<typeof PatronCreateSchema>;
export type PatronUpdate = z.infer<typeof PatronUpdateSchema>;

export type Branch = z.infer<typeof BranchSchema>;
export type BranchCreate = z.infer<typeof BranchCreateSchema>;
export type BranchUpdate = z.infer<typeof BranchUpdateSchema>;

export type Staff = z.infer<typeof StaffSchema>;
export type StaffCreate = z.infer<typeof StaffCreateSchema>;
export type StaffUpdate = z.infer<typeof StaffUpdateSchema>;

export type Item = z.infer<typeof ItemSchema>;
export type ItemCreate = z.infer<typeof ItemCreateSchema>;
export type ItemUpdate = z.infer<typeof ItemUpdateSchema>;

export type Copy = z.infer<typeof CopySchema>;

export type Loan = z.infer<typeof LoanSchema>;
export type LoanCreate = z.infer<typeof LoanCreateSchema>;

export type Hold = z.infer<typeof HoldSchema>;

export type Page<T> = {
  results: T[];
  count: number;
};
