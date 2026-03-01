import React, { createContext, useContext, useState, useEffect } from 'react';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState(() => {
    const savedCart = localStorage.getItem('zomathon_cart');
    return savedCart ? JSON.parse(savedCart) : [];
  });
  
  const [activeRestaurantId, setActiveRestaurantId] = useState(() => {
    return localStorage.getItem('zomathon_res_id') || null;
  });

  useEffect(() => {
    localStorage.setItem('zomathon_cart', JSON.stringify(cart));
    if (activeRestaurantId) {
      localStorage.setItem('zomathon_res_id', activeRestaurantId);
    } else {
      localStorage.removeItem('zomathon_res_id');
    }
  }, [cart, activeRestaurantId]);

  // UPGRADED: Added isRecommendation and anchorItemId flags
  const addToCart = (item, resId, isRecommendation = false, anchorItemId = null) => {
    const stringResId = resId ? String(resId) : null;
    
    if (activeRestaurantId && stringResId && activeRestaurantId !== stringResId) {
      const confirmClear = window.confirm(
        "You have items from another restaurant in your cart. Discard and add this instead?"
      );
      if (confirmClear) {
        setCart([{ ...item, qty: 1 }]);
        setActiveRestaurantId(stringResId);
      }
      return;
    }

    if (!activeRestaurantId && stringResId) setActiveRestaurantId(stringResId);

    setCart((prev) => {
      const existing = prev.find((i) => String(i.item_id) === String(item.item_id));
      if (existing) {
        return prev.map((i) =>
          String(i.item_id) === String(item.item_id) ? { ...i, qty: i.qty + 1 } : i
        );
      }
      return [...prev, { ...item, qty: 1 }];
    });

    // --- THE ML FEEDBACK LOOP ---
    // If this item was added via the Recommendation Drawer, log it!
    if (isRecommendation && anchorItemId) {
      fetch("http://localhost:8000/log_interaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "demo_judge_user", 
          anchor_item_id: anchorItemId,
          recommended_item_id: item.item_id,
          action: "added_to_cart"
        })
      }).catch(err => console.error("ML Logging failed:", err));
    }
  };

  const removeFromCart = (itemId) => {
    setCart((prev) => {
      const item = prev.find(i => String(i.item_id) === String(itemId));
      if (!item) return prev;

      if (item.qty > 1) {
        return prev.map(i => String(i.item_id) === String(itemId) ? { ...i, qty: i.qty - 1 } : i);
      }
      
      const newCart = prev.filter((i) => String(i.item_id) !== String(itemId));
      if (newCart.length === 0) setActiveRestaurantId(null);
      return newCart;
    });
  };

  const clearCart = () => {
    setCart([]);
    setActiveRestaurantId(null);
  };

  const totalAmount = cart.reduce((acc, item) => acc + (Number(item.price) * item.qty), 0);
  const totalQty = cart.reduce((acc, item) => acc + item.qty, 0);

  return (
    <CartContext.Provider value={{ 
      cart, 
      activeRestaurantId, 
      addToCart, 
      removeFromCart, 
      clearCart,
      totalAmount, 
      totalQty 
    }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);