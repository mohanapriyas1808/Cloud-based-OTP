import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import OTPPage from "./OTPPage";  // ✅ Correct component name
import AIDetailsPage from "./AIDetailsPage";  // ✅ Correct component name

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<OTPPage />} />
        <Route path="/ai" element={<AIDetailsPage />} />  {/* ✅ Fixes "/ai" route */}
      </Routes>
    </Router>
  );
}

export default App;
