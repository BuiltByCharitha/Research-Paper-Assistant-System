import { useState } from "react";
import { signup, login as loginAPI } from "../api/api";
import { useAuth } from "../AuthContext";

export default function SignUp() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignUp = async () => {
    if (!username || !password) return;
    setLoading(true);
    try {
      // 1. Sign up user
      await signup(username, password);

      // 2. Log in right after signup
      const data = await loginAPI(username, password);
      if (!data.access_token) throw new Error("No access token received");

      // 3. Store token in context
      login(data.access_token);
    } catch (err) {
      alert("Error signing up: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Sign Up</h2>
      <input
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
      <button onClick={handleSignUp} disabled={loading}>
        {loading ? "Signing up..." : "Sign Up"}
      </button>
    </div>
  );
}
