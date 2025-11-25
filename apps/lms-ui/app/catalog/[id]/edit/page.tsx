'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { itemsApi } from '@/lib/api/catalogs';
import { ItemUpdateSchema, type ItemUpdate } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function EditItemPage() {
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();
  const itemId = params.id as string;

  const [formData, setFormData] = useState<ItemUpdate>({
    title: '',
    author: '',
    isbn: '',
    publication_year: undefined,
    format: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data: item, isLoading: isLoadingItem } = useQuery({
    queryKey: ['items', itemId],
    queryFn: () => itemsApi.get(itemId),
  });

  useEffect(() => {
    if (item) {
      setFormData({
        title: item.title,
        author: item.author || '',
        isbn: item.isbn || '',
        publication_year: item.publication_year,
        format: item.format || '',
      });
    }
  }, [item]);

  const updateMutation = useMutation({
    mutationFn: (data: ItemUpdate) => itemsApi.update(itemId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      queryClient.invalidateQueries({ queryKey: ['items', itemId] });
      router.push('/catalog');
    },
    onError: (error: Error) => {
      setErrors({ submit: error.message });
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = ItemUpdateSchema.safeParse(formData);
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

  if (isLoadingItem) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading item information...</div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-red-500">Item not found</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/catalog">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Edit Catalog Item</h1>
          <p className="mt-2 text-gray-600">Update item information</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Item Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              error={errors.title}
              placeholder="The Great Gatsby"
            />

            <Input
              label="Author"
              value={formData.author}
              onChange={(e) => setFormData({ ...formData, author: e.target.value })}
              error={errors.author}
              placeholder="F. Scott Fitzgerald"
            />

            <Input
              label="ISBN"
              value={formData.isbn}
              onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
              error={errors.isbn}
              placeholder="978-0-7432-7356-5"
            />

            <Input
              label="Publication Year"
              type="number"
              value={formData.publication_year?.toString() || ''}
              onChange={(e) => setFormData({ 
                ...formData, 
                publication_year: e.target.value ? parseInt(e.target.value) : undefined 
              })}
              error={errors.publication_year}
              placeholder="1925"
            />

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Format
              </label>
              <select
                value={formData.format}
                onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select a format</option>
                <option value="hardcover">Hardcover</option>
                <option value="paperback">Paperback</option>
                <option value="ebook">E-book</option>
                <option value="audiobook">Audiobook</option>
                <option value="magazine">Magazine</option>
                <option value="dvd">DVD</option>
                <option value="cd">CD</option>
              </select>
              {errors.format && (
                <p className="text-sm text-red-600">{errors.format}</p>
              )}
            </div>

            {errors.submit && (
              <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600">
                {errors.submit}
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Updating...' : 'Update Item'}
              </Button>
              <Link href="/catalog">
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
