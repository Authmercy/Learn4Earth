import { Link } from "react-router-dom";
import Carousel from "../Components/Carousel";

export default function Home() {
  const images = [
    "/images/ai-learn.png",
    "/images/ai-robot-1.jpeg",
    "/images/ai-robot-2.png",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 px-6 md:px-12 py-10 font-poppins">

      {/* HERO */}
      <div className="flex flex-col md:flex-row justify-between items-center mt-10 md:mt-20">

        {/* LEFT CAROUSEL */}
        <div className="mb-10 md:mb-0 w-full md:w-1/2 h-64 md:h-[420px]">
          <Carousel images={images} />
        </div>

        {/* RIGHT TEXT */}
        <div className="max-w-xl md:w-1/2">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-green-800 leading-tight">
            Apprenez, progressez,
            <span className="text-green-600"> sauvez la planète.</span>
          </h1>

          <p className="mt-4 text-gray-700 text-lg">
            EcoLearnAI génère des parcours d’apprentissage personnalisés grâce à l’IA
            et compense automatiquement votre empreinte carbone en finançant la
            plantation d’arbres à chaque session.
          </p>

          <div className="flex gap-4 mt-6">
            <Link to="/register">
              <button className="bg-green-700 text-white px-6 py-3 rounded-md font-semibold hover:bg-green-800 transition">
                Commencer maintenant
              </button>
            </Link>

            <Link to="/features">
              <button className="border border-green-700 text-green-700 px-6 py-3 rounded-md font-semibold hover:bg-green-700 hover:text-white transition">
                Découvrir
              </button>
            </Link>
          </div>
        </div>
      </div>

      {/* VALUES SECTION */}
      <section className="mt-24 grid md:grid-cols-3 gap-8">
        <div className="bg-white/80 backdrop-blur-md p-6 rounded-xl shadow text-center hover:shadow-lg transition">
          <h3 className="text-xl font-semibold text-green-700">IA éducative</h3>
          <p className="text-gray-600 mt-2">
            Des parcours d’apprentissage générés selon votre niveau, vos objectifs et votre rythme.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-md p-6 rounded-xl shadow text-center hover:shadow-lg transition">
          <h3 className="text-xl font-semibold text-green-700">Impact mesuré</h3>
          <p className="text-gray-600 mt-2">
            Calcul automatique de votre empreinte carbone à chaque session.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-md p-6 rounded-xl shadow text-center hover:shadow-lg transition">
          <h3 className="text-xl font-semibold text-green-700">Reforestation</h3>
          <p className="text-gray-600 mt-2">
            Chaque session finance la plantation d’arbres via nos partenaires.
          </p>
        </div>
      </section>
    </div>
  );
}
