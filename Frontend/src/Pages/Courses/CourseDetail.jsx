import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function CourseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const formatStatus = (status, completed_sessions) => {
    if (completed_sessions === 0) return "Non commencé";
    if (status === "termine") return "Terminé";
    if (status === "en_cours") return "En cours";
    return status;
  };

  const statusStyle = (status) => {
    if (status === "termine")
      return "bg-green-100 text-green-700";
    if (status === "en_cours")
      return "bg-blue-100 text-blue-700";
    return "bg-gray-100 text-gray-700";
  };

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const response = await fetch(
          `http://206.189.56.166:8000/api/learning/paths/${id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (response.status === 200) {
          const data = await response.json();
          setCourse(data);
        } else {
          setApiError("Impossible de récupérer ce cours");
        }
      } catch {
        setApiError("Erreur serveur");
      }

      setLoading(false);
    };

    fetchCourse();
  }, [id, token]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-green-50 to-blue-100">
        <div className="w-16 h-16 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-6 text-green-800 font-semibold text-lg animate-pulse">
          Chargement en cours...
        </p>
      </div>
    );
  }

  if (apiError) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600">
        {apiError}
      </div>
    );
  }

  if (!course) return null;

  const hasStarted = course.completed_sessions > 0;
  const isFinished =
    course.status === "termine" ||
    course.completed_sessions >= course.total_sessions;

  const progress = Math.min(course.progress_percent, 100);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 px-6 md:px-12 py-10 font-poppins">

      <div className="max-w-5xl mx-auto">

        {/* BACK BUTTON */}
        <button
          onClick={() => navigate("/courses")}
          className="mb-6 text-green-700 font-semibold hover:underline flex items-center gap-2"
        >
          ← Retour aux cours
        </button>

        <div className="bg-white shadow-xl rounded-3xl p-10">

          {/* HEADER */}
          <h1 className="text-3xl md:text-4xl font-bold text-green-800 mb-3">
            {course.title}
          </h1>

          <p className="text-gray-600 mb-6">
            {course.description}
          </p>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <p className="text-gray-700">
              <span className="font-semibold">Sujet :</span> {course.subject}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Difficulté :</span> {course.difficulty}
            </p>
            <p className="text-gray-700">
              <span
                className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${statusStyle(course.status)}`}
              >
  {formatStatus(course.status, course.completed_sessions)}
</span>
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Sessions :</span>{" "}
              {course.completed_sessions}/{course.total_sessions}
            </p>
          </div>

          {/* PROGRESS */}
          <div className="mb-10">
            <p className="text-gray-700 font-semibold mb-2">
              Progression : {progress}%
            </p>

            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className="bg-green-600 h-4 rounded-full transition-all"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* ACTION BUTTON */}
          <div className="flex flex-wrap gap-4">

            {isFinished ? (
              <button
                onClick={() => navigate("/sessions")}
                className="bg-green-700 text-white px-8 py-3 rounded-xl font-semibold hover:bg-green-800 transition shadow-lg"
              >
                Voir les sessions
              </button>
            ) : (
              <button
                onClick={() => navigate(`/course/${id}/start`)}
                disabled={actionLoading}
                className="bg-green-700 text-white px-8 py-3 rounded-xl font-semibold hover:bg-green-800 transition shadow-lg disabled:opacity-50"
              >
                {actionLoading
                  ? "Chargement..."
                  : hasStarted
                  ? "Continuer le cours"
                  : "Commencer le cours"}
              </button>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}
