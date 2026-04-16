import React from 'react';
import { Search, ShoppingCart, Menu, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';

export const Header = () => {
  const { state } = useCart();
  const cartCount = state.items.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <header className="bg-[#131921] text-white sticky top-0 z-50">
      {/* Top Header */}
      <div className="flex items-center p-2 gap-4">
        {/* Logo */}
        <Link to="/" className="flex items-center hover:border hover:border-white p-1 rounded-sm">
          <span className="text-2xl font-bold tracking-tighter">amazon</span>
          <span className="text-xs self-start mt-1">.com</span>
        </Link>

        {/* Deliver To */}
        <div className="hidden md:flex items-center hover:border hover:border-white p-2 rounded-sm cursor-pointer">
          <MapPin className="w-5 h-5 mr-1" />
          <div className="flex flex-col text-xs">
            <span className="text-gray-300">Deliver to</span>
            <span className="font-bold text-sm">New York 10001</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 flex items-center h-10 rounded-md overflow-hidden focus-within:ring-2 focus-within:ring-[#f3a847]">
          <select className="h-full bg-gray-100 text-black text-xs px-2 border-r border-gray-300 cursor-pointer hover:bg-gray-200">
            <option>All</option>
            <option>Electronics</option>
            <option>Books</option>
            <option>Home</option>
          </select>
          <input 
            type="text" 
            className="flex-1 h-full px-3 text-black outline-none"
            placeholder="Search Amazon"
          />
          <button className="h-full bg-[#febd69] hover:bg-[#f3a847] px-4 flex items-center justify-center">
            <Search className="w-5 h-5 text-black" />
          </button>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-4">
          <div className="hidden md:flex flex-col hover:border hover:border-white p-2 rounded-sm cursor-pointer">
            <span className="text-xs">Hello, sign in</span>
            <span className="font-bold text-sm">Account & Lists</span>
          </div>

          <div className="hidden md:flex flex-col hover:border hover:border-white p-2 rounded-sm cursor-pointer">
            <span className="text-xs">Returns</span>
            <span className="font-bold text-sm">& Orders</span>
          </div>

          <Link to="/cart" className="flex items-end hover:border hover:border-white p-2 rounded-sm relative">
            <div className="relative">
              <ShoppingCart className="w-8 h-8" />
              <span className="absolute -top-1 -right-1 bg-[#f08804] text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {cartCount}
              </span>
            </div>
            <span className="font-bold text-sm mb-1 ml-1 hidden md:inline">Cart</span>
          </Link>
        </div>
      </div>

      {/* Bottom Header / Nav */}
      <div className="bg-[#232f3e] flex items-center p-2 text-sm gap-4 overflow-x-auto">
        <div className="flex items-center gap-1 hover:border hover:border-white p-1 rounded-sm cursor-pointer font-bold">
          <Menu className="w-5 h-5" />
          <span>All</span>
        </div>
        {['Today\'s Deals', 'Customer Service', 'Registry', 'Gift Cards', 'Sell'].map((item) => (
          <span key={item} className="whitespace-nowrap hover:border hover:border-white p-1 rounded-sm cursor-pointer">
            {item}
          </span>
        ))}
      </div>
    </header>
  );
};
