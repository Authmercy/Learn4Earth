import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function MesSessions() {
  const token = localStorage.getItem("access_token");
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(
          "http://206.189.56.166:8000/api/learning/sessions",
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const data = await res.json();

        if (res.status === 200 && Array.isArray(data)) {
          setSessions(data);
        }
      } catch (err) {
        console.error("Erreur sessions", err);
      }

      setLoading(false);
    };

    load();
  }, [token]);

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Chargement des sessions...
      </div>
    );

  if (sessions.length === 0)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Aucune session trouvée.
      </div>
    );

  const formatStatus = (status) => {
    if (status === "terminee") return "Terminée";
    if (status === "en_cours") return "En cours";
    if (status === "non_commencee") return "Non commencée";
    return status;
  };

  const filterSessions = (list) => {
    if (filter === "all") return list;
    return list.filter((s) => s.status === filter);
  };

  // groupement par learning_path_id (plus fiable)
  const grouped = sessions.reduce((acc, s) => {
    const key = s.learning_path_id;
    if (!acc[key]) acc[key] = [];
    acc[key].push(s);
    return acc;
  }, {});

  return (
    <div className="min-h-screen px-6 py-10 bg-gradient-to-br from-green-50 to-blue-100">

      <div className="flex justify-between items-center mb-10">
        <h1 className="text-3xl font-bold text-green-800">Mes sessions</h1>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="all">Toutes</option>
          <option value="en_cours">En cours</option>
          <option value="terminee">Terminées</option>
        </select>
      </div>

      <div className="space-y-10">
        {Object.entries(grouped).map(([courseId, courseSessions]) => {
          const filtered = filterSessions(courseSessions);

          if (filtered.length === 0) return null;

          const sorted = filtered.sort(
            (a, b) => a.session_number - b.session_number
          );

          return (
            <div
              key={courseId}
              className="bg-white rounded-2xl shadow-xl overflow-hidden"
            >
              {/* header cours */}
              <div className="bg-green-700 text-white px-8 py-4 flex justify-between">
                <h2 className="text-xl font-bold">
                  Parcours {courseId.slice(0, 8)}
                </h2>
                <span className="bg-green-500 px-3 py-1 rounded-full text-sm">
                  {sorted.length} sessions
                </span>
              </div>

              {/* sessions */}
              <div className="p-6 space-y-4">
                {sorted.map((s) => (
                  <Link
                    key={s.id}
                    to={`/session/${s.id}`}
                    state={s}
                    className="block bg-gray-50 hover:bg-gray-100 border rounded-xl p-5 transition"
                  >
                    <div className="flex justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">
                          Session {s.session_number}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {new Date(s.created_at).toLocaleString()}
                        </p>
                      </div>

                      <span className="px-3 py-1 text-xs rounded-full bg-green-100 text-green-700 font-semibold">
                        {formatStatus(s.status)}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
