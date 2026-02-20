import React, {useState} from 'react';

const Features = () => {
  const [activeFeature, setActiveFeature] = useState(null);

  const features = [
    {
      id: 'ai-learning',
      icon: '🧠',
      title: 'IA Adaptative',
      subtitle: 'Parcours personnalisés en temps réel',
      description: 'Notre moteur d\'apprentissage analyse votre progression et adapte chaque leçon à votre rythme et style d\'apprentissage. Chaque apprenant suit un chemin unique.',
      metrics: [
        {label: 'Taux de rétention', value: '94%'},
        {label: 'Temps optimisé', value: '-35%'}
      ]
    },
    {
      id: 'carbon-tracking',
      icon: '🌍',
      title: 'Empreinte Carbone',
      subtitle: 'Transparence totale sur votre impact',
      description: 'Chaque session calcule son empreinte carbone en temps réel : serveurs, bande passante, stockage. Nous transformons ces données en actions concrètes de reforestation.',
      metrics: [
        {label: 'CO₂ calculé', value: 'En direct'},
        {label: 'Précision', value: '99.2%'}
      ]
    },
    {
      id: 'impact-dashboard',
      icon: '📊',
      title: 'Tableau d\'Impact',
      subtitle: 'Visualisez votre contribution',
      description: 'Des graphiques interactifs D3.js qui montrent simultanément votre progression pédagogique et votre impact environnemental. Gamification éthique qui dépasse l\'individu.',
      metrics: [
        {label: 'Métriques suivies', value: '12+'},
        {label: 'Mise à jour', value: 'Temps réel'}
      ]
    },
    {
      id: 'reforestation',
      icon: '🌱',
      title: 'Action Climatique',
      subtitle: 'Votre apprentissage plante des arbres',
      description: 'Intégration directe avec des ONG de reforestation. Chaque heure d\'apprentissage finance la plantation d\'arbres. Impact mesurable, transparent, vérifiable.',
      metrics: [
        {label: 'Partenaires', value: '8 ONG'},
        {label: 'Zones plantées', value: '23 pays'}
      ]
    }
  ];

  const getAnimationDelay = (index) => {
    const delays = ['', 'animate-float-delay-1', 'animate-float-delay-2', 'animate-float-delay-3'];
    return delays[index] || '';
  };

  const getGridFadeAnimation = (index) => {
    const animations = ['animate-grid-fade-1', 'animate-grid-fade-2', 'animate-grid-fade-3', 'animate-grid-fade-4'];
    return animations[index] || '';
  };

  const getFeatureCardClasses = (featureId, index) => {
    const isActive = activeFeature === featureId;
    const baseClasses = 'bg-white/80 border border-emerald-200/50 rounded-3xl p-10 cursor-pointer transition-all duration-500 ease-out relative overflow-hidden backdrop-blur-md hover:-translate-y-2 hover:border-emerald-400/60 hover:bg-white/90 hover:shadow-2xl hover:shadow-emerald-500/20 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 text-left w-full';
    const activeClasses = isActive ? 'border-emerald-500/70 bg-white/95 shadow-xl shadow-emerald-400/25' : '';
    const animationClass = getGridFadeAnimation(index);

    return `${baseClasses} ${activeClasses} ${animationClass}`;
  };

  const handleFeatureToggle = (featureId) => {
    setActiveFeature(activeFeature === featureId ? null : featureId);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-green-50 text-slate-800 overflow-x-hidden relative">
      {/* Background effects */}
      <div className="absolute inset-0 pointer-events-none animate-breathe">
        <div
          className="absolute top-[15%] left-[10%] w-[500px] h-[500px] bg-emerald-400/20 rounded-full blur-[120px]"></div>
        <div
          className="absolute top-[60%] right-[15%] w-[400px] h-[400px] bg-teal-400/15 rounded-full blur-[100px]"></div>
        <div
          className="absolute bottom-[10%] left-[40%] w-[350px] h-[350px] bg-green-300/20 rounded-full blur-[90px]"></div>
      </div>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-8 py-16 pb-32 relative z-10 font-outfit">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <button
              key={feature.id}
              className={getFeatureCardClasses(feature.id, index)}
              onClick={() => handleFeatureToggle(feature.id)}
              onMouseMove={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                e.currentTarget.style.setProperty('--mouse-x', `${x}%`);
                e.currentTarget.style.setProperty('--mouse-y', `${y}%`);
              }}
              aria-pressed={activeFeature === feature.id}
              aria-label={`${feature.title}: ${feature.subtitle}`}
            >
              <div
                className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                style={{
                  background: `radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(16, 185, 129, 0.12) 0%, transparent 50%)`
                }}
              />

              <div className={`flex gap-3 items-center mb-3`}>
                <span className={`text-6xl block drop-shadow-[0_4px_12px_rgba(16,185,129,0.3)] animate-float ${getAnimationDelay(index)}`}>
                  {feature.icon}
                </span>

                <h3 className="font-crimson text-3xl font-bold text-emerald-800">
                  {feature.title}
                </h3>
              </div>

              <p className="text-base text-emerald-600 mb-5 font-semibold">
                {feature.subtitle}
              </p>
              <p className="text-base leading-relaxed text-slate-700 mb-8">
                {feature.description}
              </p>

              <div className="flex gap-8 pt-6 border-t border-emerald-200/50">
                {feature.metrics.map((metric, idx) => (
                  <div key={idx} className="flex-1">
                    <span className="font-crimson text-2xl font-bold text-emerald-600 block mb-1">
                      {metric.value}
                    </span>
                    <span className="text-xs text-emerald-700/70 uppercase tracking-wide font-medium">
                      {metric.label}
                    </span>
                  </div>
                ))}
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center px-4 py-4 pb-5 relative z-10 font-outfit">
        <h2 className="font-crimson text-4xl md:text-6xl font-extrabold text-emerald-700 mb-6">
          Prêt à transformer votre apprentissage ?
        </h2>
        <p className="text-lg md:text-xl text-slate-700 max-w-2xl mx-auto mb-10 leading-relaxed">
          Rejoignez une communauté qui apprend et agit pour le climat.
          Chaque session compte, chaque arbre compte.
        </p>
        <a href={`/login`}>
          <button className="inline-block px-12 py-5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-lg font-semibold rounded-full
          transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-emerald-500/40
          hover:from-emerald-600 hover:to-teal-600 tracking-wide">
            Commencer Gratuitement
          </button>
        </a>

        <div className="flex flex-wrap justify-center gap-3 mt-12">
          {['🚀 FastAPI', '⚛️ React', '🐘 PostgreSQL', '🐳 Docker', '☁️ AWS ECS', '🤖 OpenAI GPT'].map((tech, idx) => (
            <span key={idx}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-white/60 border border-emerald-300/40 rounded-full text-sm text-emerald-700 font-medium backdrop-blur-sm">
              {tech}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Features;