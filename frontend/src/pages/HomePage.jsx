import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/useAuth";

const fallbackPuzzles = [
  { id: "demo-1", title: "Clocktower Cipher", genre: "Cipher", difficulty: "Medium" },
  { id: "demo-2", title: "Museum Switchboard", genre: "Logic", difficulty: "Easy" },
  { id: "demo-3", title: "Signal Kitchen", genre: "Pattern", difficulty: "Hard" },
];

export default function HomePage() {
  const { token, me } = useAuth();
  const [puzzles, setPuzzles] = useState(fallbackPuzzles);

  useEffect(() => {
    let active = true;

    async function loadPuzzles() {
      try {
        const data = await apiFetch("/puzzles");
        if (active && Array.isArray(data) && data.length > 0) setPuzzles(data);
      } catch {
        if (active) setPuzzles(fallbackPuzzles);
      }
    }

    loadPuzzles();
    return () => {
      active = false;
    };
  }, []);

  const genres = useMemo(() => {
    const counts = {};
    puzzles.forEach((puzzle) => {
      counts[puzzle.genre] = (counts[puzzle.genre] || 0) + 1;
    });
    return Object.entries(counts);
  }, [puzzles]);

  return (
    <div className="page">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Collaborative puzzle rooms</p>
          <h1>BrainJam</h1>
          <p className="muted hero-text">
            Squad up, split the puzzle, and race the room timer. Everyone gets a task; everyone sees the team move.
          </p>
          <div className="hero-actions">
            {token ? (
              <>
                <Link className="primary" to="/rooms/new">Create room</Link>
                <Link className="ghost" to="/join">Join with code</Link>
                <Link className="ghost" to="/puzzles">Browse puzzles</Link>
              </>
            ) : (
              <>
                <Link className="primary" to="/register">Create account</Link>
                <Link className="ghost" to="/login">Login</Link>
              </>
            )}
          </div>
          {token && <p className="muted small signed-note">Signed in as @{me?.username || "player"}</p>}
        </div>

        <div className="hero-card sticker tilt-right">
          <h3>Pick your chaos</h3>
          <div className="pill-grid">
            {genres.map(([genre, count]) => (
              <span key={genre} className="pill">{genre} | {count}</span>
            ))}
          </div>
          <div className="divider" />
          <div className="stat-list compact-stats">
            <div className="stat">
              <span className="label">Puzzle packs</span>
              <span className="value">{puzzles.length}</span>
            </div>
            <div className="stat">
              <span className="label">Room size</span>
              <span className="value">2-4</span>
            </div>
          </div>
        </div>
      </section>

      <section className="grid">
        <div className="card sticker tilt-left">
          <p className="eyebrow">Step 01</p>
          <h2>Choose a pack</h2>
          <p className="muted">Browse seeded puzzle packs by genre, difficulty, and room size.</p>
        </div>
        <div className="card sticker">
          <p className="eyebrow">Step 02</p>
          <h2>Ready the squad</h2>
          <p className="muted">Invite teammates, lock the room, and wait for every participant to ready up.</p>
        </div>
        <div className="card sticker tilt-right">
          <p className="eyebrow">Step 03</p>
          <h2>Solve together</h2>
          <p className="muted">Tasks are assigned at start, progress updates live, and the team result lands for everyone.</p>
        </div>
      </section>
    </div>
  );
}
