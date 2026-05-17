import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";

const fallbackPuzzles = [
  { id: "clocktower", title: "Clocktower Cipher", genre: "Cipher" },
  { id: "museum", title: "Museum Switchboard", genre: "Logic" },
  { id: "signal", title: "Signal Kitchen", genre: "Pattern" },
];

export default function CreateRoomPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [puzzles, setPuzzles] = useState(fallbackPuzzles);
  const [puzzleId, setPuzzleId] = useState(searchParams.get("puzzleId") || fallbackPuzzles[0].id);
  const [puzzleDetail, setPuzzleDetail] = useState(null);
  const [maxPlayers, setMaxPlayers] = useState(4);
  const [ownerParticipates, setOwnerParticipates] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadPuzzles() {
      try {
        const data = await apiFetch("/puzzles");
        if (!active || !Array.isArray(data) || data.length === 0) return;
        setPuzzles(data);
        if (!searchParams.get("puzzleId")) setPuzzleId(data[0].id);
      } catch {
        if (active) setPuzzles(fallbackPuzzles);
      }
    }

    loadPuzzles();
    return () => {
      active = false;
    };
  }, [searchParams]);

  useEffect(() => {
    let active = true;

    async function loadPuzzleDetail() {
      if (!puzzleId) return;
      try {
        const data = await apiFetch(`/puzzles/${encodeURIComponent(puzzleId)}`);
        if (active) setPuzzleDetail(data);
      } catch {
        if (active) setPuzzleDetail(null);
      }
    }

    loadPuzzleDetail();
    return () => {
      active = false;
    };
  }, [puzzleId]);

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      const room = await apiFetch("/rooms", {
        method: "POST",
        token,
        body: JSON.stringify({ puzzleId, maxPlayers, ownerParticipates }),
      });
      navigate(`/rooms/${room.id}`);
    } catch (err) {
      setError(err.message || "Failed to create room");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page narrow">
      <div className="card sticker tilt-left">
        <p className="eyebrow">Room setup</p>
        <h1>Create a room</h1>
        <p className="muted">Choose the puzzle, tune the squad size, and launch a lobby with an invite code.</p>

        <form className="form" onSubmit={handleSubmit}>
          <label>
            Puzzle
            <select value={puzzleId} onChange={(event) => setPuzzleId(event.target.value)} required>
              {puzzles.map((puzzle) => (
                <option key={puzzle.id} value={puzzle.id}>{puzzle.title} | {puzzle.genre}</option>
              ))}
            </select>
          </label>

          {puzzleDetail && (
            <div className="card inset">
              <div className="card-topline">
                <span className="pill">{puzzleDetail.genre}</span>
                <span className="pill yellow">{puzzleDetail.difficulty}</span>
              </div>
              <div className="strong">{puzzleDetail.title}</div>
              <p className="muted small">{puzzleDetail.description}</p>
              <div className="stat-list">
                <div className="stat">
                  <span className="label">Time</span>
                  <span className="value">{puzzleDetail.estimatedMinutes || 15}m</span>
                </div>
                <div className="stat">
                  <span className="label">Tasks</span>
                  <span className="value">{puzzleDetail.taskCount || puzzleDetail.tasks?.length || 0}</span>
                </div>
              </div>
              {Array.isArray(puzzleDetail.tasks) && puzzleDetail.tasks.length > 0 && (
                <div className="list compact">
                  {puzzleDetail.tasks.slice(0, 4).map((task) => (
                    <div key={task.id} className="list-item">
                      <div className="task-main">
                        <div className="strong">{task.title}</div>
                        <div className="muted small">{task.difficulty || puzzleDetail.difficulty}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <label>
            Max players
            <select value={maxPlayers} onChange={(event) => setMaxPlayers(Number(event.target.value))}>
              {[2, 3, 4].map((count) => <option key={count} value={count}>{count}</option>)}
            </select>
          </label>
          <label className="toggle">
            <input type="checkbox" checked={ownerParticipates} onChange={(event) => setOwnerParticipates(event.target.checked)} />
            <span>Owner participates</span>
          </label>
          {error && <div className="error">{error}</div>}
          <button className="primary" type="submit" disabled={busy || !puzzleId}>
            {busy ? "Creating..." : "Create room"}
          </button>
        </form>
      </div>
    </div>
  );
}
