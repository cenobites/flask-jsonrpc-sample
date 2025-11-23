'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { patronsApi } from '@/lib/api/patrons';
import { branchesApi } from '@/lib/api/organizations';
import { PatronUpdateSchema, type PatronUpdate } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function EditPatronPage() {
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();
  const patronId = params.id as string;

  const [formData, setFormData] = useState<PatronUpdate>({
    name: '',
    email: '',
    branch_id: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data: patron, isLoading: isLoadingPatron } = useQuery({
    queryKey: ['patrons', patronId],
    queryFn: () => patronsApi.get(patronId),
  });

  const { data: branchesData } = useQuery({
    queryKey: ['branches'],
    queryFn: () => branchesApi.list(),
  });

  const branches = branchesData?.results || [];

  useEffect(() => {
    if (patron) {
      setFormData({
        name: patron.name,
        email: patron.email,
        branch_id: patron.branch_id,
      });
    }
  }, [patron]);

  const updateMutation = useMutation({
    mutationFn: (data: PatronUpdate) => patronsApi.update(patronId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patrons'] });
      queryClient.invalidateQueries({ queryKey: ['patrons', patronId] });
      router.push('/patrons');
    },
    onError: (error: Error) => {
      setErrors({ submit: error.message });
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = PatronUpdateSchema.safeParse(formData);
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

    await updateMutation.mutateAsync(formData);
  };

  if (isLoadingPatron) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading patron information...</div>
      </div>
    );
  }

  if (!patron) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-red-500">Patron not found</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/patrons">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Edit Patron</h1>
          <p className="mt-2 text-gray-600">Update patron information</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Patron Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Full Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              error={errors.name}
              placeholder="John Doe"
              required
            />

            <Input
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              error={errors.email}
              placeholder="john.doe@example.com"
              required
            />

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Branch
              </label>
              <select
                value={formData.branch_id}
                onChange={(e) => setFormData({ ...formData, branch_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select a branch</option>
                {branches.map((branch: { id: string; name: string }) => (
                  <option key={branch.id} value={branch.id}>
                    {branch.name}
                  </option>
                ))}
              </select>
              {errors.branch_id && (
                <p className="text-sm text-red-600">{errors.branch_id}</p>
              )}
            </div>

            {errors.submit && (
              <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600">
                {errors.submit}
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Updating...' : 'Update Patron'}
              </Button>
              <Link href="/patrons">
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
