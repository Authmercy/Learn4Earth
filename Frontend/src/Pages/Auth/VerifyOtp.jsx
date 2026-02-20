import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function VerifyOtp() {
  const navigate = useNavigate();
  const { state } = useLocation();

  const email = state?.email;

  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [timer, setTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);
  const [apiError, setApiError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  /* TIMER */
  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => setTimer((t) => t - 1), 1000);
      return () => clearInterval(interval);
    }
    setCanResend(true);
  }, [timer]);

  const handleOtpChange = (value, index) => {
    if (!/^[0-9]?$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    if (value && index < 5) {
      document.getElementById(`otp-${index + 1}`).focus();
    }
  };

  /* VERIFY */
  const verifyOtp = async () => {
    const code = otp.join("");

    try {
      const response = await fetch(
        "http://206.189.56.166:8000/api/auth/verify-sms",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            code,   // ✅ CORRECTION ICI
          }),
        }
      );

      const data = await response.json();

      if (response.status === 200) {
        setSuccessMessage("Compte vérifié avec succès !");
        setTimeout(() => navigate("/login"), 1500);
      } else {
        setApiError(data?.detail || "Code OTP incorrect");
      }
    } catch {
      setApiError("Erreur serveur");
    }
  };

  /* RESEND */
  const resendOtp = async () => {
    if (!canResend) return;

    setApiError("");
    setSuccessMessage("");

    try {
      const response = await fetch(
        "http://206.189.56.166:8000/api/auth/resend-otp",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email }),
        }
      );

      if (response.status === 200) {
        setSuccessMessage("Un nouveau code a été envoyé.");
        setTimer(60);
        setCanResend(false);
        setOtp(["", "", "", "", "", ""]);
        document.getElementById("otp-0").focus();
      } else {
        setApiError("Impossible de renvoyer le code.");
      }
    } catch {
      setApiError("Erreur serveur");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 flex items-center justify-center px-6">

      <div className="bg-white shadow-xl rounded-2xl p-10 w-full max-w-md">

        <h2 className="text-2xl font-bold text-center text-green-800 mb-4">
          Vérification OTP
        </h2>

        <p className="text-center text-gray-600 mb-6">
          Saisissez le code reçu par SMS ou email
        </p>

        <div className="flex justify-center gap-3 mb-6">
          {otp.map((digit, index) => (
            <input
              key={index}
              id={`otp-${index}`}
              type="text"
              maxLength={1}
              value={digit}
              onChange={(e) => handleOtpChange(e.target.value, index)}
              className="w-12 h-12 border rounded-lg text-center text-xl font-semibold focus:border-green-600 focus:ring-2 focus:ring-green-200 outline-none"
            />
          ))}
        </div>

        {apiError && <p className="text-red-600 text-center">{apiError}</p>}
        {successMessage && <p className="text-green-600 text-center">{successMessage}</p>}

        <button
          onClick={verifyOtp}
          className="bg-green-700 text-white py-3 px-6 rounded-lg hover:bg-green-800 w-full"
        >
          Vérifier le code
        </button>

        <div className="text-center mt-4 text-sm text-gray-700">
          {canResend ? (
            <button
              onClick={resendOtp}
              className="text-green-700 font-semibold hover:underline"
            >
              Renvoyer un nouveau code
            </button>
          ) : (
            <span>Renvoyer dans {timer}s</span>
          )}
        </div>
      </div>
    </div>
  );
}
