import { useNavigate } from "react-router-dom";

const PricingCard = ({
  code,
  plan,
  price,
  duration,
  description,
  features = [],
  highlighted = false,
  buttonText = "Commencer",
  delay = 0
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/subscribe/${code}`, {
      state: {
        code,
        plan,
        price,
        duration,
        description,
        features
      }
    });
  };

  return (
    <div
      className={`p-8 rounded-2xl shadow-lg bg-white border transition-all duration-300 animate-slide-up
        ${highlighted ? "border-green-600 shadow-xl scale-[1.03]" : "border-gray-200"}
      `}
      style={{ animationDelay: `${delay}ms` }}
    >
      {/* Badge Populaire */}
      {highlighted && (
        <div className="absolute top-0 right-0">
          <div className="bg-green-600 text-white px-4 py-1 text-sm font-semibold rounded-bl-xl">
            Populaire
          </div>
        </div>
      )}

      {/* Header */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-green-800">{plan}</h3>
        <p className="text-gray-600 mt-1">{description || "Accès complet à la plateforme"}</p>
      </div>

      {/* Price */}
      <div className="mb-8">
        <div className="flex items-baseline">
          <span className="text-5xl font-bold text-green-700">{price}€</span>
          <span className="text-gray-500 ml-2">/ {duration}</span>
        </div>
      </div>

      {/* Button */}
      <button
        onClick={handleClick}
        className={`w-full py-3 rounded-xl font-semibold transition-all duration-300
          ${highlighted
            ? "bg-green-700 text-white hover:bg-green-800"
            : "border border-green-700 text-green-700 hover:bg-green-50"
          }
        `}
      >
        {buttonText}
      </button>

      {/* Features */}
      <div className="mt-8 space-y-4">
        <div className="text-sm font-semibold text-gray-700">Ce qui est inclus :</div>

        {features.length === 0 && (
          <p className="text-gray-500 text-sm">Fonctionnalités à venir…</p>
        )}

        {features.map((feature, index) => (
          <div key={index} className="flex items-start gap-3">
            <div
              className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center
                ${feature.included
                  ? "bg-green-100 text-green-700"
                  : "bg-gray-100 text-gray-400"
                }
              `}
            >
              {feature.included ? (
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </div>

            <span
              className={
                feature.included
                  ? "text-gray-800"
                  : "text-gray-400 line-through"
              }
            >
              {feature.text}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PricingCard;
