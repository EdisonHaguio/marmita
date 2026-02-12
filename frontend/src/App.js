import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import Login from "./pages/Login";
import AttendantDashboard from "./pages/AttendantDashboard";
import KitchenDisplay from "./pages/KitchenDisplay";
import AdminDashboard from "./pages/AdminDashboard";
import { Toaster } from "./components/ui/sonner";

// Auto-detect API URL (works both online and offline)
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || window.location.origin;
export const API = `${BACKEND_URL}/api`;

export const axiosInstance = axios.create({
  baseURL: API,
});

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  return (
    <div className="App min-h-screen">
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={
              !user ? (
                <Login onLogin={handleLogin} />
              ) : user.role === "admin" ? (
                <Navigate to="/admin" />
              ) : (
                <Navigate to="/atendente" />
              )
            }
          />
          <Route
            path="/atendente"
            element={
              user && user.role === "attendant" ? (
                <AttendantDashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" />
              )
            }
          />
          <Route
            path="/cozinha"
            element={<KitchenDisplay />}
          />
          <Route
            path="/admin"
            element={
              user && user.role === "admin" ? (
                <AdminDashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" />
              )
            }
          />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" />
    </div>
  );
}

export default App;