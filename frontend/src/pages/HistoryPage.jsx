import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";

export default function HistoryPage() {
  const { token } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadHistory() {
      try {
        const data = await apiFetch("/rooms/history", { token });
        if (active) setRooms(Array.isArray(data) ? data : []);
      } catch {
        if (active) setRooms([]);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadHistory();
    return () => {
      active = false;
    };
  }, [token]);

  return (
    <div className="page">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Solved rooms</p>
          <h1>Your puzzle runs</h1>
          <p className="muted">Completed rooms will collect here once the backend starts saving results.</p>
        </div>
        <Link className="primary" to="/rooms/new">Create room</Link>
      </section>

      {loading ? (
        <div className="card">Loading history...</div>
      ) : rooms.length === 0 ? (
        <div className="card sticker tilt-left">
          <h2>No completed rooms yet</h2>
          <p className="muted">Your first solved BrainJam will show up here with team time and teammates.</p>
          <Link className="primary" to="/puzzles">Browse puzzles</Link>
        </div>
      ) : (
        <section className="grid">
          {rooms.map((room) => (
            <article key={room.id} className="card">
              <p className="eyebrow">Room {room.inviteCode}</p>
              <h2>{room.puzzle?.title || "Puzzle room"}</h2>
              <div className="stat-list">
                <div className="stat">
                  <span className="label">Team time</span>
                  <span className="value">{room.teamTimeSeconds || 0}s</span>
                </div>
                <div className="stat">
                  <span className="label">Role</span>
                  <span className="value">{room.myRole || "Member"}</span>
                </div>
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
