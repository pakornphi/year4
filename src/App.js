import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/login";
import Register from "./components/register";
import Main from "./components/main";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/main" element={<Main />} />
        <Route path="/" element={<h1>Welcome! Please <a href="/login">Login</a></h1>} />
      </Routes>
    </Router>
  );
}

export default App;
