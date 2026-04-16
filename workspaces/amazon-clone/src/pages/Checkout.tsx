import React, { useState } from 'react';
import { useCart } from '../context/CartContext';
import { Link, useNavigate } from 'react-router-dom';
import { Lock } from 'lucide-react';

export const Checkout = () => {
  const { state, dispatch } = useCart();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const handlePlaceOrder = () => {
    setLoading(true);
    setTimeout(() => {
      dispatch({ type: 'CLEAR_CART' });
      alert('Order placed successfully!');
      navigate('/');
      setLoading(false);
    }, 2000);
  };

  if (state.items.length === 0) {
    return (
      <div className="text-center py-20">
        <h2 className="text-xl mb-4">Your cart is empty.</h2>
        <Link to="/" className="text-[#007185] hover:underline">Go shopping</Link>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-screen pb-20">
      {/* Checkout Header */}
      <div className="bg-gradient-to-b from-gray-50 to-gray-100 border-b border-gray-200 py-4">
        <div className="max-w-[1000px] mx-auto px-4 flex justify-between items-center">
          <Link to="/" className="flex items-center">
            <span className="text-3xl font-bold tracking-tighter">amazon</span>
            <span className="text-xs self-start mt-1">.com</span>
          </Link>
          <h1 className="text-2xl font-medium text-gray-600">Checkout (<Link to="/cart" className="text-[#007185] hover:underline">{state.items.length} items</Link>)</h1>
          <Lock className="w-5 h-5 text-gray-500" />
        </div>
      </div>

      <div className="max-w-[1000px] mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-9 space-y-6">
          {/* Step 1: Address */}
          <div className="border-b border-gray-200 pb-6">
            <div className="flex gap-4">
              <span className="font-bold w-8">1</span>
              <div className="flex-1">
                <h2 className="font-bold text-lg mb-2 text-[#c45500]">Shipping address</h2>
                <div className="text-sm space-y-1">
                  <p>John Doe</p>
                  <p>123 Main Street</p>
                  <p>New York, NY 10001</p>
                  <p>United States</p>
                  <p>Phone: 555-0123</p>
                </div>
              </div>
              <button className="text-[#007185] text-sm hover:underline hover:text-[#c7511f]">Change</button>
            </div>
          </div>

          {/* Step 2: Payment */}
          <div className="border-b border-gray-200 pb-6">
            <div className="flex gap-4">
              <span className="font-bold w-8">2</span>
              <div className="flex-1">
                <h2 className="font-bold text-lg mb-2 text-[#c45500]">Payment method</h2>
                <div className="text-sm space-y-1">
                  <p className="font-bold">Visa ending in 1234</p>
                  <p className="text-[#007185] hover:underline cursor-pointer">Billing address: Same as shipping address</p>
                </div>
              </div>
              <button className="text-[#007185] text-sm hover:underline hover:text-[#c7511f]">Change</button>
            </div>
          </div>

          {/* Step 3: Review */}
          <div className="border border-gray-300 rounded-md p-4">
            <div className="flex gap-4">
              <span className="font-bold w-8 text-[#c45500]">3</span>
              <div className="flex-1">
                <h2 className="font-bold text-lg mb-4 text-[#c45500]">Review items and shipping</h2>
                
                <div className="space-y-6">
                  {state.items.map((item) => (
                    <div key={item.id} className="flex gap-4 border border-gray-200 rounded-md p-4">
                      <img src={item.image} alt={item.title} className="w-20 h-20 object-contain mix-blend-multiply" />
                      <div className="flex-1">
                        <h4 className="font-bold text-sm line-clamp-2">{item.title}</h4>
                        <div className="text-sm font-bold text-[#b12704] mt-1">${item.price.toFixed(2)}</div>
                        <div className="text-sm text-gray-500 mt-1">Qty: {item.quantity}</div>
                        <div className="text-sm font-bold text-gray-700 mt-1">
                          Delivery: <span className="text-green-700">Tomorrow, Mar 4</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="mt-6 ml-12 border border-gray-200 rounded-md bg-gray-50 p-4 flex justify-between items-center">
              <button 
                onClick={handlePlaceOrder}
                disabled={loading}
                className={`bg-[#ffd814] hover:bg-[#f7ca00] border border-[#fcd200] rounded-lg px-8 py-2 text-sm shadow-sm cursor-pointer ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {loading ? 'Placing Order...' : 'Place your order'}
              </button>
              
              <div className="text-right">
                <div className="text-lg font-bold text-[#b12704]">Order Total: ${state.total.toFixed(2)}</div>
                <div className="text-xs text-gray-500">
                  By placing your order, you agree to Amazon's <span className="text-[#007185] hover:underline cursor-pointer">privacy notice</span> and <span className="text-[#007185] hover:underline cursor-pointer">conditions of use</span>.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Order Summary Sidebar */}
        <div className="lg:col-span-3">
          <div className="bg-white border border-gray-200 rounded-md p-4 sticky top-4">
            <button 
              onClick={handlePlaceOrder}
              disabled={loading}
              className={`w-full bg-[#ffd814] hover:bg-[#f7ca00] border border-[#fcd200] rounded-lg py-2 text-sm shadow-sm cursor-pointer mb-4 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {loading ? 'Placing Order...' : 'Place your order'}
            </button>
            
            <div className="text-xs text-center text-gray-500 mb-4 border-b border-gray-200 pb-4">
              By placing your order, you agree to Amazon's <span className="text-[#007185] hover:underline cursor-pointer">privacy notice</span> and <span className="text-[#007185] hover:underline cursor-pointer">conditions of use</span>.
            </div>

            <h3 className="font-bold text-lg mb-2">Order Summary</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span>Items:</span>
                <span>${state.total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Shipping & handling:</span>
                <span>$0.00</span>
              </div>
              <div className="flex justify-between">
                <span>Total before tax:</span>
                <span>${state.total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Estimated tax to be collected:</span>
                <span>$0.00</span>
              </div>
              <div className="flex justify-between font-bold text-[#b12704] text-lg border-t border-gray-200 pt-2 mt-2">
                <span>Order Total:</span>
                <span>${state.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
