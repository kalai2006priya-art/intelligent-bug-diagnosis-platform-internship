import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('bug_platform_token'));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('bug_platform_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
          localStorage.setItem('bug_platform_user', JSON.stringify(userData));
        } catch (err) {
          console.warn('Session expired or invalid:', err);
          logout();
        }
      }
      setLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (email, password) => {
    const res = await authApi.login(email, password);
    localStorage.setItem('bug_platform_token', res.access_token);
    localStorage.setItem('bug_platform_user', JSON.stringify(res.user));
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const signup = async (name, email, password) => {
    const res = await authApi.signup(name, email, password);
    localStorage.setItem('bug_platform_token', res.access_token);
    localStorage.setItem('bug_platform_user', JSON.stringify(res.user));
    setToken(res.access_token);
    setUser(res.user);
    return res.user;
  };

  const logout = () => {
    localStorage.removeItem('bug_platform_token');
    localStorage.removeItem('bug_platform_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isAuthenticated: !!token && !!user,
      loading,
      login,
      signup,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
