"use client";

import { create } from "zustand";
import { api, ApiError } from "@/lib/api";

interface User {
  id: string;
  email: string;
  naam: string;
  organisatie: string | null;
  organisatie_naam: string | null;
  rol: string;
  rol_display: string;
  status: string;
  totp_enabled: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<{ totp_required: boolean }>;
  verifyTotp: (code: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchProfile: () => Promise<void>;
  initialize: () => void;
  clearError: () => void;
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.post<{
        totp_required: boolean;
        temp_token?: string;
        access?: string;
        refresh?: string;
        user?: User;
      }>("/api/v1/auth/login/", { email, password });

      if (data.totp_required && data.temp_token) {
        localStorage.setItem("temp_token", data.temp_token);
        set({ isLoading: false });
        return { totp_required: true };
      }

      if (data.access && data.refresh) {
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        set({
          user: data.user || null,
          isAuthenticated: true,
          isLoading: false,
        });
      }
      return { totp_required: false };
    } catch (err) {
      const message = err instanceof ApiError
        ? JSON.parse(err.body)?.detail || "Inloggen mislukt."
        : "Er is een fout opgetreden.";
      set({ isLoading: false, error: message });
      throw err;
    }
  },

  verifyTotp: async (code: string) => {
    set({ isLoading: true, error: null });
    try {
      const tempToken = localStorage.getItem("temp_token");
      const data = await api.post<{
        access: string;
        refresh: string;
        user: User;
      }>("/api/v1/auth/token/verify-totp/", { totp_code: code }, {
        headers: { Authorization: `Bearer ${tempToken}` },
      });

      localStorage.removeItem("temp_token");
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err) {
      const message = err instanceof ApiError
        ? JSON.parse(err.body)?.detail || "Ongeldige code."
        : "Er is een fout opgetreden.";
      set({ isLoading: false, error: message });
      throw err;
    }
  },

  logout: async () => {
    const refresh = localStorage.getItem("refresh_token");
    try {
      if (refresh) {
        await api.post("/api/v1/auth/logout/", { refresh });
      }
    } catch {
      // Ignore logout errors
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("temp_token");
      set({ user: null, isAuthenticated: false });
    }
  },

  fetchProfile: async () => {
    // Controleer de token direct in localStorage, niet de Zustand-state.
    // Dit werkt ook wanneer de token extern is ingesteld (bijv. via loginApi in de demo)
    // zonder dat isAuthenticated al op true staat in de store.
    const token =
      typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) return;
    try {
      const user = await api.get<User>("/api/v1/profiel/mij/");
      set({ user, isAuthenticated: true });
    } catch {
      // Token verlopen of ongeldig
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      set({ user: null, isAuthenticated: false });
    }
  },

  initialize: () => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        set({ isAuthenticated: true });
        get().fetchProfile();
      }
    }
  },

  clearError: () => set({ error: null }),
}));
