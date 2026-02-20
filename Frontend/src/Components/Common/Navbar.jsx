import { useState, useRef, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  const isLoggedIn = !!localStorage.getItem("access_token");
  const user = localStorage.getItem("user")
    ? JSON.parse(localStorage.getItem("user"))
    : null;

  const menuRef = useRef(null);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/");
  };

  // Fermer le menu utilisateur si clic extérieur
  useEffect(() => {
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const publicLinks = [
    { href: "/", label: "Accueil" },
    { href: "/features", label: "Fonctionnalités" },
    // { href: "/impact", label: "Impact" },
    { href: "/pricing", label: "Tarifs" },
    { href: "/contact", label: "Contact" },
  ];

  const authLinks = [
    { href: "/courses", label: "Mes cours" },
    { href: "/sessions", label: "Mes sessions" },
    // { href: "/impact-carbone", label: "Impact carbone" },
    { href: "/plans", label: "Mon abonnement" },
    { href: "/dashboard", label: "Tableau de Bord Carbone" },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-white/40 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">

        {/* LOGO */}
        <div className="flex flex-col items-start md:items-center">
          <Link to="/" className="flex flex-col items-start md:items-center">
            <img
              src="/images/logo.png"
              alt="EcoLearnAI logo"
              className="h-20 md:h-24 drop-shadow-xl"
            />
            <span className="text-xs md:text-sm text-green-700 tracking-wide">
              Plateforme d'apprentissage écologique
            </span>
          </Link>
        </div>


        {/* DESKTOP MENU */}
        <ul className="hidden md:flex gap-8 text-gray-700 font-medium">
          {(isLoggedIn ? authLinks : publicLinks).map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={`transition ${
                isActive(link.href)
                  ? "text-green-700 font-semibold"
                  : "hover:text-green-700"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </ul>

        {/* USER MENU (DESKTOP) */}
        <div className="hidden md:flex items-center gap-4">
          {!isLoggedIn ? (
            <>
              <Link to="/login">
                <button className="px-4 py-2 border border-green-700 text-green-700 rounded-md hover:bg-green-700 hover:text-white transition">
                  Se connecter
                </button>
              </Link>

              {/* <Link to="/register">
                <button className="px-4 py-2 bg-green-700 text-white rounded-md hover:bg-green-800 transition">
                  S'inscrire
                </button>
              </Link> */}
            </>
          ) : (
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow hover:shadow-md transition border border-gray-200"
              >
                <span className="font-semibold text-gray-800">
                  {user?.full_name || "Mon compte"}
                </span>
                <svg
                  className={`w-4 h-4 transition-transform ${
                    menuOpen ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {menuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden animate-fadeIn">
                  <Link
                    to="/profile"
                    className="flex items-center gap-2 px-4 py-3 hover:bg-gray-50 transition text-gray-700"
                    onClick={() => setMenuOpen(false)}
                  >
                    👤 Profil
                  </Link>

                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 w-full text-left px-4 py-3 hover:bg-red-50 text-red-600 transition"
                  >
                    🚪 Déconnexion
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* MOBILE BURGER */}
        <button
          className="md:hidden text-green-700 text-3xl"
          onClick={() => setOpen(!open)}
        >
          ☰
        </button>
      </div>

      {/* MOBILE MENU */}
      {open && (
        <div className="md:hidden bg-white/90 backdrop-blur-xl shadow-lg p-4 animate-fadeIn">
          <ul className="flex flex-col gap-4 text-gray-700 font-medium">
            {(isLoggedIn ? authLinks : publicLinks).map((link) => (
              <Link
                key={link.href}
                to={link.href}
                onClick={() => setOpen(false)}
                className="hover:text-green-700"
              >
                {link.label}
              </Link>
            ))}
          </ul>

          {/* MOBILE USER MENU */}
          {isLoggedIn && (
            <div className="mt-6 border-t pt-4">
              <Link
                to="/profile"
                onClick={() => setOpen(false)}
                className="block px-4 py-2 hover:bg-gray-100 rounded-md"
              >
                👤 Profil
              </Link>

              <button
                onClick={() => {
                  handleLogout();
                  setOpen(false);
                }}
                className="w-full text-left px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
              >
                🚪 Déconnexion
              </button>
            </div>
          )}

          {!isLoggedIn && (
            <div className="flex flex-col gap-3 mt-4">
              <Link
                to="/login"
                className="px-4 py-2 border border-green-700 text-green-700 rounded-md hover:bg-green-700 hover:text-white transition text-center"
                onClick={() => setOpen(false)}
              >
                Se connecter
              </Link>

              {/* <Link
                to="/register"
                className="px-4 py-2 bg-green-700 text-white rounded-md hover:bg-green-800 transition text-center"
                onClick={() => setOpen(false)}
              >
                S'inscrire
              </Link> */}
            </div>
          )}
        </div>
      )}
    </nav>
  );
}
