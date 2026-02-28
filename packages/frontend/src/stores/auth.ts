import { create } from 'zustand';
import { api } from '@/lib/api';

interface AuthState {
  user: { id: string; username: string } | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,

  login: async (username, password) => {
    const res = await api.post<{
      success: boolean;
      data: { token: string; user: { id: string; username: string } };
    }>('/api/auth/login', { username, password });

    api.setToken(res.data.token);
    set({ user: res.data.user });
  },

  logout: () => {
    api.setToken(null);
    set({ user: null });
  },

  checkAuth: async () => {
    try {
      const token = api.getToken();
      if (!token) {
        set({ isLoading: false });
        return;
      }
      const res = await api.get<{
        success: boolean;
        data: { id: string; username: string };
      }>('/api/auth/me');
      set({ user: res.data, isLoading: false });
    } catch {
      set({ user: null, isLoading: false });
    }
  },
}));
