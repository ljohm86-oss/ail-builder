import React from 'react';
import { ProductCard } from '../components/ProductCard';
import { products } from '../data/products';

export const Home = () => {
  return (
    <div className="bg-gray-100 min-h-screen">
      <div className="max-w-[1500px] mx-auto px-4 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>
    </div>
  );
};
