import { Link } from "react-router-dom";
import logo_for_now from "../assets/logo_for_now.jpg";

function SideBar() {
  const navItems = [
    { label: "Home", path: "/" },
    { label: "Workouts", path: "/workouts" },
    { label: "Progress", path: "/progress" },
    { label: "Settings", path: "/settings" },
  ];

  return (
    <div className="h-screen w-70 bg-white">
      {/* Logo Section */}
      <div className="border-b border-r border-gray-200 rounded">
        <div className="flex items-center gap-3">
          <img
            src={logo_for_now}
            width={90}
            height={90}
            className="rounded-xl pr-0 m-4 mr-0 pb-4"
          />  
		  <div>
			<h1 className="text-2xl font-slab">LIFTS REC</h1>
			<p className="text-xs text-gray-600">
				Stay Consistent, Achieve More
			</p>
		</div>
        </div>
		
      </div>

      {/* Navigation Links */}
      <nav className="p-4 space-y-2 border-r border-gray-200 rounded h-screen">
		<div> {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="block px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-100 hover:text-gray-700 transition-colors font-oswald"
          >
            {item.label}
          </Link>
        ))} </div>

      </nav>
    </div>
  );
}

export default SideBar;
