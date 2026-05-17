import { Navigate, Route, Routes } from "react-router-dom";
import RequireAuth from "../components/RequireAuth.jsx";
import CreateRoomPage from "../pages/CreateRoomPage.jsx";
import HistoryPage from "../pages/HistoryPage.jsx";
import HomePage from "../pages/HomePage.jsx";
import JoinRoomPage from "../pages/JoinRoomPage.jsx";
import LoginPage from "../pages/LoginPage.jsx";
import PuzzleBrowserPage from "../pages/PuzzleBrowserPage.jsx";
import RegisterPage from "../pages/RegisterPage.jsx";
import RoomPage from "../pages/RoomPage.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/puzzles" element={<PuzzleBrowserPage />} />
      <Route
        path="/rooms/new"
        element={(
          <RequireAuth>
            <CreateRoomPage />
          </RequireAuth>
        )}
      />
      <Route
        path="/join"
        element={(
          <RequireAuth>
            <JoinRoomPage />
          </RequireAuth>
        )}
      />
      <Route
        path="/rooms/:roomId"
        element={(
          <RequireAuth>
            <RoomPage />
          </RequireAuth>
        )}
      />
      <Route
        path="/history"
        element={(
          <RequireAuth>
            <HistoryPage />
          </RequireAuth>
        )}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
