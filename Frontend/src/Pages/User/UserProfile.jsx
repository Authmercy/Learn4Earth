import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function UserProfile() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const [user, setUser] = useState(null);
  const [progression, setProgression] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [payments, setPayments] = useState([]);

  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});

  // Redirect if not logged in
  useEffect(() => {
    if (!token) navigate("/login");
  }, [token, navigate]);

  // Fetch profile
  useEffect(() => {
    if (!token) return;

    const load = async () => {
      const headers = { Authorization: `Bearer ${token}` };

      const u = await fetch("http://206.189.56.166:8000/api/users/me", { headers });
      const p = await fetch("http://206.189.56.166:8000/api/users/me/progression", { headers });
      const s = await fetch("http://206.189.56.166:8000/api/subscriptions/my", { headers });
      const pay = await fetch("http://206.189.56.166:8000/api/payments/my", { headers });

      const userData = await u.json();
      setUser(userData);
      setForm(userData);

      setProgression(await p.json());
      setSubscription(await s.json());
      setPayments(await pay.json());
    };

    load();
  }, [token]);

  if (!user) return null;

  // Save profile
  const saveProfile = async () => {
    try {
      const res = await fetch("http://206.189.56.166:8000/api/users/me", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      });

      if (res.ok) {
        const updated = await res.json();
        setUser(updated);
        setEditing(false);
      } else {
        alert("Erreur lors de la mise à jour.");
      }
    } catch {
      alert("Erreur réseau.");
    }
  };

  return (
  <div className="max-w-6xl mx-auto mt-10 px-6">

    {/* HEADER */}
    <div className="bg-gradient-to-r from-green-600 to-green-500 text-white rounded-2xl p-8 shadow-lg mb-10 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <div className="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center text-3xl font-bold">
          {user.full_name?.[0]}
        </div>

        <div>
          <h1 className="text-3xl font-bold">{user.full_name}</h1>
          <p className="opacity-90">{user.email}</p>
        </div>
      </div>

      {!editing ? (
        <button
          onClick={() => setEditing(true)}
          className="px-5 py-2 bg-white text-green-700 rounded-lg font-semibold"
        >
          Modifier
        </button>
      ) : (
        <div className="flex gap-3">
          <button
            onClick={saveProfile}
            className="px-5 py-2 bg-white text-green-700 rounded-lg font-semibold"
          >
            Enregistrer
          </button>
          <button
            onClick={() => {
              setEditing(false);
              setForm(user);
            }}
            className="px-5 py-2 bg-white/30 rounded-lg"
          >
            Annuler
          </button>
        </div>
      )}
    </div>

    {/* GRID PRINCIPAL */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

      <Card title="Informations personnelles">
        <Editable label="Nom complet" field="full_name" editing={editing} form={form} setForm={setForm}/>
        <Editable label="Téléphone" field="phone_number" editing={editing} form={form} setForm={setForm}/>
        <Editable label="Ville" field="address_city" editing={editing} form={form} setForm={setForm}/>
        <Editable label="Date de naissance" field="date_of_birth" editing={editing} form={form} setForm={setForm}/>
      </Card>

      <Card title="Apprentissage">
        {progression && (
          <>
            <Progress label="XP total" value={progression.total_xp} max={1000}/>
            <Progress label="Minutes apprises" value={progression.total_learning_minutes} max={1000}/>
            <Info label="Streak actuel" value={progression.current_streak}/>
            <Info label="Plus long streak" value={progression.longest_streak}/>
          </>
        )}
      </Card>

      <Card title="Sécurité">
        <Info label="Compte vérifié" value={user.is_verified ? "Oui" : "Non"} />
        <Info label="Dernière connexion" value={user.last_login_at} />

        <Link to="/change-password">
          <button className="mt-4 px-4 py-2 bg-green-700 text-white rounded-lg">
            Changer mot de passe
          </button>
        </Link>
      </Card>

      <Card title="Abonnement">
        {subscription ? (
          <>
            <Info label="Plan" value={subscription.plan_name}/>
            <Info label="Statut" value={subscription.status}/>
            <Info label="Fin" value={subscription.end_date}/>
          </>
        ) : (
          <p className="text-gray-500">Aucun abonnement</p>
        )}
      </Card>

    </div>
  </div>
);

}

function Section({ title, children }) {
  return (
    <div className="mb-10">
      <h2 className="text-2xl font-semibold text-green-600 mb-4">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {children}
      </div>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div>
      <p className="text-gray-500 text-sm">{label}</p>
      <p className="font-semibold">{value}</p>
    </div>
  );
}

function Editable({ label, field, editing, form, setForm }) {
  return (
    <div>
      <p className="text-gray-500 text-sm">{label}</p>

      {!editing ? (
        <p className="font-semibold">{form[field] || "—"}</p>
      ) : (
        <input
          type="text"
          value={form[field] || ""}
          onChange={(e) => setForm({ ...form, [field]: e.target.value })}
          className="w-full px-3 py-2 border rounded-md"
        />
      )}
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="bg-white rounded-2xl shadow-md p-6">
      <h2 className="text-xl font-semibold text-green-700 mb-4">{title}</h2>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

function Progress({ label, value, max }) {
  const percent = Math.min((value / max) * 100, 100);
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div className="bg-green-600 h-3 rounded-full" style={{ width: `${percent}%` }}></div>
      </div>
    </div>
  );
}

