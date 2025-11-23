'use client';

import { useQuery } from '@tanstack/react-query';
import { patronsApi } from '@/lib/api/patrons';
import { branchesApi } from '@/lib/api/organizations';
import { loansApi } from '@/lib/api/circulations';
import { itemsApi } from '@/lib/api/catalogs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, BookOpen, ArrowLeftRight, Building2 } from 'lucide-react';

export default function Home() {
  const { data: patrons } = useQuery({
    queryKey: ['patrons'],
    queryFn: patronsApi.list,
  });

  const { data: branches } = useQuery({
    queryKey: ['branches'],
    queryFn: branchesApi.list,
  });

  const { data: loans } = useQuery({
    queryKey: ['loans'],
    queryFn: loansApi.list,
  });

  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: itemsApi.list,
  });

  const stats = [
    {
      name: 'Total Patrons',
      value: patrons?.count || 0,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Catalog Items',
      value: items?.count || 0,
      icon: BookOpen,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Active Loans',
      value: loans?.results.filter((l) => !l.return_date).length || 0,
      icon: ArrowLeftRight,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      name: 'Branches',
      value: branches?.count || 0,
      icon: Building2,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">Overview of your library management system</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`rounded-lg p-3 ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Loans</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loans?.results.slice(0, 5).map((loan) => (
                <div key={loan.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                  <div>
                    <p className="font-medium text-gray-900">Copy ID: {loan.copy_id}</p>
                    <p className="text-sm text-gray-600">Patron: {loan.patron_id}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Due: {new Date(loan.due_date).toLocaleDateString()}</p>
                    {loan.return_date ? (
                      <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700">
                        Returned
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-700">
                        Active
                      </span>
                    )}
                  </div>
                </div>
              ))}
              {!loans?.results.length && (
                <p className="text-center text-sm text-gray-500">No loans found</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <a
                href="/circulation/checkout"
                className="block rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50"
              >
                <h4 className="font-medium text-gray-900">Check Out Item</h4>
                <p className="text-sm text-gray-600">Loan an item to a patron</p>
              </a>
              <a
                href="/patrons/new"
                className="block rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50"
              >
                <h4 className="font-medium text-gray-900">Add Patron</h4>
                <p className="text-sm text-gray-600">Register a new library member</p>
              </a>
              <a
                href="/catalog/new"
                className="block rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50"
              >
                <h4 className="font-medium text-gray-900">Add Item</h4>
                <p className="text-sm text-gray-600">Add a new item to the catalog</p>
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

