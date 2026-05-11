import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api, tokenStore } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => tokenStore.getUser());
  const [loading, setLoading] = useState(false);

  const login = useCallback(async ({ email, password }) => {
    setLoading(true);
    try {
      const data = await api.login({ email, password });
      // login returns TokenResponse (no user); fetch user via account or stored.
      tokenStore.set({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
      });
      // Decode minimal user from token? Backend doesn't return user here; we keep email.
      const minimalUser = { email };
      tokenStore.set({ user: minimalUser });
      setUser(minimalUser);
      return data;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async ({ full_name, email, password }) => {
    setLoading(true);
    try {
      const data = await api.register({ full_name, email, password });
      tokenStore.set({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        user: data.user,
      });
      setUser(data.user);
      return data;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      /* ignore */
    }
    tokenStore.clear();
    setUser(null);
  }, []);

  useEffect(() => {
    // No-op: token is already in localStorage
  }, []);

  const value = { user, isAuthenticated: !!user, login, register, logout, loading };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
