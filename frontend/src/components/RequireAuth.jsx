import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export default function RequireAuth({ children }) {
  const { token, loading } = useAuth();

  if (loading) {
    return (
      <div className="page">
        <div className="card">Loading...</div>
      </div>
    );
  }

  if (!token) return <Navigate to="/login" replace />;
  return children;
}
