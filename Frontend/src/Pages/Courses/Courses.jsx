import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const [page, setPage] = useState(1);
  const itemsPerPage = 8;

  const token = localStorage.getItem("access_token");

  const colors = [
    "from-green-200 to-green-100",
    "from-blue-200 to-blue-100",
    "from-purple-200 to-purple-100",
    "from-yellow-200 to-yellow-100",
    "from-pink-200 to-pink-100",
    "from-teal-200 to-teal-100",
  ];

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await fetch("http://206.189.56.166:8000/api/learning/paths", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.status === 200) {
          const data = await response.json();
          setCourses(data);
        } else {
          setApiError("Impossible de récupérer vos cours");
        }
      } catch {
        setApiError("Erreur serveur");
      }
      setLoading(false);
    };

    fetchCourses();
  }, [token]);

  /* ===============================
     FILTRAGE + RECHERCHE
  =============================== */

  const filteredCourses = courses.filter((c) => {
    const matchSearch =
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.subject.toLowerCase().includes(search.toLowerCase());

    let matchStatus = true;

    if (statusFilter === "termine") {
      matchStatus = c.status === "termine";
    } else if (statusFilter === "en_cours") {
      matchStatus = c.status === "en_cours";
    } else if (statusFilter === "non_commence") {
      matchStatus = c.completed_sessions === 0;
    }

    return matchSearch && matchStatus;
  });

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
  const totalPages = Math.ceil(filteredCourses.length / itemsPerPage);
  const startIndex = (page - 1) * itemsPerPage;
  const visibleCourses = filteredCourses.slice(
    startIndex,
    startIndex + itemsPerPage
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 px-6 md:px-12 py-10">

      {/* HEADER */}
      <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-6 mb-10">
        <h1 className="text-4xl font-bold text-green-800">Mes cours</h1>

        <div className="flex flex-col md:flex-row gap-4">

          {/* SEARCH */}
          <input
            placeholder="Rechercher un cours..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="px-4 py-3 rounded-xl border border-gray-300 shadow-sm focus:ring-2 focus:ring-green-400 outline-none"
          />

          {/* FILTER */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="px-4 py-3 rounded-xl border border-gray-300 shadow-sm"
          >
            <option value="all">Tous</option>
            <option value="non_commence">Non commencé</option>
            <option value="en_cours">En cours</option>
            <option value="termine">Terminé</option>
          </select>

          <Link to="/generate-course">
            <button className="bg-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-800 shadow">
              Générer un cours
            </button>
          </Link>
        </div>
      </div>

      {loading && <p>Chargement...</p>}
      {apiError && <p className="text-red-600">{apiError}</p>}

      {/* GRID */}
      {filteredCourses.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center w-full">
          <img
            src="/images/empty.png"
            alt="Aucun cours"
            className="w-40 mb-6 opacity-80"
          />

          <h2 className="text-2xl font-semibold text-gray-700 mb-2">
            Aucun cours pour le moment
          </h2>

          <p className="text-gray-500 mb-6 max-w-md">
            Commencez votre apprentissage en générant votre premier cours personnalisé.
          </p>

          <Link to="/generate-course">
            <button className="bg-green-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-800 shadow">
              Générer mon premier cours
            </button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {visibleCourses.map((course, i) => (
            <Link
              key={course.id}
              to={`/course/${course.id}`}
              className={`rounded-2xl p-6 shadow-lg bg-gradient-to-br ${
                colors[i % colors.length]
              } hover:scale-[1.02] transition`}
            >
              <h2 className="text-lg font-bold text-gray-800">{course.title}</h2>
              <p className="text-sm text-gray-600 mt-1">{course.subject}</p>

              <p className="text-sm font-semibold mt-2">
                Difficulté : {course.difficulty}
              </p>

              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-green-600 h-3 rounded-full"
                    style={{
                      width: `${Math.min(course.progress_percent, 100)}%`,
                    }}
                  ></div>
                </div>

                <p className="text-sm text-gray-700 mt-1">
                  Progression : {Math.min(course.progress_percent, 100)}%
                </p>
              </div>

              <p className="text-sm mt-3">
                Sessions : {course.completed_sessions}/{course.total_sessions}
              </p>

              <span
                className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${statusStyle(
                  course.status
                )}`}
              >
                {formatStatus(course.status, course.completed_sessions)}
              </span>
            </Link>
          ))}
        </div>
      )}


      {/* PAGINATION */}
      {filteredCourses.length > itemsPerPage && (
        <div className="flex justify-center gap-3 mt-10 flex-wrap">
          {[...Array(totalPages)].map((_, i) => (
            <button
              key={i}
              onClick={() => setPage(i + 1)}
              className={`px-4 py-2 rounded-lg ${
                page === i + 1
                  ? "bg-green-700 text-white"
                  : "bg-white border hover:bg-gray-100"
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
