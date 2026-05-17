import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";

export default function JoinRoomPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [inviteCode, setInviteCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      const room = await apiFetch("/rooms/join", {
        method: "POST",
        token,
        body: JSON.stringify({ inviteCode }),
      });
      navigate(`/rooms/${room.id}`);
    } catch (err) {
      setError(err.message || "Failed to join room");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page narrow">
      <div className="card sticker tilt-right">
        <p className="eyebrow">Invite code</p>
        <h1>Join a room</h1>
        <p className="muted">Paste the room code from your teammate and jump into the lobby.</p>

        <form className="form" onSubmit={handleSubmit}>
          <label>
            Room code
            <input
              className="code-input"
              value={inviteCode}
              onChange={(event) => setInviteCode(event.target.value.toUpperCase())}
              placeholder="ABC12345"
              required
            />
          </label>
          {error && <div className="error">{error}</div>}
          <button className="primary" type="submit" disabled={busy || !inviteCode}>
            {busy ? "Joining..." : "Join room"}
          </button>
        </form>
      </div>
    </div>
  );
}
