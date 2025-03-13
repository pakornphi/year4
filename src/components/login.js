import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; // ✅ ใช้ React Router
import "../login.css"; // Import CSS
import "../register.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate(); // ✅ ใช้ navigate() เพื่อเปลี่ยนหน้า

  // const Register = () => {
  //   const [username, setUsername] = useState("");
  //   const [email, setEmail] = useState("");
  //   const [password, setPassword] = useState("");
  //   const [confirmPassword, setConfirmPassword] = useState("");
  //   const [error, setError] = useState("");
  //   const [success, setSuccess] = useState("");
  //   const navigate = useNavigate();

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "/script.js";
    script.async = true;
    document.body.appendChild(script);

    //ล้าง script ตอน unmount
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const [isRegister, setIsRegister] = useState(false);

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

      navigate("/main"); // ✅ เปลี่ยนเส้นทางไปหน้า `main.js`

    } catch (err) {
      setError(err.message);
    }
  };

  return (
      <div className="body">
        <div className="container">
          <div className="form-box login">
            <form className="form" action="">
              <h1>Login</h1>
              <div className="input-box">
                <input type="text" 
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required/>
                <i className="bx bxs-user"></i>
              </div>
              <div className="input-box">
                <input type="password" 
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required/>
                <i className="bx bxs-lock-alt"></i>
              </div>
              <button type="submit" className="btn">Login</button>
              {/* <p>Not have an account? <a href="/register">register here</a></p> */}
            </form>
          </div>

          <div className="form-box register">
            <form className="form" action="">
              <h1>Registration</h1>
              <div className="input-box">
                <input type="text" 
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required/>
                <i className="bx bxs-user"></i>
              </div>
              <div className="input-box">
                <input type="email" 
                placeholder="Email"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required/>
                <i className="bx bxs-envelope"></i>
              </div>
              <div className="input-box">
                <input type="password" 
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required/>
                <i className="bx bxs-lock-alt"></i>
              </div>
                <button type="submit" className="btn">Register</button>
            </form>
          </div>

          <div className="toggle-box">
            <div className="toggle-panel toggle-left">
              <h1>Hello, Welcome!</h1>
              <p>Don't have an account?</p>
              <button className="btn register-btn">Register</button>
            </div>
            <div className="toggle-panel toggle-right">
              <h1>Welcome Back!</h1>
              <p>Already have an account?</p>
              <button className="btn login-btn">Login</button>
            </div>
          </div>

        </div>
      </div>

    );
  };

export default Login;

