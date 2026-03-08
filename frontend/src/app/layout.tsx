import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { HelpDrawer } from "@/components/help/HelpDrawer";
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
          {/* Skip-to-content link: verborgen tot focus, voor toetsenbordgebruikers (WCAG 2.4.1) */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-700 focus:shadow-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            Ga naar hoofdinhoud
          </a>
          <Header />
          <main id="main-content" className="flex-1" tabIndex={-1}>
            {children}
          </main>
          <Footer />
          {/* Help-drawer: globaal beschikbaar op elke pagina */}
          <HelpDrawer />
        </Providers>
      </body>
    </html>
  );
}
