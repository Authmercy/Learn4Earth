import { useState } from "react";

export default function Contact() {
  const [formData, setFormData] = useState({
    nom: "",
    prenom: "",
    email: "",
    telephone: "",
    titre: "",
    message: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert("Message envoyé avec succès !");
    console.log(formData);

    setFormData({
      nom: "",
      prenom: "",
      email: "",
      telephone: "",
      titre: "",
      message: "",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-16 px-4">
      <div className="bg-white shadow-xl rounded-2xl w-full max-w-3xl p-10">
        
        <h1 className="text-3xl font-bold text-green-700 mb-8 text-center">
          📩 Contactez-nous
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">

          {/* Nom & Prénom */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Nom</label>
              <input
                type="text"
                name="nom"
                value={formData.nom}
                onChange={handleChange}
                required
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Prénom</label>
              <input
                type="text"
                name="prenom"
                value={formData.prenom}
                onChange={handleChange}
                required
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
            />
          </div>

          {/* Téléphone */}
          <div>
            <label className="block text-sm font-medium mb-2">Numéro de téléphone</label>
            <input
              type="tel"
              name="telephone"
              value={formData.telephone}
              onChange={handleChange}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
            />
          </div>

          {/* ✅ Nouveau champ Titre */}
          <div>
            <label className="block text-sm font-medium mb-2">Titre</label>
            <input
              type="text"
              name="titre"
              value={formData.titre}
              onChange={handleChange}
              required
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
              placeholder="Sujet de votre message"
            />
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              name="message"
              rows="5"
              value={formData.message}
              onChange={handleChange}
              required
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
            ></textarea>
          </div>

          {/* Bouton */}
          <div className="text-center">
            <button
              type="submit"
              className="bg-green-700 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-800 transition"
            >
              Envoyer le message
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}
