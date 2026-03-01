import React, { useEffect, useState } from 'react';
import { useCart } from '../context/CartContext';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Minus, Plus, ChevronRight, ShoppingBag, Tag, ChevronLeft } from 'lucide-react';
import { getFoodImage } from '../utils/ImageHelper';

const OrderPage = () => {
  const { cart, totalAmount, addToCart, removeFromCart, activeRestaurantId, clearCart } = useCart();
  const navigate = useNavigate();
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);

  // Constants for billing
  const deliveryFee = 40;
  const platformFee = 5;
  const totalPayable = totalAmount + deliveryFee + platformFee;

  useEffect(() => {
    if (cart.length > 0) {
      setLoading(true);
      const lastItem = cart[cart.length - 1];

      // Fetching 64D Embedding recommendations from FastAPI
      fetch(`http://localhost:8000/recommend/${lastItem.item_id}`)
        .then(res => res.json())
        .then(data => {
          setRecs(data);
          setLoading(false);
        })
        .catch(err => {
          console.error("AI Engine Error:", err);
          setLoading(false);
        });
    }
  }, [cart.length]);

  if (cart.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-screen p-10 text-center bg-white">
        <ShoppingBag size={64} className="text-gray-100 mb-4" />
        <h2 className="text-xl font-black text-gray-300 uppercase tracking-widest">Cart Empty</h2>
        <p className="text-xs text-gray-400 mt-2 font-medium">Add some items to see AI recommendations!</p>
      </div>
    );
  }

  const handlePlaceOrder = () => {
    // Navigate to checkout
    window.location.href = '/checkout';
  };

  return (
    <div className="pt-16 p-4 pb-44 bg-gray-50 min-h-screen font-sans">
      <div className="flex items-center space-x-3 mb-6">
        <button onClick={() => navigate(-1)} className="p-1.5 bg-white border border-gray-100 rounded-full hover:bg-gray-50 active:scale-95 transition-all shadow-sm">
          <ChevronLeft size={22} className="text-gray-800" />
        </button>
        <div className="flex items-center space-x-2">
          <h2 className="text-xl font-black tracking-tight text-gray-800 uppercase">Review Order</h2>
          <span className="bg-red-100 text-red-600 text-[10px] font-black px-2 py-0.5 rounded-md uppercase">Checkout</span>
        </div>
      </div>

      {/* 1. Active Cart Items with Quantity Controls */}
      <div className="bg-white rounded-[2.5rem] p-6 shadow-sm border border-gray-100 mb-8">
        {cart.map(item => (
          <div key={item.item_id} className="flex justify-between items-center py-5 border-b border-gray-50 last:border-0">
            <div className="flex flex-col text-left">
              <span className="text-sm font-black text-gray-800 leading-tight">{item.name}</span>
              <span className="text-[10px] text-gray-400 font-bold mt-1 uppercase tracking-tight">₹{item.price} per unit</span>
            </div>

            <div className="flex items-center space-x-4">
              {/* Quantity Toggle */}
              <div className="flex items-center bg-white border border-gray-200 rounded-xl px-2 py-1 shadow-sm">
                <button onClick={() => removeFromCart(item.item_id)} className="text-red-500 p-1 active:scale-125 transition-transform"><Minus size={14} strokeWidth={3} /></button>
                <span className="text-xs font-black px-2 text-gray-700 w-4 text-center">{item.qty}</span>
                <button onClick={() => addToCart(item, activeRestaurantId)} className="text-red-500 p-1 active:scale-125 transition-transform"><Plus size={14} strokeWidth={3} /></button>
              </div>
              <span className="text-sm font-black text-gray-700 w-16 text-right font-mono">₹{item.price * item.qty}</span>
            </div>
          </div>
        ))}

        {/* 2. Coupon Section */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <button className="w-full flex items-center justify-between bg-white border border-gray-200 rounded-2xl p-4 shadow-sm active:scale-[0.98] transition-all">
            <div className="flex items-center space-x-3">
              <div className="bg-red-50 p-2 rounded-xl">
                <Tag size={20} className="text-red-500" />
              </div>
              <div className="flex flex-col text-left">
                <span className="text-sm font-black text-gray-800">Apply Coupon</span>
                <span className="text-[10px] font-bold text-gray-400 mt-0.5">Save ₹50 or more</span>
              </div>
            </div>
            <ChevronRight size={20} className="text-gray-300" />
          </button>
        </div>

        {/* 3. Bill Summary */}
        <div className="mt-6 pt-6 border-t-2 border-dashed border-gray-100 space-y-2">
          <div className="flex justify-between text-[10px] font-bold text-gray-400 uppercase tracking-widest">
            <span>Item Total</span>
            <span>₹{totalAmount}</span>
          </div>
          <div className="flex justify-between text-[10px] font-bold text-gray-400 uppercase tracking-widest">
            <span>Delivery Fee</span>
            <span>₹{deliveryFee}</span>
          </div>
          <div className="flex justify-between text-[10px] font-bold text-gray-400 uppercase tracking-widest">
            <span>Platform Fee</span>
            <span>₹{platformFee}</span>
          </div>
        </div>
      </div>

      {/* 3. AI Recommendation Rail (Similarity Model) */}
      <div className="mt-10">
        <div className="flex justify-between items-end mb-4 px-1">
          <div className="text-left">
            <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Complete Your Meal</h4>
            <p className="text-[9px] text-red-500 font-bold italic">Smart Suggestions based on {cart[cart.length - 1]?.name}</p>
          </div>
          {loading && <div className="w-3 h-3 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></div>}
        </div>

        <div className="flex overflow-x-auto space-x-4 no-scrollbar pb-4">
          <AnimatePresence>
            {recs.map((item, index) => (
              <motion.div
                key={item.item_id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex-shrink-0 w-40 bg-white border border-gray-100 p-4 rounded-[2rem] shadow-sm text-left"
              >
                <div className="h-28 bg-gray-50 rounded-2xl mb-3 overflow-hidden">
                  <img
                    src={getFoodImage(item.name)}
                    className="w-full h-full object-cover"
                    alt={item.name}
                    loading="lazy"
                    onError={(e) => { e.target.src = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=150&q=80"; }}
                  />
                </div>
                <p className="text-[11px] font-black text-gray-800 truncate">{item.name}</p>
                <p className="text-[10px] text-red-500 font-black mt-1">₹{item.price}</p>
                <button
                  onClick={() => addToCart(item, activeRestaurantId)}
                  className="mt-3 w-full bg-white border-2 border-red-50 text-red-500 py-2 rounded-xl text-[10px] font-black uppercase hover:bg-red-50 active:scale-95 transition-all shadow-sm"
                >
                  Add +
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* 4. Sticky Checkout Bar */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-white/90 backdrop-blur-xl border-t border-gray-50 z-50">
        <button
          onClick={handlePlaceOrder}
          className="w-full bg-[#E23744] text-white py-4 rounded-[1.5rem] font-black flex justify-between px-8 shadow-2xl shadow-red-200 active:scale-[0.98] transition-transform"
        >
          <div className="flex flex-col items-start">
            <span className="text-[10px] uppercase opacity-70 font-black tracking-widest leading-none">Total Payable</span>
            <span className="text-xl font-black tracking-tighter mt-1">₹{totalPayable}</span>
          </div>
          <div className="flex items-center text-sm uppercase tracking-tighter">
            Place Order <ChevronRight size={20} className="ml-1" />
          </div>
        </button>
      </div>
    </div>
  );
};

export default OrderPage;