import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";

const fallbackPuzzles = [
  {
    id: "clocktower",
    title: "Clocktower Cipher",
    genre: "Cipher",
    difficulty: "Medium",
    estimatedMinutes: 18,
    taskCount: 4,
    description: "Decode scattered clock notes before the final bell locks the tower.",
  },
  {
    id: "museum",
    title: "Museum Switchboard",
    genre: "Logic",
    difficulty: "Easy",
    estimatedMinutes: 12,
    taskCount: 3,
    description: "Route gallery lights, labels, and exhibit alarms into the right sequence.",
  },
  {
    id: "signal",
    title: "Signal Kitchen",
    genre: "Pattern",
    difficulty: "Hard",
    estimatedMinutes: 22,
    taskCount: 4,
    description: "Find the recipe hidden in kitchen sounds, colors, and station codes.",
  },
];

export default function PuzzleBrowserPage() {
  const [puzzles, setPuzzles] = useState(fallbackPuzzles);
  const [genres, setGenres] = useState(["All"]);
  const [difficulties, setDifficulties] = useState(["All"]);
  const [genre, setGenre] = useState("All");
  const [difficulty, setDifficulty] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadMeta() {
      try {
        const [genreData, allPuzzles] = await Promise.all([
          apiFetch("/puzzles/genres"),
          apiFetch("/puzzles"),
        ]);

        if (!active) return;

        if (Array.isArray(genreData) && genreData.length) {
          setGenres(["All", ...genreData]);
        } else {
          setGenres(["All", ...new Set(allPuzzles.map((puzzle) => puzzle.genre).filter(Boolean))]);
        }

        setDifficulties(["All", ...new Set(allPuzzles.map((puzzle) => puzzle.difficulty).filter(Boolean))]);
      } catch {
        if (!active) return;
        setGenres(["All", ...new Set(fallbackPuzzles.map((puzzle) => puzzle.genre).filter(Boolean))]);
        setDifficulties(["All", ...new Set(fallbackPuzzles.map((puzzle) => puzzle.difficulty).filter(Boolean))]);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadMeta();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadPuzzles() {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (genre !== "All") params.set("genre", genre);
        if (difficulty !== "All") params.set("difficulty", difficulty);

        const data = await apiFetch(params.size ? `/puzzles?${params.toString()}` : "/puzzles");
        if (active && Array.isArray(data)) setPuzzles(data);
      } catch {
        if (!active) return;
        setPuzzles(fallbackPuzzles);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadPuzzles();
    return () => {
      active = false;
    };
  }, [genre, difficulty]);

  const filtered = useMemo(() => puzzles, [puzzles]);

  return (
    <div className="page">
      <section className="page-heading">
        <div>
          <p className="eyebrow">Puzzle browser</p>
          <h1>Pick a pack</h1>
          <p className="muted">Seeded puzzle rooms for teams of two to four.</p>
        </div>
        <Link className="primary" to="/rooms/new">Create room</Link>
      </section>

      <section className="toolbar">
        <div className="segmented">
          {genres.map((item) => (
            <button key={item} className={item === genre ? "segment active" : "segment"} onClick={() => setGenre(item)}>
              {item}
            </button>
          ))}
        </div>
        <label className="inline-select">
          Difficulty
          <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
            {difficulties.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
      </section>

      {loading ? (
        <div className="card">Loading puzzles...</div>
      ) : (
        <section className="grid">
          {filtered.map((puzzle, index) => (
            <article key={puzzle.id} className={`card puzzle-card ${index % 2 ? "tilt-right" : "tilt-left"}`}>
              <div className="card-topline">
                <span className="pill">{puzzle.genre}</span>
                <span className="pill yellow">{puzzle.difficulty}</span>
              </div>
              <h2>{puzzle.title}</h2>
              <p className="muted">{puzzle.description || "A collaborative puzzle pack with separate tasks for each player."}</p>
              <div className="stat-list">
                <div className="stat">
                  <span className="label">Time</span>
                  <span className="value">{puzzle.estimatedMinutes || 15}m</span>
                </div>
                <div className="stat">
                  <span className="label">Tasks</span>
                  <span className="value">{puzzle.taskCount || 4}</span>
                </div>
              </div>
              <Link className="primary" to={`/rooms/new?puzzleId=${encodeURIComponent(puzzle.id)}`}>Create room</Link>
            </article>
          ))}
          {filtered.length === 0 && <div className="card">No puzzle packs match those filters.</div>}
        </section>
      )}
    </div>
  );
}
