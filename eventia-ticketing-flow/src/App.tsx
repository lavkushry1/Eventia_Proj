import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import Events from "./pages/Events";
import EventDetail from "./pages/EventDetail";
import Checkout from "./pages/Checkout";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import AdminEventManagement from "./pages/AdminEventManagement";
import AdminUpiManagement from "./pages/AdminUpiManagement";
import AdminUtrVerification from "./pages/AdminUtrVerification";
import AdminImageUploads from "./pages/AdminImageUploads";
import ARVenuePreview from "./pages/ARVenuePreview";
import NotFound from "./pages/NotFound";
import About from "./pages/About";
import AdminDiscountManagement from "./pages/AdminDiscountManagement";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/events" element={<Events />} />
        <Route path="/event/:id" element={<EventDetail />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/about" element={<About />} />
        <Route path="/admin-login" element={<AdminLogin />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/admin-events" element={<AdminEventManagement />} />
        <Route path="/admin-events/new" element={<AdminEventManagement />} />
        <Route path="/admin/events/new" element={<Navigate to="/admin-events/new" replace />} />
        <Route path="/admin-upi" element={<AdminUpiManagement />} />
        <Route path="/admin/upi-management" element={<Navigate to="/admin-upi" replace />} />
        <Route path="/admin-utr" element={<AdminUtrVerification />} />
        <Route path="/admin-images" element={<AdminImageUploads />} />
        <Route path="/admin/event/:eventId/images" element={<AdminImageUploads />} />
        <Route path="/admin-discounts" element={<AdminDiscountManagement />} />
        <Route path="/admin/discounts" element={<Navigate to="/admin-discounts" replace />} />
        <Route path="/venue-preview/:id" element={<ARVenuePreview />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
