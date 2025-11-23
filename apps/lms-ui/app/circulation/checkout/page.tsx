'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { loansApi } from '@/lib/api/circulations';
import { patronsApi } from '@/lib/api/patrons';
import { copiesApi } from '@/lib/api/catalogs';
import { staffApi } from '@/lib/api/organizations';
import { LoanCreateSchema, type LoanCreate } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function CheckoutPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<LoanCreate>({
    patron_id: '',
    copy_id: '',
    staff_id: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data: patrons } = useQuery({
    queryKey: ['patrons'],
    queryFn: patronsApi.list,
  });

  const { data: staff } = useQuery({
    queryKey: ['staff'],
    queryFn: staffApi.list,
  });

  const checkoutMutation = useMutation({
    mutationFn: loansApi.checkout,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      router.push('/circulation');
    },
    onError: (error: Error) => {
      setErrors({ submit: error.message });
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = LoanCreateSchema.safeParse(formData);
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.issues.forEach((err) => {
        if (err.path[0]) {
          fieldErrors[err.path[0].toString()] = err.message;
        }
      });
      setErrors(fieldErrors);
      return;
    }

    await checkoutMutation.mutateAsync(formData);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/circulation">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Check Out Item</h1>
          <p className="mt-2 text-gray-600">Loan an item to a patron</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Checkout Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">
                Patron
              </label>
              <select
                value={formData.patron_id}
                onChange={(e) => setFormData({ ...formData, patron_id: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              >
                <option value="">Select a patron</option>
                {patrons?.results.map((patron) => (
                  <option key={patron.id} value={patron.id}>
                    {patron.name} ({patron.email})
                  </option>
                ))}
              </select>
              {errors.patron_id && <p className="mt-1 text-sm text-red-600">{errors.patron_id}</p>}
            </div>

            <Input
              label="Copy ID / Barcode"
              value={formData.copy_id}
              onChange={(e) => setFormData({ ...formData, copy_id: e.target.value })}
              error={errors.copy_id}
              placeholder="Scan or enter copy barcode"
              required
            />

            <div>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">
                Staff Member
              </label>
              <select
                value={formData.staff_id}
                onChange={(e) => setFormData({ ...formData, staff_id: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                required
              >
                <option value="">Select staff member</option>
                {staff?.results.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.name}
                  </option>
                ))}
              </select>
              {errors.staff_id && <p className="mt-1 text-sm text-red-600">{errors.staff_id}</p>}
            </div>

            {errors.submit && (
              <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600">
                {errors.submit}
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={checkoutMutation.isPending}>
                {checkoutMutation.isPending ? 'Processing...' : 'Check Out'}
              </Button>
              <Link href="/circulation">
                <Button type="button" variant="secondary">
                  Cancel
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
