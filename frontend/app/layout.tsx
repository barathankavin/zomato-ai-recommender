import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import MouseGlow from "@/components/MouseGlow";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "Zomato AI Recommendations",
  description:
    "AI-powered restaurant recommendations for Bangalore, powered by Groq LLM",
  keywords: ["zomato", "restaurant", "recommendation", "AI", "bangalore"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${outfit.variable} font-sans antialiased bg-[#0A0A0A] text-white min-h-screen`}
      >
        <MouseGlow />
        {children}
      </body>
    </html>
  );
}
