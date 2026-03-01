import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useCart } from '../context/CartContext';

const AddOnDrawer = ({ isOpen, onClose, item }) => {
  const { addToCart } = useCart();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  // --- FETCH ML RECOMMENDATIONS ---
  useEffect(() => {
    if (isOpen && item?.item_id) {
      setLoading(true);
      fetch(`http://localhost:8000/recommend/${item.item_id}`)
        .then((res) => res.json())
        .then((data) => {
          setRecommendations(data || []);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Failed to fetch ML recommendations:", err);
          setLoading(false);
        });
    } else {
      setRecommendations([]);
    }
  }, [isOpen, item]);

  // --- HANDLE ADDING RECOMMENDED ITEM ---
  const handleAddRecommendation = (recItem) => {
    // We pass true for `isRecommendation` and the original item.item_id as the `anchorItemId`
    addToCart(recItem, item.restaurant_id, true, item.item_id);
    alert(`Added ${recItem.name} to cart!`); // Optional UX feedback
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-[60]"
          />
          
          <motion.div 
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl z-[70] max-w-md mx-auto p-5 pb-safe"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-bold">Complete your meal</h3>
                <p className="text-xs text-gray-500 italic">People who ordered {item?.name} also added:</p>
              </div>
              <button onClick={onClose} className="bg-gray-100 rounded-full w-8 h-8 flex items-center justify-center text-gray-600">✕</button>
            </div>

            <div className="space-y-4 max-h-[60vh] overflow-y-auto no-scrollbar pb-6">
              {loading ? (
                <p className="text-sm text-center py-4 text-gray-500">AI is finding perfect pairings...</p>
              ) : recommendations.length > 0 ? (
                recommendations.map((rec) => (
                  <div key={rec.item_id} className="flex justify-between items-center py-2 border-b border-gray-100">
                    <div className="flex items-center space-x-3">
                      <div className={`w-4 h-4 border flex items-center justify-center p-[2px] ${rec.is_veg === 1 ? 'border-green-600' : 'border-red-600'}`}>
                        <div className={`w-full h-full rounded-full ${rec.is_veg === 1 ? 'bg-green-600' : 'bg-red-600'}`} />
                      </div>
                      <div>
                        <span className="text-sm font-semibold text-gray-800 block">{rec.name}</span>
                        <span className="text-xs text-gray-500">{rec.category}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-bold text-gray-700">₹{rec.price}</span>
                      <button 
                        onClick={() => handleAddRecommendation(rec)}
                        className="bg-red-50 text-red-500 border border-red-200 px-3 py-1 rounded-lg text-xs font-bold hover:bg-red-100"
                      >
                        ADD
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-center py-4 text-gray-500">No special recommendations found.</p>
              )}
            </div>
            
            <button onClick={onClose} className="w-full bg-zomato mt-2 py-3 rounded-xl text-white font-bold shadow-lg">
              Done
            </button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default AddOnDrawer;