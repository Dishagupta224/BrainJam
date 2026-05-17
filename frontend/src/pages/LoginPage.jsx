import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(identifier, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page narrow auth-page">
      <div className="card sticker">
        <p className="eyebrow">Player check-in</p>
        <h1>Welcome back</h1>
        <p className="muted">Log in to rejoin your room or start a new puzzle run.</p>
        <form className="form" onSubmit={handleSubmit}>
          <label>
            Username or email
            <input value={identifier} onChange={(event) => setIdentifier(event.target.value)} placeholder="brainjammer" required />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="********" required />
          </label>
          {error && <div className="error">{error}</div>}
          <button className="primary" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="muted small">New here? <Link to="/register">Create an account</Link></p>
      </div>
    </div>
  );
}
