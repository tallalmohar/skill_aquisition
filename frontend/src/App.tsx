import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SideBar from "./components/Sidebar";
import Home from "./pages/Home";
import Workouts from "./pages/Workouts";
import Progress from "./pages/Progress";
import Settings from "./pages/Settings";

function App() {
  return (
    <Router>
      <div className="flex">
        <SideBar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/workouts" element={<Workouts />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
