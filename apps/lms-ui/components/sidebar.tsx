'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  BookOpen, 
  Users, 
  Building2, 
  UserCircle, 
  ArrowLeftRight, 
  BookMarked 
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/', icon: BookOpen },
  { name: 'Catalog', href: '/catalog', icon: BookMarked },
  { name: 'Patrons', href: '/patrons', icon: Users },
  { name: 'Circulation', href: '/circulation', icon: ArrowLeftRight },
  { name: 'Branches', href: '/branches', icon: Building2 },
  { name: 'Staff', href: '/staff', icon: UserCircle },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-gray-50">
      <div className="flex h-16 items-center border-b px-6">
        <BookOpen className="h-8 w-8 text-blue-600" />
        <h1 className="ml-3 text-xl font-bold text-gray-900">Library MS</h1>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
