import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { products } from '../data/products';
import { useCart } from '../context/CartContext';
import { Star, MapPin } from 'lucide-react';

export const ProductDetails = () => {
  const { id } = useParams();
  const product = products.find((p) => p.id === id);
  const { dispatch } = useCart();

  if (!product) {
    return <div className="text-center py-20">Product not found</div>;
  }

  const addToCart = () => {
    dispatch({ type: 'ADD_TO_CART', payload: product });
  };

  return (
    <div className="bg-white min-h-screen py-8">
      <div className="max-w-[1500px] mx-auto px-4 grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Image Section */}
        <div className="md:col-span-5 flex justify-center">
          <img 
            src={product.image} 
            alt={product.title} 
            className="max-h-[500px] object-contain"
          />
        </div>

        {/* Details Section */}
        <div className="md:col-span-4 space-y-4">
          <h1 className="text-2xl font-medium text-gray-900 leading-snug">
            {product.title}
          </h1>
          
          <div className="flex items-center gap-2 text-sm">
            <div className="flex text-[#ffa41c]">
              {[...Array(5)].map((_, i) => (
                <Star 
                  key={i} 
                  className={`w-4 h-4 ${i < Math.floor(product.rating) ? 'fill-current' : 'text-gray-300'}`} 
                />
              ))}
            </div>
            <span className="text-[#007185] hover:underline cursor-pointer">
              {product.reviews.toLocaleString()} ratings
            </span>
          </div>

          <div className="border-t border-b border-gray-200 py-4">
            <div className="flex items-baseline gap-1">
              <span className="text-sm relative -top-1.5">$</span>
              <span className="text-3xl font-medium text-gray-900">{Math.floor(product.price)}</span>
              <span className="text-sm relative -top-1.5">{(product.price % 1).toFixed(2).substring(2)}</span>
            </div>
            {product.isPrime && (
              <div className="flex items-center gap-1 mt-2">
                <span className="text-[#00a8e1] font-bold text-sm italic">prime</span>
                <span className="text-sm text-gray-500">One-Day</span>
              </div>
            )}
            <div className="text-sm text-gray-600 mt-2">
              <span className="font-bold">FREE Returns</span>
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Join Prime to save $15.00 on this item.
            </div>
          </div>

          <div className="space-y-2 text-sm">
            <div className="grid grid-cols-2 gap-2">
              <span className="font-bold text-gray-700">Brand</span>
              <span>Generic</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <span className="font-bold text-gray-700">Color</span>
              <span>Black</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <span className="font-bold text-gray-700">Connectivity</span>
              <span>Wireless</span>
            </div>
          </div>

          <div className="mt-4">
            <h3 className="font-bold text-lg mb-2">About this item</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
              <li>High-quality materials ensure durability and longevity.</li>
              <li>Designed for maximum comfort and ease of use.</li>
              <li>Perfect for everyday use or as a gift.</li>
              <li>Includes a 1-year manufacturer warranty.</li>
            </ul>
          </div>
        </div>

        {/* Buy Box */}
        <div className="md:col-span-3">
          <div className="border border-gray-300 rounded-lg p-4 space-y-4">
            <div className="flex items-baseline gap-1">
              <span className="text-sm relative -top-1.5">$</span>
              <span className="text-2xl font-medium text-gray-900">{Math.floor(product.price)}</span>
              <span className="text-sm relative -top-1.5">{(product.price % 1).toFixed(2).substring(2)}</span>
            </div>

            <div className="text-sm text-gray-600">
              FREE delivery <span className="font-bold text-gray-900">Tomorrow, Mar 4</span>. Order within <span className="text-green-600">5 hrs 32 mins</span>
            </div>

            <div className="flex items-center gap-2 text-sm text-[#007185] hover:underline cursor-pointer">
              <MapPin className="w-4 h-4" />
              <span>Deliver to New York 10001</span>
            </div>

            <div className="text-lg text-green-700 font-medium">In Stock</div>

            <div className="space-y-3">
              <button 
                onClick={addToCart}
                className="w-full bg-[#ffd814] hover:bg-[#f7ca00] border border-[#fcd200] rounded-full py-2 text-sm shadow-sm cursor-pointer"
              >
                Add to Cart
              </button>
              <button className="w-full bg-[#ffa41c] hover:bg-[#fa8900] border border-[#ff8f00] rounded-full py-2 text-sm shadow-sm cursor-pointer">
                Buy Now
              </button>
            </div>

            <div className="text-xs text-gray-600 space-y-1 pt-2">
              <div className="grid grid-cols-[auto_1fr] gap-2">
                <span className="text-gray-500">Ships from</span>
                <span>Amazon.com</span>
              </div>
              <div className="grid grid-cols-[auto_1fr] gap-2">
                <span className="text-gray-500">Sold by</span>
                <span>Amazon.com</span>
              </div>
              <div className="grid grid-cols-[auto_1fr] gap-2">
                <span className="text-gray-500">Returns</span>
                <span className="text-[#007185] hover:underline cursor-pointer">Eligible for Return, Refund or Replacement within 30 days of receipt</span>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-4 mt-4">
              <div className="flex items-center gap-2 mb-2">
                <input type="checkbox" className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" />
                <span className="text-sm">Add a gift receipt for easy returns</span>
              </div>
              <button className="w-full border border-gray-300 bg-white hover:bg-gray-50 rounded-sm py-1 text-sm shadow-sm">
                Add to List
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
