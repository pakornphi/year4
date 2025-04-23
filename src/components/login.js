import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles.css";
import { FaUser, FaLock } from "react-icons/fa";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.message);

      localStorage.setItem("token", data.token);
      alert("✅ Login successful!");
      navigate("/main");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-container">
      {/* 🔹 ด้านซ้าย - Register info */}
      <div className="login-left">
        <div className="welcome-content">
          <h2>Hello, Welcome!</h2>
          <p>Don't have an account?</p>
          <button className="register-btn" onClick={() => navigate("/register")}>
            Register
          </button>
        </div>
      </div>

      {/* 🔹 ด้านขวา - Login form */}
      <div className="login-right">
        <h2>Login</h2>
        {error && <p className="error-message">{error}</p>}
        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group">
            <FaUser className="icon" />
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="input-group">
            <FaLock className="icon" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
