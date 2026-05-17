# Phase 1 Product And UX Spec

## Product Name

BrainJam

The repository can remain named BrainCollab, but the user-facing app should keep the demo frontend identity as BrainJam. The name already matches the playful puzzle-room concept and appears throughout the pasted React demo.

## Product Goal

BrainJam is a collaborative puzzle-room web app where players create or join short puzzle sessions, split tasks across the team, mark themselves ready, solve their assigned challenge, and see realtime team progress until the room is complete.

The app should feel like a lightweight party-puzzle tool: fast to enter, clear during play, and visually energetic without becoming hard to scan.

## Visual Direction

Keep the current BrainJam style from `frontend_demo`:

- Soft lavender page background with subtle playful texture.
- White and pale-purple cards with thick dark borders.
- Offset hard shadows for a paper-sticker feel.
- Rounded but chunky controls.
- Uppercase micro-labels and button text.
- Bright accent colors: purple, coral, teal, and yellow.
- Slight card tilts and tape/sticker details for selected feature cards.

The redesign should stay playful rather than becoming a minimal SaaS dashboard. During the active puzzle room, the layout can become a little denser and more game-like, but it should still use the same visual language.

## Core Product Decisions

- Rooms support configurable player counts: 2, 3, or 4 players.
- Default room size is 4 players.
- Room owners may choose whether they participate when creating the room.
- If the owner participates, the owner receives a task like everyone else.
- If the owner does not participate, the owner can manage and spectate the room.
- Tasks are randomly assigned when the owner starts the room.
- A room can only start when all participating members are ready.
- Puzzle content is fixed seed data for the initial version.
- Admin-created puzzle content is out of scope for the first build.
- Completed rooms are saved in user history.
- Realtime room updates should cover joins, leaves/removals, ready state, room settings, start, task completion, and final result.
- Flask-SocketIO is preferred for this project because named rooms and event-style realtime updates fit the product better than raw socket messages.

## Main User Roles

- Guest: Can view the landing screen and auth screens. Must register or log in before creating or joining rooms.
- Member: Can browse puzzles, create rooms, join rooms, ready up, and complete assigned tasks.
- Owner: Can configure a room, regenerate invite code, lock the room, remove members before start, and start the session.
- Spectating owner: Can manage the room without receiving a task when `ownerParticipates` is false.

## Core Screens

1. Landing or Home
2. Register
3. Login
4. Puzzle Browser
5. Create Room
6. Join Room
7. Room Lobby
8. Active Puzzle Room
9. Completion / Results
10. User History

## Screen Layouts

### 1. Landing Or Home

Purpose: Explain the app quickly and route users into auth, puzzle browsing, creating, or joining.

Layout:

- Header with BrainJam brand on the left.
- Right side shows Login and Register for guests, or user status and Logout for logged-in users.
- Main hero uses two-column layout on desktop and stacked layout on mobile.
- Left side contains eyebrow text, large `BrainJam` title, short value statement, and auth/create/join actions.
- Right side contains a sticker-style summary card showing available puzzle genres and seeded puzzle count.
- Logged-in users see create/join cards below the hero.

Primary actions:

- Guest: Create an account, Login.
- Logged-in user: Create room, Join room, Browse puzzles.

### 2. Register

Purpose: Create a user account.

Layout:

- Centered narrow card.
- Title: `Create your account`.
- Fields: username, email, password.
- Primary button: `Create account`.
- Secondary link to login.
- Inline error block using the existing coral error style.

Validation:

- Username minimum 3 characters.
- Password minimum 8 characters.
- Email required and unique.

### 3. Login

Purpose: Authenticate an existing user.

Layout:

- Centered narrow card.
- Title: `Welcome back`.
- Fields: username/email and password.
- Primary button: `Login`.
- Secondary link to register.
- Inline error block.

Behavior:

- On success, redirect to home or to a protected page the user tried to access.

### 4. Puzzle Browser

Purpose: Let users scan available puzzle packs before creating a room.

Layout:

- Page header with title and short muted description.
- Filter row with genre pills and difficulty selector.
- Puzzle cards in a responsive grid.
- Each puzzle card shows title, genre, difficulty, estimated time, player count support, and a short description.
- Card action: `Create room`.

Data shown:

- Puzzle title.
- Genre.
- Difficulty.
- Estimated duration.
- Number of tasks.
- Supported room sizes.

Empty/loading states:

- Loading card while fetching.
- Empty card if no puzzle packs match filters.

### 5. Create Room

Purpose: Configure a new room from a chosen puzzle.

Layout:

- Sticker card with selected puzzle summary at top.
- Form controls:
  - Puzzle selector.
  - Max players selector: 2, 3, 4.
  - Owner participates checkbox.
  - Optional room lock toggle, default unlocked.
- Primary button: `Create room`.

Behavior:

- Backend creates room with invite code.
- Creator is added as owner.
- If owner participates, owner is also counted as a participant.
- Redirect to room lobby after creation.

