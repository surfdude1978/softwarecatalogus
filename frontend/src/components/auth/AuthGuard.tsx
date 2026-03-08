"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Spinner } from "@/components/ui/Spinner";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user, fetchProfile } = useAuth();
  const router = useRouter();
  const [hasMounted, setHasMounted] = useState(false);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  useEffect(() => {
    if (!hasMounted) return;

    // Initialize auth state from localStorage
    const token = localStorage.getItem("access_token");
    
    if (!token) {
      router.push("/login");
      return;
    }

    if (!user) {
      fetchProfile().then(() => setIsReady(true)).catch(() => {
        router.push("/login");
      });
    } else {
      setIsReady(true);
    }
  }, [hasMounted, user, fetchProfile, router]);

  if (!hasMounted || !isReady) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return <>{children}</>;
}
