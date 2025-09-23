import { createContext, useState, useContext } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token") || null);

  const login = (newToken) => {
    setToken(newToken);
    localStorage.setItem("token", newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
  };

  // universal fetch wrapper that auto logs out on 401
  const fetchWithAuth = async (url, options = {}) => {
    options.headers = {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    };

    const res = await fetch(url, options);

    if (res.status === 401) {
      logout(); // auto clear invalid token
      throw new Error("Unauthorized. Please login again.");
    }

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Request failed");
    }

    return await res.json();
  };

  return (
    <AuthContext.Provider value={{ token, login, logout, fetchWithAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
