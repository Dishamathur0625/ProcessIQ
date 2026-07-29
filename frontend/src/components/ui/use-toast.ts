import { useState } from "react";

export interface ToastProps {
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([]);
  
  const toast = (props: ToastProps) => {
    setToasts((prev) => [...prev, props]);
    // In a real app this would trigger the UI component.
    // For this prototype, we fallback to console or native alert if needed, 
    // or we assume it's wired into the ToastProvider.
    console.log("Toast triggered:", props.title, props.description);
  };
  
  return { toast, toasts };
}
