import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export default function SiteHeader() {
  const auth = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    auth.logout();
    navigate("/login");
  }

  return (
    <header className="site-header">
      <Link className="brand" to="/">BrainJam</Link>
      <nav className="nav">
        <Link className="nav-link" to="/puzzles">Puzzles</Link>
        {auth.token ? (
          <>
            <Link className="nav-link" to="/history">History</Link>
            <span className="user-chip">@{auth.me?.username || "player"}</span>
            <button className="ghost compact" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link className="nav-link" to="/login">Login</Link>
            <Link className="nav-link" to="/register">Register</Link>
          </>
        )}
      </nav>
    </header>
  );
}
