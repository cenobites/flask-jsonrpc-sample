'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { patronsApi } from '@/lib/api/patrons';
import { branchesApi } from '@/lib/api/organizations';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Pencil, Trash2, Mail, Building2 } from 'lucide-react';
import { formatDate } from '@/lib/utils';

export default function PatronsPage() {
  const queryClient = useQueryClient();

  const { data: patrons, isLoading } = useQuery({
    queryKey: ['patrons'],
    queryFn: patronsApi.list,
  });

  const { data: branches } = useQuery({
    queryKey: ['branches'],
    queryFn: branchesApi.list,
  });

  const deleteMutation = useMutation({
    mutationFn: patronsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patrons'] });
    },
  });

  const getBranchName = (branchId: string) => {
    return branches?.results.find((b) => b.id === branchId)?.name || branchId;
  };

  const handleDelete = async (patronId: string) => {
    if (window.confirm('Are you sure you want to delete this patron?')) {
      await deleteMutation.mutateAsync(patronId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading patrons...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Patrons</h1>
          <p className="mt-2 text-gray-600">Manage library members and their information</p>
        </div>
        <Link href="/patrons/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Patron
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Patrons ({patrons?.count || 0})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Card Number</TableHead>
                <TableHead>Branch</TableHead>
                <TableHead>Membership Expiry</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {patrons?.results.map((patron) => (
                <TableRow key={patron.id}>
                  <TableCell className="font-medium">{patron.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center text-gray-600">
                      <Mail className="mr-2 h-4 w-4" />
                      {patron.email}
                    </div>
                  </TableCell>
                  <TableCell>{patron.card_number || 'N/A'}</TableCell>
                  <TableCell>
                    <div className="flex items-center text-gray-600">
                      <Building2 className="mr-2 h-4 w-4" />
                      {getBranchName(patron.branch_id)}
                    </div>
                  </TableCell>
                  <TableCell>
                    {patron.membership_expiry ? formatDate(patron.membership_expiry) : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Link href={`/patrons/${patron.id}/edit`}>
                        <Button variant="ghost" size="sm">
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(patron.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {!patrons?.results.length && (
            <div className="py-8 text-center text-gray-500">
              No patrons found. Add your first patron to get started.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
