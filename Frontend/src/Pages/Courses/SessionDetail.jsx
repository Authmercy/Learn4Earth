import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function SessionDetail() {
  const { session_id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const location = useLocation();
  const session = location.state;

  const [score, setScore] = useState(0);
  const [duration, setDuration] = useState(10);
  const [completed, setCompleted] = useState(false);

  const completeSession = async () => {
    try {
      const response = await fetch(
        `http://206.189.56.166:8000/api/learning/sessions/${session_id}/complete`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            score,
            duration_minutes: duration,
          }),
        }
      );

      if (response.status === 200) {
        setCompleted(true);
        setTimeout(() => navigate("/courses"), 1500);
      } else {
        alert("Erreur lors de la complétion.");
      }
    } catch (error) {
      console.error(error);
      alert("Erreur réseau.");
    }
  };

  // Protection si accès direct sans state
  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-700">
        Session introuvable
      </div>
    );
  }

  const isDefaultContent =
    typeof session.content === "string" &&
    session.content.startsWith("[Contenu par defaut]");

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 px-6 py-10 font-poppins">
      <div className="max-w-5xl mx-auto bg-white shadow-xl rounded-2xl p-8 md:p-10 space-y-8">

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b pb-4">
          <div>
            <p className="text-sm uppercase tracking-wide text-green-700 font-semibold">
              Session {session.session_number}
            </p>
            <h1 className="text-3xl font-bold text-gray-900 mt-1">
              {session.title}
            </h1>
          </div>

          <div className="flex flex-col items-start md:items-end gap-2">
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold ${
                session.status === "en_cours"
                  ? "bg-yellow-100 text-yellow-800"
                  : session.status === "terminee"
                  ? "bg-green-100 text-green-800"
                  : "bg-gray-100 text-gray-700"
              }`}
            >
              Statut : {session.status}
            </span>

            {isDefaultContent && (
              <span className="text-xs text-orange-700 bg-orange-50 px-3 py-1 rounded-full">
                Contenu par défaut (IA indisponible)
              </span>
            )}
          </div>
        </div>

        {/* Contenu */}
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-3 underline underline-offset-4 decoration-green-500">
            Contenu de la session
          </h2>

          <div className="border rounded-xl bg-gray-50/70 max-h-[420px] overflow-y-auto p-5 md:p-6">
            <article className="prose prose-sm md:prose-base max-w-none prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-strong:text-green-800 prose-li:marker:text-green-600">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {session.content}
              </ReactMarkdown>
            </article>
          </div>
        </div>

        {/* Score & Durée */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="text-gray-700 text-sm font-semibold block mb-2">
              Score obtenu
            </label>
            <input
              type="number"
              className="border border-gray-300 focus:border-green-600 focus:ring-2 focus:ring-green-100 p-3 rounded-lg w-full"
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
            />
          </div>

          <div>
            <label className="text-gray-700 text-sm font-semibold block mb-2">
              Durée (minutes)
            </label>
            <input
              type="number"
              className="border border-gray-300 focus:border-green-600 focus:ring-2 focus:ring-green-100 p-3 rounded-lg w-full"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
            />
          </div>
        </div>

        {/* Bouton */}
        <div>
          <button
            onClick={completeSession}
            className="bg-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-800 transition shadow-sm"
          >
            Terminer la session
          </button>

          {completed && (
            <p className="text-green-700 font-semibold mt-4">
              Session complétée ! Redirection...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
