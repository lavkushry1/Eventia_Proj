import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  BarChart, 
  Calendar, 
  Tag, 
  CreditCard, 
  Settings, 
  Users, 
  LogOut, 
  Image,
  Menu,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAdminAuth } from '@/hooks/use-admin-auth';
import { toast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const { adminToken, logout } = useAdminAuth();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  
  if (!adminToken) {
    navigate('/admin-login');
    return null;
  }

  const handleLogout = () => {
    logout();
    toast({
      title: "Logged out",
      description: "You have been logged out successfully."
    });
    navigate('/admin-login');
  };

  const NavItem = ({ 
    href, 
    icon: Icon, 
    title 
  }: { 
    href: string, 
    icon: React.ElementType, 
    title: string 
  }) => {
    const isActive = location.pathname === href;
    
    return (
      <Link 
        to={href} 
        className={cn(
          "flex items-center gap-x-2 px-3 py-2 text-sm rounded-md transition-colors",
          isActive 
            ? "bg-gray-100 text-gray-900 font-medium" 
            : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
        )}
      >
        <Icon className="h-4 w-4" />
        <span>{title}</span>
      </Link>
    );
  };

  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b sticky top-0 z-30 bg-white">
        <div className="flex h-16 items-center justify-between px-4 sm:px-6">
          <div className="flex items-center">
            <Button 
              variant="ghost" 
              size="icon" 
              className="md:hidden mr-2"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <Link to="/admin-dashboard" className="font-bold text-xl">
              Eventia Admin
            </Link>
          </div>
          
          <Button variant="ghost" onClick={handleLogout} className="flex items-center">
            <LogOut className="mr-2 h-4 w-4" />
            <span>Logout</span>
          </Button>
        </div>
      </header>
      
      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className={cn(
          "fixed inset-y-0 left-0 z-20 mt-16 w-64 transform border-r bg-white p-4 transition-transform duration-200 md:relative md:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}>
          <nav className="space-y-1 mt-2">
            <NavItem href="/admin-dashboard" icon={BarChart} title="Dashboard" />
            <NavItem href="/admin-events" icon={Calendar} title="Events" />
            <NavItem href="/admin-discounts" icon={Tag} title="Discounts" />
            <NavItem href="/admin-upi" icon={CreditCard} title="Payment Settings" />
            <NavItem href="/admin-utr" icon={CreditCard} title="Payment Verification" />
            <NavItem href="/admin-images" icon={Image} title="Image Management" />
            <NavItem href="#" icon={Users} title="User Management" />
            <NavItem href="#" icon={Settings} title="Settings" />
          </nav>
        </aside>
        
        {/* Main content */}
        <main className={cn(
          "flex-1 overflow-y-auto bg-gray-50 p-4 transition-all",
          sidebarOpen ? "md:ml-0" : "md:ml-0"
        )}>
          {children}
        </main>
      </div>
    </div>
  );
};

export default AdminLayout; 