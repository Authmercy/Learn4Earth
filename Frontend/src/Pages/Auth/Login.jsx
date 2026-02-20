import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [apiError, setApiError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setApiError("");

    const formData = new URLSearchParams();
    formData.append("grant_type", "password");
    formData.append("username", email);
    formData.append("password", password);
    formData.append("scope", "");
    formData.append("client_id", "");
    formData.append("client_secret", "");

    try {
      const response = await fetch("http://206.189.56.166:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      const data = await response.json();

      /* LOGIN OK */
      if (response.status === 200) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        navigate("/dashboard");
        return;
      }

      /* COMPTE NON ACTIVÉ */
      if (response.status === 403) {
        navigate("/verify-otp", { state: { email } });
        return;
      }

      /* IDENTIFIANTS INCORRECTS */
      if (response.status === 401) {
        setApiError("Email ou mot de passe incorrect");
        return;
      }

      setApiError("Erreur inconnue");
    } catch {
      setApiError("Impossible de contacter le serveur");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 flex items-center justify-center px-6">

      <div className="w-full max-w-5xl bg-white shadow-2xl rounded-2xl overflow-hidden grid grid-cols-1 md:grid-cols-2">

        <div className="hidden md:block">
          <img
            src="/images/login-side.png"
            alt="AI Illustration"
            className="w-full h-full object-cover"
          />
        </div>

        <div className="p-10 flex flex-col justify-center">

          <h2 className="text-2xl font-bold text-center text-green-800 mb-6">
            Connexion
          </h2>

          <form className="flex flex-col gap-4" onSubmit={handleLogin}>
            <input
              type="email"
              placeholder="Email"
              className="border p-3 rounded-lg"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <input
              type="password"
              placeholder="Mot de passe"
              className="border p-3 rounded-lg"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {apiError && (
              <p className="text-red-600 text-sm text-center">{apiError}</p>
            )}

            <button className="bg-green-700 text-white py-3 rounded-lg hover:bg-green-800">
              Se connecter
            </button>
          </form>

          <p className="text-center mt-4">
            <Link to="/forgot-password" className="text-green-700 text-sm hover:underline">
              Mot de passe oublié ?
            </Link>
          </p>

          <p className="text-center mt-6 text-sm">
            Pas encore de compte ?
            <Link to="/register" className="text-green-700 ml-1">
              S'inscrire
            </Link>
          </p>

        </div>
      </div>
    </div>
  );
}
