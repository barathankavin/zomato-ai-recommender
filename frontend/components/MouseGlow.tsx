"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function MouseGlow() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: e.clientX,
        y: e.clientY,
      });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  if (!isClient) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <motion.div
        className="absolute w-[600px] h-[600px] rounded-full blur-[100px] opacity-20"
        style={{
          background: "radial-gradient(circle, rgba(226, 55, 68, 0.4) 0%, rgba(0,0,0,0) 70%)",
        }}
        animate={{
          x: mousePosition.x - 300,
          y: mousePosition.y - 300,
        }}
        transition={{
          type: "tween",
          ease: "backOut",
          duration: 0.5,
        }}
      />
    </div>
  );
}
