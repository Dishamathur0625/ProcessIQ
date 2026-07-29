import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Navbar } from "@/components/layout/Navbar";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ProcessIQ - Intelligent Data Preprocessing",
  description: "Enterprise Industrial Analytics Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-zinc-50 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-50`}>
        <Providers>
          <Navbar />
          <main className="container mx-auto p-4 py-8">
            {children}
          </main>
          {/* Note: In shadcn v4, toast might require a Toaster component imported from sonner or toast */}
        </Providers>
      </body>
    </html>
  );
}
