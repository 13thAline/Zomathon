import React from 'react';
import { NavLink } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { ShoppingBag, Utensils, Search, Zap } from 'lucide-react';

const BottomNav = () => {
  const { cart } = useCart();
  const itemCount = cart.reduce((acc, item) => acc + item.qty, 0);

  const navItems = [
    { path: '/', label: 'Delivery', icon: <ShoppingBag size={20} /> },
    { path: '/dining', label: 'Dining', icon: <Utensils size={20} /> },
    { path: '/search', label: 'Search', icon: <Search size={20} /> },
    { path: '/order', label: 'Cart', icon: <ShoppingBag size={20} />, isCart: true },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around items-center py-2 pb-safe shadow-[0_-4px_12px_rgba(0,0,0,0.05)] z-40 max-w-md mx-auto">
      {navItems.map((item) => (
        <NavLink
          key={item.label}
          to={item.path}
          className={({ isActive }) =>
            `flex flex-col items-center relative transition-colors duration-200 ${isActive ? 'text-red-500 font-bold' : 'text-gray-400'
            }`
          }
        >
          {item.icon}

          {/* Cart Badge Logic */}
          {item.isCart && itemCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-600 text-white text-[8px] w-4 h-4 rounded-full flex items-center justify-center border-2 border-white animate-pulse">
              {itemCount}
            </span>
          )}

          <span className="text-[10px] mt-1">{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
};

export default BottomNav;