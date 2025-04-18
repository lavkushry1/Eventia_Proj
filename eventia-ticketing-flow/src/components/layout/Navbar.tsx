import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X, Ticket, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 bg-white shadow-md z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <Ticket className="h-8 w-8 text-primary" />
            <span className="ml-2 text-xl font-bold text-primary">Eventia</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-4">
            <Link to="/" className="text-gray-700 hover:text-primary px-3 py-2 rounded-md">
              Home
            </Link>
            <Link to="/events" className="text-gray-700 hover:text-primary px-3 py-2 rounded-md">
              Events
            </Link>
            <Link to="/events?category=IPL" className="text-gray-700 hover:text-primary px-3 py-2 rounded-md">
              IPL Tickets
            </Link>
            <Link to="/about" className="text-gray-700 hover:text-primary px-3 py-2 rounded-md">
              About
            </Link>
            <Link to="/admin-login">
              <Button variant="outline" size="sm" className="ml-4 flex items-center">
                <User className="h-4 w-4 mr-2" />
                Admin
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button 
              onClick={toggleMenu}
              className="text-gray-700 hover:text-primary"
              aria-label={isOpen ? "Close menu" : "Open menu"}
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <div 
        className={cn(
          "md:hidden bg-white",
          isOpen ? "block animate-slide-up" : "hidden"
        )}
      >
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <Link to="/" 
            className="block text-gray-700 hover:text-primary px-3 py-2 rounded-md"
            onClick={() => setIsOpen(false)}
          >
            Home
          </Link>
          <Link to="/events" 
            className="block text-gray-700 hover:text-primary px-3 py-2 rounded-md"
            onClick={() => setIsOpen(false)}
          >
            Events
          </Link>
          <Link to="/events?category=IPL" 
            className="block text-gray-700 hover:text-primary px-3 py-2 rounded-md"
            onClick={() => setIsOpen(false)}
          >
            IPL Tickets
          </Link>
          <Link to="/about" 
            className="block text-gray-700 hover:text-primary px-3 py-2 rounded-md"
            onClick={() => setIsOpen(false)}
          >
            About
          </Link>
          <div className="mt-4 px-3">
            <Link to="/admin-login" onClick={() => setIsOpen(false)}>
              <Button variant="outline" className="w-full justify-start">
                <User className="h-4 w-4 mr-2" />
                Admin Login
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
