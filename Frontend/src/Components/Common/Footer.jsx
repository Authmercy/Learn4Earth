export default function Footer() {
  return (
    <footer className="bg-green-900 text-white py-10 mt-20">
      <div className="max-w-7xl mx-auto px-6 text-center">
        <p className="text-green-200">
          © {new Date().getFullYear()} EcoLearnAI — Tous droits réservés.
        </p>
      </div>
    </footer>
  );
}
