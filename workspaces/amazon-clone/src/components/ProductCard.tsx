import React from 'react';
import { Link } from 'react-router-dom';
import { Star } from 'lucide-react';
import { Product } from '../data/products';

export const ProductCard = ({ product }: { product: Product }) => {
  return (
    <div className="bg-white p-4 border border-gray-200 rounded-sm hover:shadow-lg transition-shadow flex flex-col h-full">
      <div className="relative pb-[100%] mb-4 bg-gray-50">
        <img 
          src={product.image} 
          alt={product.title} 
          className="absolute inset-0 w-full h-full object-contain p-4 mix-blend-multiply"
        />
      </div>
      
      <div className="flex-1 flex flex-col">
        <Link to={`/product/${product.id}`} className="hover:text-[#c7511f] hover:underline mb-1 line-clamp-3 text-sm font-medium">
          {product.title}
        </Link>
        
        <div className="flex items-center mb-1">
          <div className="flex text-[#ffa41c]">
            {[...Array(5)].map((_, i) => (
              <Star 
                key={i} 
                className={`w-4 h-4 ${i < Math.floor(product.rating) ? 'fill-current' : 'text-gray-300'}`} 
              />
            ))}
          </div>
          <span className="text-xs text-[#007185] ml-1 hover:underline cursor-pointer">
            {product.reviews.toLocaleString()}
          </span>
        </div>

        <div className="mt-auto">
          <div className="flex items-baseline mb-1">
            <span className="text-xs align-top relative top-0.5">$</span>
            <span className="text-2xl font-medium">{Math.floor(product.price)}</span>
            <span className="text-xs align-top relative top-0.5">{(product.price % 1).toFixed(2).substring(2)}</span>
          </div>
          
          {product.isPrime && (
            <div className="flex items-center gap-1 mb-2">
              <span className="text-[#00a8e1] font-bold text-xs italic">prime</span>
              <span className="text-xs text-gray-500">FREE delivery</span>
            </div>
          )}
          
          <span className="text-xs text-gray-500">
            Delivery <span className="font-bold text-gray-700">Tomorrow, Mar 4</span>
          </span>
        </div>
      </div>
    </div>
  );
};
