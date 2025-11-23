'use client';

import { useQuery } from '@tanstack/react-query';
import { loansApi, holdsApi } from '@/lib/api/circulations';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { ArrowLeftRight, BookMarked, Plus } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import Link from 'next/link';

export default function CirculationPage() {
  const { data: loans, isLoading: loansLoading } = useQuery({
    queryKey: ['loans'],
    queryFn: loansApi.list,
  });

  const { data: holds, isLoading: holdsLoading } = useQuery({
    queryKey: ['holds'],
    queryFn: holdsApi.list,
  });

  const activeLoans = loans?.results.filter((loan) => !loan.return_date) || [];
  const overdueLoans =
    activeLoans.filter((loan) => new Date(loan.due_date) < new Date()) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Circulation</h1>
          <p className="mt-2 text-gray-600">Manage loans, returns, and holds</p>
        </div>
        <Link href="/circulation/checkout">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Check Out Item
          </Button>
        </Link>
      </div>

      <div className="grid gap-6 sm:grid-cols-3">
        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Loans</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{activeLoans.length}</p>
            </div>
            <div className="rounded-lg bg-blue-50 p-3">
              <ArrowLeftRight className="h-6 w-6 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm font-medium text-gray-600">Overdue</p>
              <p className="mt-2 text-3xl font-bold text-red-600">{overdueLoans.length}</p>
            </div>
            <div className="rounded-lg bg-red-50 p-3">
              <ArrowLeftRight className="h-6 w-6 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Holds</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{holds?.count || 0}</p>
            </div>
            <div className="rounded-lg bg-purple-50 p-3">
              <BookMarked className="h-6 w-6 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Loans</CardTitle>
        </CardHeader>
        <CardContent>
          {loansLoading ? (
            <div className="py-8 text-center text-gray-500">Loading loans...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Patron ID</TableHead>
                  <TableHead>Copy ID</TableHead>
                  <TableHead>Checkout Date</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {activeLoans.map((loan) => {
                  const isOverdue = new Date(loan.due_date) < new Date();
                  return (
                    <TableRow key={loan.id}>
                      <TableCell className="font-medium">{loan.patron_id}</TableCell>
                      <TableCell>{loan.copy_id}</TableCell>
                      <TableCell>{formatDate(loan.checkout_date)}</TableCell>
                      <TableCell>
                        <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
                          {formatDate(loan.due_date)}
                        </span>
                      </TableCell>
                      <TableCell>
                        {isOverdue ? (
                          <span className="inline-flex items-center rounded-full bg-red-50 px-2 py-1 text-xs font-medium text-red-700">
                            Overdue
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700">
                            Active
                          </span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm">
                          Check In
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
          {!loansLoading && !activeLoans.length && (
            <div className="py-8 text-center text-gray-500">No active loans found.</div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Active Holds</CardTitle>
        </CardHeader>
        <CardContent>
          {holdsLoading ? (
            <div className="py-8 text-center text-gray-500">Loading holds...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Patron ID</TableHead>
                  <TableHead>Item ID</TableHead>
                  <TableHead>Hold Date</TableHead>
                  <TableHead>Expiry Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {holds?.results.map((hold) => (
                  <TableRow key={hold.id}>
                    <TableCell className="font-medium">{hold.patron_id}</TableCell>
                    <TableCell>{hold.item_id}</TableCell>
                    <TableCell>{formatDate(hold.hold_date)}</TableCell>
                    <TableCell>{hold.expiry_date ? formatDate(hold.expiry_date) : 'N/A'}</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center rounded-full bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-700">
                        {hold.status}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        Fulfill
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!holdsLoading && !holds?.results.length && (
            <div className="py-8 text-center text-gray-500">No active holds found.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
