import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    phone_number: "",
    date_of_birth: "",
    level: "debutant",
    objectives: "",
    preferences: "",
    gdpr_consent: false,
    gdpr_marketing_consent: false,
    gdpr_data_retention_consent: false,
  });

  const [apiErrors, setApiErrors] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiErrors([]);

    try {
      const response = await fetch("http://206.189.56.166:8000/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (response.status === 201) {
        navigate("/verify-otp", {
          state: {
            email: form.email,
            phone_number: form.phone_number,
          },
        });
        return;
      }

      if (response.status === 422) {
        const data = await response.json();
        setApiErrors(data.detail);
        return;
      }

      setApiErrors([{ msg: "Erreur inconnue" }]);
    } catch {
      setApiErrors([{ msg: "Impossible de contacter le serveur" }]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 flex items-center justify-center px-6">

      <div className="w-full max-w-6xl bg-white shadow-2xl rounded-2xl overflow-hidden grid grid-cols-1 md:grid-cols-2">

        {/* IMAGE */}
        <div className="hidden md:block">
          <img
            src="/images/register-side.jpg"
            alt="AI Illustration"
            className="w-full h-full object-cover"
          />
        </div>

        {/* FORM */}
        <div className="p-10 overflow-y-auto max-h-screen">

          <h2 className="text-2xl font-bold text-center text-green-800 mb-6">
            Inscription
          </h2>

          <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={handleSubmit}>

            {/* EMAIL */}
            <div className="col-span-2">
              <input
                type="email"
                name="email"
                placeholder="Email"
                className="border p-3 rounded-lg w-full"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>

            {/* PASSWORD */}
            <div className="col-span-2">
              <input
                type="password"
                name="password"
                placeholder="Mot de passe"
                className="border p-3 rounded-lg w-full"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>

            {/* FULL NAME */}
            <div className="col-span-2">
              <input
                type="text"
                name="full_name"
                placeholder="Nom complet"
                className="border p-3 rounded-lg w-full"
                value={form.full_name}
                onChange={handleChange}
                required
              />
            </div>

            {/* PHONE */}
            <div className="col-span-2">
              <input
                type="text"
                name="phone_number"
                placeholder="Téléphone (+33...)"
                className="border p-3 rounded-lg w-full"
                value={form.phone_number}
                onChange={handleChange}
                required
              />
            </div>

            {/* DATE OF BIRTH */}
            <div className="col-span-2">
              <input
                type="date"
                name="date_of_birth"
                className="border p-3 rounded-lg w-full"
                value={form.date_of_birth}
                onChange={handleChange}
                required
              />
            </div>

            {/* OBJECTIVES */}
            <div className="col-span-2">
              <textarea
                name="objectives"
                placeholder="Vos objectifs d'apprentissage"
                className="border p-3 rounded-lg w-full h-20"
                value={form.objectives}
                onChange={handleChange}
              ></textarea>
            </div>

            {/* PREFERENCES */}
            <div className="col-span-2">
              <textarea
                name="preferences"
                placeholder="Vos préférences (ex: vidéos, exercices...)"
                className="border p-3 rounded-lg w-full h-20"
                value={form.preferences}
                onChange={handleChange}
              ></textarea>
            </div>

            {/* GDPR */}
            <div className="col-span-2 mt-2 space-y-2">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  name="gdpr_consent"
                  checked={form.gdpr_consent}
                  onChange={handleChange}
                />
                <span>J’accepte la collecte et le traitement de mes données (RGPD)</span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  name="gdpr_marketing_consent"
                  checked={form.gdpr_marketing_consent}
                  onChange={handleChange}
                />
                <span>J’accepte de recevoir des communications marketing</span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  name="gdpr_data_retention_consent"
                  checked={form.gdpr_data_retention_consent}
                  onChange={handleChange}
                />
                <span>J’accepte la conservation de mes données</span>
              </label>
            </div>

            {/* API ERRORS */}
            {apiErrors.length > 0 && (
              <div className="col-span-2 bg-red-50 border border-red-300 p-3 rounded-lg">
                {apiErrors.map((err, i) => (
                  <p key={i} className="text-red-700 text-sm">
                    {err.msg}
                  </p>
                ))}
              </div>
            )}

            <button className="col-span-2 bg-green-700 text-white py-3 rounded-lg hover:bg-green-800 mt-4">
              Créer mon compte
            </button>
          </form>

          <p className="text-center mt-6 text-sm">
            Déjà un compte ?
            <Link to="/login" className="text-green-700 ml-1">
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
