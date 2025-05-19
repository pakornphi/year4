import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/login";
import Register from "./components/register";
import Main from "./components/main";
import Dashboard from "./components/dashboard";
import ProtectedRoute from "./components/ProtectedRoute"; // ✅ เพิ่ม

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* ✅ ต้อง login ก่อนถึงเข้าได้ */}
        <Route
          path="/main"
          element={
            <ProtectedRoute>
              <Main />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<h1>Welcome! Please <a href="/login">Login</a></h1>} />
      </Routes>
    </Router>
  );
}

export default App;
