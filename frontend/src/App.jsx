import { BrowserRouter } from "react-router-dom";
import SiteHeader from "./components/SiteHeader.jsx";
import AppRoutes from "./routes/AppRoutes.jsx";

function AppLayout({ children }) {
  return (
    <div className="app">
      <SiteHeader />
      <main className="site-main">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <AppRoutes />
      </AppLayout>
    </BrowserRouter>
  );
}
