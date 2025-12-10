import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SideBar from "./components/Sidebar";
import Home from "./pages/Home";
import Workouts from "./pages/Workouts";
import Progress from "./pages/Progress";
import Settings from "./pages/Settings";
import { useState } from "react";
import mobile_sidebar_btn from "../src/assets/mobile_sidebar_btn.png"

function App() {
	const [isOpen, setIsOpen] = useState(false);
  return (
		<Router>
		<div className="flex">
		{/* Hamburger button - mobile only */}
			<button 
			className="md:hidden p-4 " 
			onClick={() => setIsOpen(!isOpen)}
			>
			<img height={30} width={30} src={mobile_sidebar_btn} />
			</button>

		{isOpen && (
  		<div className="md:hidden fixed inset-0 backdrop-blur-[3px] z-50">
			<button 
			onClick={() => setIsOpen(false)}
			className="absolute top-4 right-4 text-2xl"
			>
			X
			</button>
			<SideBar />
			</div>
		)}
		{/* Desktop sidebar - always visible */}
		<div className="hidden md:block">
		<SideBar />
		</div>
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
