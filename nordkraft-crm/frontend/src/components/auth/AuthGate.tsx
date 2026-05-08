"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { authApi } from "@/lib/api";

const PUBLIC_PATHS = new Set<string>(["/login"]);

export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const isPublic = PUBLIC_PATHS.has(pathname);
    const token = localStorage.getItem("nk_token");

    if (!token) {
      if (!isPublic) router.replace("/login");
      setReady(true);
      return;
    }

    authApi
      .me()
      .then(() => setReady(true))
      .catch(() => {
        localStorage.removeItem("nk_token");
        if (!isPublic) router.replace("/login");
        setReady(true);
      });
  }, [pathname, router]);

  if (!ready) return null;
  return <>{children}</>;
}

