'use client';

import { useQuery } from '@tanstack/react-query';
import { staffApi } from '@/lib/api/organizations';
import { branchesApi } from '@/lib/api/organizations';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Plus, Mail, Building2 } from 'lucide-react';
import type { Staff, Branch } from '@/lib/schemas';

export default function StaffPage() {
  const { data: staff, isLoading } = useQuery({
    queryKey: ['staff'],
    queryFn: staffApi.list,
  });

  const { data: branches } = useQuery({
    queryKey: ['branches'],
    queryFn: branchesApi.list,
  });

  const getBranchName = (branchId: string) => {
    return branches?.results.find((b: Branch) => b.id === branchId)?.name || branchId;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading staff...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Staff</h1>
          <p className="mt-2 text-gray-600">Manage library staff members</p>
        </div>
        <Link href="/staff/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Staff Member
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Staff ({staff?.count || 0})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Branch</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {staff?.results.map((member: Staff) => (
                <TableRow key={member.id}>
                  <TableCell className="font-medium">{member.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center text-gray-600">
                      <Mail className="mr-2 h-4 w-4" />
                      {member.email}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                      {member.role || 'Staff'}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center text-gray-600">
                      <Building2 className="mr-2 h-4 w-4" />
                      {getBranchName(member.branch_id)}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {!staff?.results.length && (
            <div className="py-8 text-center text-gray-500">
              No staff members found.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
