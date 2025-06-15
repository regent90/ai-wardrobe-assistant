import { useState } from 'react';

export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const toast = ({ title, description, variant = 'default' }) => {
    const id = Date.now();
    const newToast = { id, title, description, variant };
    
    setToasts(prev => [...prev, newToast]);
    
    // 自動移除 toast
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
    
    // 簡單的 alert 替代方案
    if (variant === 'destructive') {
      alert(`錯誤: ${title}\n${description}`);
    } else {
      alert(`${title}\n${description}`);
    }
  };

  return { toast };
};

