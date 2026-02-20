import { useState } from "react";

export default function Admin() {

  /* ================= USERS (VERSION ORIGINALE) ================= */
  const [users, setUsers] = useState([
    {
      id: 1,
      name: "Sophie Martin",
      email: "sophie@ecolearn.ai",
      role: "User",
      plan: "Mensuel",
      status: "Active",
    },
    {
      id: 2,
      name: "Lucas Bernard",
      email: "lucas@ecolearn.ai",
      role: "Admin",
      plan: "Annuel",
      status: "Active",
    },
  ]);

  const toggleStatus = (id) => {
    setUsers(
      users.map((u) =>
        u.id === id
          ? {
              ...u,
              status: u.status === "Active" ? "Suspended" : "Active",
            }
          : u
      )
    );
  };

  const deleteUser = (id) => {
    setUsers(users.filter((u) => u.id !== id));
  };

  /* ================= PLANS ================= */

  const [plans, setPlans] = useState({
    monthly: {
      price: 9.99,
      features: ["Cours illimités", "Support premium"],
    },
    yearly: {
      price: 89.99,
      features: ["Cours illimités", "Support premium"],
    },
  });

  const updatePlanPrice = (type, value) => {
    setPlans({
      ...plans,
      [type]: {
        ...plans[type],
        price: Number(value),
      },
    });
  };

  const addFeature = (type) => {
    setPlans({
      ...plans,
      [type]: {
        ...plans[type],
        features: [...plans[type].features, "Nouvelle fonctionnalité"],
      },
    });
  };

  const removeFeature = (type, index) => {
    const updated = plans[type].features.filter((_, i) => i !== index);

    setPlans({
      ...plans,
      [type]: {
        ...plans[type],
        features: updated,
      },
    });
  };

  const updateFeature = (type, index, value) => {
    const updated = [...plans[type].features];
    updated[index] = value;

    setPlans({
      ...plans,
      [type]: {
        ...plans[type],
        features: updated,
      },
    });
  };

  const handleSave = () => {
    alert("Modifications enregistrées !");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-10">
      <h1 className="text-3xl font-bold text-green-800 mb-8">
        🌿 Admin Panel
      </h1>

      {/* ================= USERS ================= */}
      <div className="bg-white rounded-2xl shadow-md p-6 mb-12">
        <h2 className="text-xl font-semibold text-green-700 mb-4">
          Gestion des utilisateurs
        </h2>

        <table className="w-full">
          <thead>
            <tr className="bg-green-50 text-left">
              <th className="p-3">Nom</th>
              <th>Email</th>
              <th>Rôle</th>
              <th>Plan</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b">
                <td className="p-3">{user.name}</td>
                <td>{user.email}</td>
                <td>
                  <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700">
                    {user.role}
                  </span>
                </td>
                <td>
                  <span className="px-2 py-1 text-xs rounded-full bg-gray-100">
                    {user.plan}
                  </span>
                </td>
                <td>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      user.status === "Active"
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {user.status}
                  </span>
                </td>
                <td className="space-x-2">
                  <button
                    onClick={() => toggleStatus(user.id)}
                    className="px-3 py-1 text-sm border border-green-600 text-green-700 rounded-lg hover:bg-green-50"
                  >
                    Suspendre
                  </button>
                  <button
                    onClick={() => deleteUser(user.id)}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ================= ABONNEMENTS ================= */}
      <div className="bg-white rounded-2xl shadow-md p-8">
        <h2 className="text-xl font-semibold text-green-700 mb-8">
          Gestion des abonnements
        </h2>

        <div className="grid md:grid-cols-2 gap-10">

          {/* Mensuel */}
          <div className="bg-gray-50 rounded-2xl p-8 shadow-sm flex flex-col">
            <h3 className="text-xl font-bold mb-4">Mensuel</h3>

            <div className="relative mb-6">
              <input
                type="number"
                value={plans.monthly.price}
                onChange={(e) =>
                  updatePlanPrice("monthly", e.target.value)
                }
                className="w-full p-2 pr-10 border rounded"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                €
              </span>
            </div>

            {plans.monthly.features.map((feature, index) => (
              <div key={index} className="flex mb-3">
                <input
                  value={feature}
                  onChange={(e) =>
                    updateFeature("monthly", index, e.target.value)
                  }
                  className="flex-1 p-2 border rounded"
                />
                <button
                  onClick={() =>
                    removeFeature("monthly", index)
                  }
                  className="ml-2 text-red-600"
                >
                  Supprimer
                </button>
              </div>
            ))}

            <button
              onClick={() => addFeature("monthly")}
              className="text-green-700 text-sm underline mb-6"
            >
              + Ajouter une fonctionnalité
            </button>

            <button
              onClick={handleSave}
              className="mt-auto bg-green-700 text-white py-2 rounded-lg"
            >
              Valider les modifications
            </button>
          </div>

          {/* Annuel */}
          <div className="bg-white border-2 border-green-600 rounded-2xl p-8 flex flex-col">
            <h3 className="text-xl font-bold mb-4">Annuel</h3>

            <div className="relative mb-6">
              <input
                type="number"
                value={plans.yearly.price}
                onChange={(e) =>
                  updatePlanPrice("yearly", e.target.value)
                }
                className="w-full p-2 pr-10 border rounded"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">
                €
              </span>
            </div>

            {plans.yearly.features.map((feature, index) => (
              <div key={index} className="flex mb-3">
                <input
                  value={feature}
                  onChange={(e) =>
                    updateFeature("yearly", index, e.target.value)
                  }
                  className="flex-1 p-2 border rounded"
                />
                <button
                  onClick={() =>
                    removeFeature("yearly", index)
                  }
                  className="ml-2 text-red-600"
                >
                  Supprimer
                </button>
              </div>
            ))}

            <button
              onClick={() => addFeature("yearly")}
              className="text-green-700 text-sm underline mb-6"
            >
              + Ajouter une fonctionnalité
            </button>

            <button
              onClick={handleSave}
              className="mt-auto bg-green-700 text-white py-2 rounded-lg"
            >
              Valider les modifications
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
