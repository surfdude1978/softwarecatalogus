import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "Softwarecatalogus",
    template: "%s | Softwarecatalogus",
  },
  description:
    "De Softwarecatalogus van VNG Realisatie — het centrale platform voor gemeentelijke software-registratie en -vergelijking.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="nl" className={inter.variable} suppressHydrationWarning>
      <body suppressHydrationWarning className="flex min-h-screen flex-col bg-gray-50 font-sans text-gray-900 antialiased">
        <Providers>
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
