import { useCallback, useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api/client";
import { AuthContext } from "./authContext";
import { clearToken, getToken, setToken as persistToken } from "./authStorage";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getToken());
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async (nextToken = token) => {
    if (!nextToken) {
      setMe(null);
      setLoading(false);
      return;
    }

    try {
      const user = await apiFetch("/auth/me", { token: nextToken });
      setMe(user);
    } catch {
      clearToken();
      setToken("");
      setMe(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    refreshMe();
  }, [refreshMe]);

  const value = useMemo(() => ({
    token,
    me,
    loading,

    async login(identifier, password) {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ identifier, password }),
      });
      persistToken(data.token);
      setToken(data.token);
      if (data.user) setMe(data.user);
      setLoading(true);
      await refreshMe(data.token);
    },

    async register(username, email, password) {
      const data = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ username, email, password }),
      });
      persistToken(data.token);
      setToken(data.token);
      if (data.user) setMe(data.user);
      setLoading(true);
      await refreshMe(data.token);
    },

    logout() {
      clearToken();
      setToken("");
      setMe(null);
    },
  }), [token, me, loading, refreshMe]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
