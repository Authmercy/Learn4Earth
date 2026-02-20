import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function EditProfile() {
  const navigate = useNavigate();
  const storedUser = JSON.parse(localStorage.getItem("user"));

  const [form, setForm] = useState({
    full_name: storedUser.full_name,
    phone_number: storedUser.phone_number,
    address_city: storedUser.address_city,
    address_country: storedUser.address_country,
    level: storedUser.level,
  });

  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError("");

    try {
      const response = await fetch("http://206.189.56.166:8000/api/auth/update-profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (response.status === 200) {
        localStorage.setItem("user", JSON.stringify(data.user));
        setSuccess("Profil mis à jour !");
        setTimeout(() => navigate("/profile"), 1000);
        return;
      }

      setApiError("Impossible de mettre à jour le profil");

    } catch {
      setApiError("Erreur serveur");
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-10 p-6 bg-white shadow-xl rounded-xl">
      <h1 className="text-3xl font-bold text-green-700 mb-6">
        Modifier mon profil
      </h1>

      <form className="grid grid-cols-1 md:grid-cols-2 gap-6" onSubmit={handleSubmit}>

        <div className="col-span-2">
          <label className="text-gray-500 text-sm">Nom complet</label>
          <input
            type="text"
            name="full_name"
            value={form.full_name}
            onChange={handleChange}
            className="border p-3 rounded-lg w-full"
          />
        </div>

        <div>
          <label className="text-gray-500 text-sm">Téléphone</label>
          <input
            type="text"
            name="phone_number"
            value={form.phone_number}
            onChange={handleChange}
            className="border p-3 rounded-lg w-full"
          />
        </div>

        <div>
          <label className="text-gray-500 text-sm">Ville</label>
          <input
            type="text"
            name="address_city"
            value={form.address_city}
            onChange={handleChange}
            className="border p-3 rounded-lg w-full"
          />
        </div>

        <div>
          <label className="text-gray-500 text-sm">Pays</label>
          <input
            type="text"
            name="address_country"
            value={form.address_country}
            onChange={handleChange}
            className="border p-3 rounded-lg w-full"
          />
        </div>

        <div>
          <label className="text-gray-500 text-sm">Niveau</label>
          <select
            name="level"
            value={form.level}
            onChange={handleChange}
            className="border p-3 rounded-lg w-full"
          >
            <option value="debutant">Débutant</option>
            <option value="intermediaire">Intermédiaire</option>
            <option value="avance">Avancé</option>
          </select>
        </div>

        {apiError && <p className="text-red-600 text-sm col-span-2">{apiError}</p>}
        {success && <p className="text-green-600 text-sm col-span-2">{success}</p>}

        <button className="col-span-2 bg-green-700 text-white py-3 rounded-lg hover:bg-green-800">
          Enregistrer
        </button>
      </form>
    </div>
  );
}
