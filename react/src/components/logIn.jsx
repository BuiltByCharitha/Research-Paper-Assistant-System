import { useState } from "react";
import { login as loginAPI } from "../api/api";
import { useAuth } from "../AuthContext";

export default function Login() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) return;
    setLoading(true);
    try {
      const data = await loginAPI(username, password);
      if (!data.access_token) throw new Error("No access token received");
      login(data.access_token);
    } catch (err) {
      alert("Login failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}
