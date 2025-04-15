
import React from 'react';
import { Link } from 'react-router-dom';
import { Ticket, Facebook, Twitter, Instagram, Mail, Phone } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white pt-12 pb-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center mb-4">
              <Ticket className="h-8 w-8 text-secondary" />
              <span className="ml-2 text-xl font-bold">Eventia</span>
            </div>
            <p className="text-gray-400 mb-4">Your go-to platform for booking IPL matches and other exciting events. No login required!</p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-secondary" aria-label="Facebook">
                <Facebook size={20} />
              </a>
              <a href="#" className="text-gray-400 hover:text-secondary" aria-label="Twitter">
                <Twitter size={20} />
              </a>
              <a href="#" className="text-gray-400 hover:text-secondary" aria-label="Instagram">
                <Instagram size={20} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="col-span-1">
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-400 hover:text-secondary">Home</Link>
              </li>
              <li>
                <Link to="/events" className="text-gray-400 hover:text-secondary">Events</Link>
              </li>
              <li>
                <Link to="/ipl-tickets" className="text-gray-400 hover:text-secondary">IPL Tickets</Link>
              </li>
              <li>
                <Link to="/about" className="text-gray-400 hover:text-secondary">About Us</Link>
              </li>
            </ul>
          </div>

          {/* Help & Support */}
          <div className="col-span-1">
            <h3 className="text-lg font-semibold mb-4">Help & Support</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-secondary">FAQs</a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-secondary">Shipping Policy</a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-secondary">Cancellation Policy</a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-secondary">Terms & Conditions</a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div className="col-span-1">
            <h3 className="text-lg font-semibold mb-4">Contact Us</h3>
            <ul className="space-y-2">
              <li className="flex items-center text-gray-400">
                <Mail size={16} className="mr-2" />
                <span>support@eventia.com</span>
              </li>
              <li className="flex items-center text-gray-400">
                <Phone size={16} className="mr-2" />
                <span>+91 9876543210</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8">
          <p className="text-center text-gray-400">
            &copy; {new Date().getFullYear()} Eventia. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
