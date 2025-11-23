'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { branchesApi } from '@/lib/api/organizations';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Pencil, Trash2, Mail, Phone, MapPin } from 'lucide-react';

export default function BranchesPage() {
  const queryClient = useQueryClient();

  const { data: branches, isLoading } = useQuery({
    queryKey: ['branches'],
    queryFn: branchesApi.list,
  });

  const deleteMutation = useMutation({
    mutationFn: branchesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['branches'] });
    },
  });

  const handleDelete = async (branchId: string) => {
    if (window.confirm('Are you sure you want to delete this branch?')) {
      await deleteMutation.mutateAsync(branchId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading branches...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Branches</h1>
          <p className="mt-2 text-gray-600">Manage library branch locations</p>
        </div>
        <Link href="/branches/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Branch
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Branches ({branches?.count || 0})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Address</TableHead>
                <TableHead>Phone</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {branches?.results.map((branch) => (
                <TableRow key={branch.id}>
                  <TableCell className="font-medium">{branch.name}</TableCell>
                  <TableCell>
                    {branch.address ? (
                      <div className="flex items-center text-gray-600">
                        <MapPin className="mr-2 h-4 w-4" />
                        {branch.address}
                      </div>
                    ) : (
                      'N/A'
                    )}
                  </TableCell>
                  <TableCell>
                    {branch.phone ? (
                      <div className="flex items-center text-gray-600">
                        <Phone className="mr-2 h-4 w-4" />
                        {branch.phone}
                      </div>
                    ) : (
                      'N/A'
                    )}
                  </TableCell>
                  <TableCell>
                    {branch.email ? (
                      <div className="flex items-center text-gray-600">
                        <Mail className="mr-2 h-4 w-4" />
                        {branch.email}
                      </div>
                    ) : (
                      'N/A'
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Link href={`/branches/${branch.id}/edit`}>
                        <Button variant="ghost" size="sm">
                          <Pencil className="h-4 w-4" />
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(branch.id)}
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
          {!branches?.results.length && (
            <div className="py-8 text-center text-gray-500">
              No branches found. Add your first branch to get started.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
