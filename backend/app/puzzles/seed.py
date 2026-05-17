from __future__ import annotations

from sqlalchemy.exc import OperationalError, ProgrammingError

from app.extensions import db
from app.models import PuzzlePack, PuzzleTask


def ensure_seed_puzzles() -> None:
    """
    Seed initial puzzle packs + tasks if the DB is empty.

    Safe to call on startup; no-ops if puzzles already exist.
    """
    try:
        existing = db.session.query(PuzzlePack.id).limit(1).first()
    except (OperationalError, ProgrammingError):
        # DB unreachable or migrations not applied yet.
        db.session.rollback()
        return

    if existing is not None:
        return

    packs: list[PuzzlePack] = [
        PuzzlePack(
            title="Clocktower Cipher",
            slug="clocktower",
            genre="Cipher",
            difficulty="Medium",
            description="Decode scattered clock notes before the final bell locks the tower.",
            estimated_minutes=18,
            is_active=True,
            tasks=[
                PuzzleTask(title="Decode the bell notes", prompt="Find the hidden phrase in the bell schedule.", answer="MIDNIGHT TOLL", order_index=1, difficulty="Medium"),
                PuzzleTask(title="Match the gears", prompt="Pair each gear size with its correct symbol to reveal the key.", answer="GEAR KEY", order_index=2, difficulty="Medium"),
                PuzzleTask(title="Align the hands", prompt="Set the clock hands to the four marked times and read the letters.", answer="TIMELOCK", order_index=3, difficulty="Medium"),
                PuzzleTask(title="Final chime", prompt="Use the decoded key to open the last latch before the bell rings.", answer="OPEN", order_index=4, difficulty="Medium"),
            ],
        ),
        PuzzlePack(
            title="Museum Switchboard",
            slug="museum",
            genre="Logic",
            difficulty="Easy",
            description="Route gallery lights, labels, and exhibit alarms into the right sequence.",
            estimated_minutes=12,
            is_active=True,
            tasks=[
                PuzzleTask(title="Gallery order", prompt="Reorder the gallery rooms using the curator’s clues.", answer="A-B-C-D", order_index=1, difficulty="Easy"),
                PuzzleTask(title="Light routing", prompt="Connect the switches so only one exhibit is lit at a time.", answer="SEQUENCE", order_index=2, difficulty="Easy"),
                PuzzleTask(title="Label swap", prompt="Swap two labels to make every description match its artifact.", answer="SWAP", order_index=3, difficulty="Easy"),
                PuzzleTask(title="Alarm check", prompt="Identify which sensor is false-triggering by eliminating the others.", answer="SENSOR 3", order_index=4, difficulty="Easy"),
            ],
        ),
        PuzzlePack(
            title="Signal Kitchen",
            slug="signal",
            genre="Pattern",
            difficulty="Hard",
            description="Find the recipe hidden in kitchen sounds, colors, and station codes.",
            estimated_minutes=22,
            is_active=True,
            tasks=[
                PuzzleTask(title="Station codes", prompt="Translate the stove station codes into ingredients.", answer="SALT", order_index=1, difficulty="Hard"),
                PuzzleTask(title="Color timing", prompt="Map the timer colors to durations to form a number sequence.", answer="3142", order_index=2, difficulty="Hard"),
                PuzzleTask(title="Sound pattern", prompt="Match kitchen sounds to a repeating rhythm to find the missing beat.", answer="CLAP", order_index=3, difficulty="Hard"),
                PuzzleTask(title="Recipe assembly", prompt="Combine the decoded pieces to produce the final recipe keyword.", answer="SOUFFLE", order_index=4, difficulty="Hard"),
            ],
        ),
    ]

    for pack in packs:
        db.session.add(pack)
    db.session.commit()

