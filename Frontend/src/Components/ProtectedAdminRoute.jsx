import { Navigate } from "react-router-dom";

export default function ProtectedAdminRoute({ children }) {
  const role = localStorage.getItem("role");

  if (role !== "Admin") {
    return <Navigate to="/" replace />;
  }

  return children;
}
