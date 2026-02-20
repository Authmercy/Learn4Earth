import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function GenerateCourse() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [form, setForm] = useState({
    title: "",
    subject: "",
    description: "",
    difficulty: "debutant",
    total_sessions: 5,
  });

  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [subscriptionPopup, setSubscriptionPopup] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError("");
    setLoading(true);

    try {
      // 1️⃣ Création du parcours
      const pathRes = await fetch(
        "http://206.189.56.166:8000/api/learning/paths",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(form),
        }
      );

      // 🔐 Token expiré
      if (pathRes.status === 401) {
        localStorage.clear();
        navigate("/login");
        return;
      }

      // 🔥 Abonnement requis
      if (pathRes.status === 403) {
        setSubscriptionPopup(true);
        return;
      }

      if (pathRes.status !== 201) {
        setApiError("Impossible de générer le cours");
        return;
      }

      const path = await pathRes.json();

      // 2️⃣ Génération de la première session
      const sessionRes = await fetch(
        "http://206.189.56.166:8000/api/learning/sessions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            learning_path_id: path.id,
            title: `Session 1 - ${path.title}`,
            session_number: 1,
          }),
        }
      );

      // 🔐 Token expiré
      if (sessionRes.status === 401) {
        localStorage.clear();
        navigate("/login");
        return;
      }

      // 🔥 Abonnement requis (cas où l’API bloque ici)
      if (sessionRes.status === 403) {
        setSubscriptionPopup(true);
        return;
      }

      if (sessionRes.status !== 201) {
        setApiError("Cours créé mais session impossible.");
        return;
      }

      const session = await sessionRes.json();

      // 3️⃣ Redirection vers la session générée
      navigate(`/session/${session.id}`, { state: session });

    } catch {
      setApiError("Erreur serveur");
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-green-100 px-6 py-12">

    {/* Popup abonnement */}
    {subscriptionPopup && (
      <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center max-w-sm">
          <h2 className="text-xl font-bold text-red-600 mb-3">
            Abonnement requis
          </h2>
          <p className="text-gray-700 mb-6">
            Vous devez souscrire à un abonnement actif pour générer un cours.
          </p>
          <button
            onClick={() => navigate("/plans")}
            className="bg-green-700 text-white px-6 py-3 rounded-lg hover:bg-green-800 transition"
          >
            Voir les abonnements
          </button>
        </div>
      </div>
    )}

    {/* HEADER */}
    <div className="max-w-4xl mx-auto text-center mb-10">
      <h1 className="text-4xl font-bold text-green-800">
        Générer un nouveau parcours
      </h1>
      <p className="text-gray-600 mt-2">
        L’IA construit automatiquement votre parcours pédagogique personnalisé
      </p>
    </div>

    {/* FORM CARD */}
    <div className="max-w-4xl mx-auto bg-white shadow-xl rounded-3xl p-10 border border-gray-100">

      <form className="grid grid-cols-1 md:grid-cols-2 gap-8" onSubmit={handleSubmit}>

        {/* TITRE */}
        <div className="md:col-span-2 flex flex-col gap-2">
          <label className="text-sm text-gray-600 font-medium">
            Titre du cours
          </label>
          <input
            name="title"
            value={form.title}
            onChange={handleChange}
            required
            className="px-5 py-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-green-400 focus:border-green-500 outline-none transition shadow-sm"
            placeholder="Introduction à l’écologie"
          />
        </div>

        {/* SUBJECT */}
        <div className="md:col-span-2 flex flex-col gap-2">
          <label className="text-sm text-gray-600 font-medium">
            Sujet
          </label>
          <input
            name="subject"
            value={form.subject}
            onChange={handleChange}
            required
            className="px-5 py-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-green-400 focus:border-green-500 outline-none transition shadow-sm"
            placeholder="Énergies renouvelables"
          />
        </div>

        {/* DESCRIPTION */}
        <div className="md:col-span-2 flex flex-col gap-2">
          <label className="text-sm text-gray-600 font-medium">
            Description
          </label>
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            required
            className="px-5 py-4 h-32 rounded-xl border border-gray-300 focus:ring-2 focus:ring-green-400 focus:border-green-500 outline-none transition shadow-sm resize-none"
            placeholder="Objectifs pédagogiques du parcours..."
          />
        </div>

        {/* DIFFICULTÉ */}
        <div className="flex flex-col gap-2">
          <label className="text-sm text-gray-600 font-medium">
            Difficulté
          </label>
          <select
            name="difficulty"
            value={form.difficulty}
            onChange={handleChange}
            className="px-5 py-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-green-400 focus:border-green-500 outline-none transition shadow-sm"
          >
            <option value="debutant">Débutant</option>
            <option value="intermediaire">Intermédiaire</option>
            <option value="avance">Avancé</option>
          </select>
        </div>

        {/* SESSIONS */}
        <div className="flex flex-col gap-2">
          <label className="text-sm text-gray-600 font-medium">
            Nombre de sessions
          </label>
          <input
            type="number"
            name="total_sessions"
            min="1"
            max="50"
            value={form.total_sessions}
            onChange={handleChange}
            className="px-5 py-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-green-400 focus:border-green-500 outline-none transition shadow-sm"
          />
        </div>

        {/* ERROR */}
        {apiError && (
          <p className="text-red-600 md:col-span-2 text-center">{apiError}</p>
        )}

        {/* BUTTON */}
        <button
          className="md:col-span-2 mt-6 bg-gradient-to-r from-green-600 to-green-700 text-white py-4 rounded-xl font-semibold text-lg shadow-lg hover:scale-[1.01] transition disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Génération en cours..." : "Générer le cours avec l’IA"}
        </button>

      </form>
    </div>
  </div>
);

}
