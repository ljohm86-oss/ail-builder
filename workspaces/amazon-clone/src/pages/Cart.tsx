import React from 'react';
import { useCart } from '../context/CartContext';
import { Link, useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus } from 'lucide-react';

export const Cart = () => {
  const { state, dispatch } = useCart();
  const navigate = useNavigate();

  const updateQuantity = (id: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { id, quantity } });
  };

  const removeItem = (id: string) => {
    dispatch({ type: 'REMOVE_FROM_CART', payload: id });
  };

  return (
    <div className="bg-gray-100 min-h-screen py-8">
      <div className="max-w-[1500px] mx-auto px-4 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cart Items */}
        <div className="lg:col-span-9 bg-white p-6 rounded-sm shadow-sm">
          <div className="flex justify-between items-end border-b border-gray-200 pb-4 mb-4">
            <h1 className="text-3xl font-medium">Shopping Cart</h1>
            <span className="text-sm text-gray-600">Price</span>
          </div>

          {state.items.length === 0 ? (
            <div className="text-center py-10">
              <h2 className="text-xl mb-4">Your Amazon Cart is empty.</h2>
              <Link to="/" className="text-[#007185] hover:underline hover:text-[#c7511f]">
                Shop today's deals
              </Link>
            </div>
          ) : (
            <div className="space-y-6">
              {state.items.map((item) => (
                <div key={item.id} className="flex gap-4 border-b border-gray-200 pb-6 last:border-0">
                  <div className="w-48 h-48 flex-shrink-0 bg-gray-50 flex items-center justify-center">
                    <img src={item.image} alt={item.title} className="max-w-full max-h-full object-contain mix-blend-multiply" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex justify-between mb-2">
                      <Link to={`/product/${item.id}`} className="text-lg font-medium text-[#007185] hover:underline hover:text-[#c7511f] line-clamp-2">
                        {item.title}
                      </Link>
                      <span className="font-bold text-lg ml-4">${item.price.toFixed(2)}</span>
                    </div>
                    
                    <div className="text-sm text-green-700 mb-1">In Stock</div>
                    {item.isPrime && (
                      <div className="flex items-center gap-1 mb-2">
                        <span className="text-[#00a8e1] font-bold text-xs italic">prime</span>
                        <span className="text-xs text-gray-500">FREE delivery</span>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-4 mt-4">
                      <div className="flex items-center border border-gray-300 rounded-md shadow-sm">
                        <button 
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-l-md border-r border-gray-300"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="px-4 py-1 text-sm font-medium">{item.quantity}</span>
                        <button 
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-r-md border-l border-gray-300"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>
                      
                      <div className="h-4 border-l border-gray-300"></div>
                      
                      <button 
                        onClick={() => removeItem(item.id)}
                        className="text-sm text-[#007185] hover:underline hover:text-[#c7511f]"
                      >
                        Delete
                      </button>
                      
                      <div className="h-4 border-l border-gray-300"></div>
                      
                      <button className="text-sm text-[#007185] hover:underline hover:text-[#c7511f]">
                        Save for later
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {state.items.length > 0 && (
            <div className="flex justify-end pt-4">
              <span className="text-lg">
                Subtotal ({state.items.reduce((acc, item) => acc + item.quantity, 0)} items): 
                <span className="font-bold ml-1">${state.total.toFixed(2)}</span>
              </span>
            </div>
          )}
        </div>

        {/* Checkout Sidebar */}
        {state.items.length > 0 && (
          <div className="lg:col-span-3">
            <div className="bg-white p-6 rounded-sm shadow-sm sticky top-24">
              <div className="text-lg mb-4">
                Subtotal ({state.items.reduce((acc, item) => acc + item.quantity, 0)} items): 
                <span className="font-bold ml-1">${state.total.toFixed(2)}</span>
              </div>
              
              <div className="flex items-center gap-2 mb-4">
                <input type="checkbox" className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" />
                <span className="text-sm">This order contains a gift</span>
              </div>
              
              <button 
                onClick={() => navigate('/checkout')}
                className="w-full bg-[#ffd814] hover:bg-[#f7ca00] border border-[#fcd200] rounded-lg py-2 text-sm shadow-sm cursor-pointer mb-4"
              >
                Proceed to checkout
              </button>
            </div>
            
            <div className="bg-white p-6 rounded-sm shadow-sm mt-6">
              <h3 className="font-bold text-sm mb-2">Customers who bought items in your Recent History also bought</h3>
              {/* Recommendations could go here */}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
