import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './Components/Common/Navbar'
import Footer from './Components/Common/Footer'
import ProtectedAdminRoute from './Components/ProtectedAdminRoute'
import Home from "./Pages/Home";
import Login from "./Pages/Auth/Login";
import Register from "./Pages/Auth/Register";
import Pricing from './Pages/Pricing';
import Courses from './Pages/Courses/Courses';
import UserProfile from './Pages/User/UserProfile';
import VerifyOtp from './Pages/Auth/VerifyOtp';
import GenerateCourse from './Pages/Courses/GenerateCourse';
import CourseDetail from './Pages/Courses/CourseDetail';
import StartSession from './Pages/Courses/StartSession';
import SessionDetail from './Pages/Courses/SessionDetail';
import MesSessions from './Pages/Courses/MesSessions';
import Plans from './Pages/Abonnement/Plans';
import PaymentCallback from './Pages/Abonnement/PaymentCallback';
import Subscribe from './Pages/Abonnement/Subscribe';
import MyPayments from './Pages/Abonnement/MyPaiments';
import Invoice from './Pages/Abonnement/Invoice';
import PaymentStatus from './Pages/Abonnement/PaymentStatus';
import ImpactCarbone from './Pages/User/ImpactCarbone';
import Dashboard from './Pages/User/Dashboard';
import Contact from "./Pages/Contact";
import Admin from "./Pages/Admin";
import Features from "@/Pages/Features.jsx";

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow">
          <Routes>

            {/* Accueil */}
            <Route path="/" element={<Home />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/features" element={<Features />} />

            {/* Auth */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Users */}
            <Route path="/courses" element={<Courses />} />
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/verify-otp" element={<VerifyOtp />} /> 

            {/* Courses */}
            <Route path="/generate-course" element={<GenerateCourse />} />
            <Route path="/course/:id" element={<CourseDetail />} /> 
            <Route path="/course/:id/start" element={<StartSession />} />
            <Route path="/session/:session_id" element={<SessionDetail />} />
            <Route path="/sessions" element={<MesSessions />} />

            <Route path="/plans" element={<Plans />} />
            <Route path="/subscribe/:plan_code" element={<Subscribe />} />

            <Route path="/payment-callback" element={<PaymentCallback />} />
            <Route path="/my-payments" element={<MyPayments />} />
            <Route path="/invoice/:payment_id" element={<Invoice />} />
            <Route path="/payment-status/:payment_id" element={<PaymentStatus />} />

            <Route path="/impact-carbone" element={<ImpactCarbone />} />
            <Route path="/dashboard" element={<Dashboard />} />

            <Route path="/contact" element={<Contact />} />

            <Route
              path="/admin"
              element={
                <ProtectedAdminRoute>
                  <Admin />
                </ProtectedAdminRoute>
              }
            />

          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}

export default App;
