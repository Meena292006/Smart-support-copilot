// frontend/src/App.jsx
import React from "react";
import Navbar from "./components/Navbar.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import Dashboard from "./components/Dashboard.jsx";  // ← This is the NEW epic one!

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />
      
      {/* Full-width layout: Chat on left, Dashboard on right */}
      <div className="flex flex-col lg:flex-row h-screen">
        <div className="w-full lg:w-1/2 xl:w-2/5 bg-white border-r border-gray-200 overflow-hidden">
          <ChatWindow />
        </div>
        <div className="w-full lg:w-1/2 xl:w-3/5 overflow-y-auto">
          <Dashboard />   {/* ← This now shows the FULL BEAUTIFUL dashboard */}
        </div>
      </div>
    </div>
  );
}

export default App;