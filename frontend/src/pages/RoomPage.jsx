import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";

export default function RoomPage() {
  const { roomId } = useParams();
  const { token, me } = useAuth();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const refreshInFlight = useRef(false);

  async function refresh() {
    if (!token || refreshInFlight.current) return;
    refreshInFlight.current = true;
    setError("");
    setLoading(true);

    try {
      const roomData = await apiFetch(`/rooms/${roomId}`, { token });
      setRoom(roomData);
    } catch (err) {
      setError(err.message || "Failed to load room");
      setRoom(null);
    } finally {
      refreshInFlight.current = false;
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roomId, token]);

  const isOwner = room && me && room.ownerId === me.id;
  const participantCount = room?.members?.filter((member) => member.role !== "SPECTATOR").length || 0;

  const colors = useMemo(() => {
    const palette = ["#FF6B6B", "#6A5CFF", "#2ED9C3", "#FFD166"];
    const map = new Map();
    (room?.members || []).forEach((member, index) => map.set(member.id, palette[index % palette.length]));
    return map;
  }, [room?.members]);

  if (loading) {
    return (
      <div className="page">
        <div className="card">Loading room...</div>
      </div>
    );
  }

  if (!room) {
    return (
      <div className="page">
        <div className="card">Room not found.</div>
        {error && <div className="error">{error}</div>}
      </div>
    );
  }

  return (
    <div className="page">
      <section className="room-header">
        <div>
          <p className="eyebrow">Room {room.id}</p>
          <h1>{room.puzzle?.title || "Puzzle room"}</h1>
          <p className="muted">
            {room.puzzle?.genre || "Puzzle"} | Status: {room.status}
          </p>
        </div>
        <div className="room-meta">
          <div className="stat">
            <span className="label">Invite code</span>
            <span className="value mono">{room.inviteCode}</span>
          </div>
          <div className="stat">
            <span className="label">Room</span>
            <span className="value">
              {room.locked ? "Locked" : `${participantCount}/${room.maxPlayers || 4}`}
            </span>
          </div>
        </div>
      </section>

      <section className="room-grid">
        <div className="card sticker tilt-left">
          <h2>Lobby</h2>
          <p className="muted small">
            Owner participates: <strong>{room.ownerParticipates ? "Yes" : "No (spectating)"}</strong>
          </p>
          <div className="list">
            {room.members?.map((member) => (
              <div
                className="list-item member-card"
                key={member.id}
                style={{
                  borderColor: colors.get(member.id),
                  background: `${colors.get(member.id)}14`,
                }}
              >
                <div>
                  <div className="strong">@{member.username}</div>
                  <div className="muted small">{member.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {isOwner && (
          <div className="card sticker">
            <h2>Owner controls</h2>
            <div className="muted small">
              Locking, kicking, ready-up, and starting the room comes in the next phases.
            </div>
          </div>
        )}
      </section>

      {error && <div className="error">{error}</div>}
    </div>
  );
}

