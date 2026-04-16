import React from 'react';

export const Footer = () => {
  return (
    <footer className="bg-[#131921] text-white mt-8">
      <div className="bg-[#37475a] py-4 text-center text-sm hover:bg-[#485769] cursor-pointer">
        Back to top
      </div>
      
      <div className="max-w-7xl mx-auto py-12 px-4 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm">
        <div>
          <h3 className="font-bold mb-4 text-base">Get to Know Us</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="hover:underline cursor-pointer">Careers</li>
            <li className="hover:underline cursor-pointer">Blog</li>
            <li className="hover:underline cursor-pointer">About Amazon</li>
            <li className="hover:underline cursor-pointer">Investor Relations</li>
            <li className="hover:underline cursor-pointer">Amazon Devices</li>
            <li className="hover:underline cursor-pointer">Amazon Science</li>
          </ul>
        </div>

        <div>
          <h3 className="font-bold mb-4 text-base">Make Money with Us</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="hover:underline cursor-pointer">Sell products on Amazon</li>
            <li className="hover:underline cursor-pointer">Sell on Amazon Business</li>
            <li className="hover:underline cursor-pointer">Sell apps on Amazon</li>
            <li className="hover:underline cursor-pointer">Become an Affiliate</li>
            <li className="hover:underline cursor-pointer">Advertise Your Products</li>
            <li className="hover:underline cursor-pointer">Self-Publish with Us</li>
          </ul>
        </div>

        <div>
          <h3 className="font-bold mb-4 text-base">Amazon Payment Products</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="hover:underline cursor-pointer">Amazon Business Card</li>
            <li className="hover:underline cursor-pointer">Shop with Points</li>
            <li className="hover:underline cursor-pointer">Reload Your Balance</li>
            <li className="hover:underline cursor-pointer">Amazon Currency Converter</li>
          </ul>
        </div>

        <div>
          <h3 className="font-bold mb-4 text-base">Let Us Help You</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="hover:underline cursor-pointer">Amazon and COVID-19</li>
            <li className="hover:underline cursor-pointer">Your Account</li>
            <li className="hover:underline cursor-pointer">Your Orders</li>
            <li className="hover:underline cursor-pointer">Shipping Rates & Policies</li>
            <li className="hover:underline cursor-pointer">Returns & Replacements</li>
            <li className="hover:underline cursor-pointer">Manage Your Content and Devices</li>
            <li className="hover:underline cursor-pointer">Help</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-gray-700 py-8 text-center text-xs text-gray-300">
        <p>© 1996-2024, Amazon.com, Inc. or its affiliates</p>
      </div>
    </footer>
  );
};