### 6. Join Room

Purpose: Join an existing room by invite code.

Layout:

- Narrow card or home-page card.
- Invite code input in uppercase monospace style.
- Primary button: `Join room`.
- Error block for invalid, locked, full, completed, or already-started rooms.

Behavior:

- Users can only join rooms with status `OPEN`.
- Locked rooms reject new joins.
- Full rooms reject new joins.
- Successful join redirects to lobby.

### 7. Room Lobby

Purpose: Prepare the team before the puzzle starts.

Layout:

- Header row with room id, puzzle title, genre, status, invite code, member count, and room lock state.
- Progress or readiness strip showing every participant.
- Lobby card listing members with username, role, and ready state.
- Current user button: `I'm ready` or `Mark not ready`.
- Owner controls card visible only to owner before start:
  - Lock room toggle.
  - Max players selector.
  - Regenerate invite code.
  - Remove member buttons.
  - Start room button.

Start rules:

- Start is enabled only when all participating members are ready.
- A room must have at least 2 participating players.
- Spectating owner does not need to be ready unless they are participating.

Realtime updates:

- Member joined.
- Member removed.
- Member ready state changed.
- Settings changed.
- Invite code regenerated.
- Room started.

### 8. Active Puzzle Room

Purpose: Let players complete assigned tasks while tracking team progress.

Layout:

- Room header with puzzle title, status, invite code, elapsed team time, and room size.
- Team progress card with a segmented or horizontal progress bar.
- Participant legend using the existing accent color palette.
- Main grid:
  - Player task card for the current user's assigned task.
  - Team task list showing all task titles, assignees, and statuses.
  - Optional room activity feed for realtime events.

Task card:

- Task title.
- Prompt/instructions.
- Optional answer input if puzzle type requires validation.
- `Mark complete` or `Submit answer` button.
- Status pill: assigned, in progress, completed.

Behavior:

- Each participant receives one task initially.
- For MVP, task completion can be manual: player clicks `Mark complete`.
- Later phases can support answer validation per puzzle type.
- All clients update when any task is completed.

Realtime updates:

- Task assigned.
- Task completed.
- Team progress changed.
- Room completed.

### 9. Completion / Results

Purpose: Celebrate and summarize the session when all tasks are complete.

Layout:

- Centered completion overlay or full results screen using the current completion panel style.
- Eyebrow: `Solved`.
- Title: `Room complete`.
- Team time.
- Puzzle name and genre.
- Participant list with completion statuses.
- Actions:
  - Back to home.
  - View history.
  - Create another room with same puzzle.

Behavior:

- Room status becomes `COMPLETED`.
- Completion timestamp and team duration are saved.
- All clients receive completion event.

### 10. User History

Purpose: Let logged-in users see completed rooms.

Layout:

- Header with `Your puzzle runs`.
- List or grid of completed room cards.
- Each card shows puzzle title, room code, date, role, team time, and members.
- Empty state invites user to create a first room.

Scope:

- History is useful but can come after the core create/join/play loop.
- Backend should still save completed rooms from the start so history can be added without data loss.

## Suggested Navigation

- `/` - Home
- `/register` - Register
- `/login` - Login
- `/puzzles` - Puzzle browser
- `/rooms/new` - Create room
- `/join` - Join by invite code
- `/rooms/:roomId` - Room lobby, active room, or completed room depending on room status
- `/history` - Completed room history

## Initial Data Model Notes

These are not final database schemas, but they define the product objects needed in later phases.

- User: username, email, password hash, created date.
- PuzzlePack: title, genre, difficulty, description, estimated duration, active flag.
- PuzzleTask: puzzle pack id, title, prompt, order/index.
- Room: owner id, puzzle pack id, invite code, status, max members, locked flag, owner participates flag, timestamps.
- RoomMember: room id, user id, role, ready flag, joined timestamp.
- RoomTask: room id, puzzle task id, assigned user id, status, completed timestamp, duration seconds.
- RoomEvent: room id, event type, actor id, payload, created timestamp.

## MVP Acceptance Criteria

- A user can register, log in, and log out.
- A logged-in user can browse seeded puzzle packs.
- A logged-in user can create a room from a puzzle pack.
- A room has an invite code.
- Another logged-in user can join by invite code.
- Participants can mark ready/not ready.
- Owner can start the room after all participants are ready.
- Tasks are assigned to participants when the room starts.
- A participant can complete their assigned task.
- Realtime updates are visible to everyone in the room.
- When all tasks are complete, the room shows a team result and saves completion data.

## Open Questions For Later Phases

- Should task completion remain manual, or should some puzzle packs require answer validation?
- Should users be allowed to leave an active room?
- Should disconnected users remain assigned to their task?
- Should invite codes expire?
- Should puzzle packs support more tasks than players, creating multiple rounds?
- Should room history be private to participants only, or visible to owners as a management view?
