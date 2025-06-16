import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <img 
                className="h-10 w-10 rounded-full" 
                src="/images/twoem.jpg" 
                alt="TWOEM Logo" 
              />
              <span className="ml-2 text-xl font-bold">TWOEM Online Productions</span>
            </div>
            <p className="text-gray-300 mb-4">
              Your trusted Cyber Café in Kagwe Town—high-speed internet, printing, 
              lamination, and all your digital needs under one roof.
            </p>
            <div className="text-gray-300">
              <p className="mb-2">📍 Plaza Building, Kagwe Town (opposite Total Petrol Station)</p>
              <p className="mb-2">📞 0707 330 204 / 0769 720 002</p>
              <p>✉️ twoemcyber@gmail.com</p>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-300 hover:text-white transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/services" className="text-gray-300 hover:text-white transition-colors">
                  Services
                </Link>
              </li>
              <li>
                <Link to="/eulogies" className="text-gray-300 hover:text-white transition-colors">
                  Eulogies
                </Link>
              </li>
              <li>
                <a href="/#contact" className="text-gray-300 hover:text-white transition-colors">
                  Contact Us
                </a>
              </li>
            </ul>
          </div>

          {/* Services */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Our Services</h3>
            <ul className="space-y-2 text-gray-300">
              <li>eCitizen Services</li>
              <li>iTax Services</li>
              <li>Digital Printing</li>
              <li>Cyber Services</li>
              <li>Internet Installation</li>
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-300 text-sm">
            © 2025 TWOEM Online Productions. All rights reserved.
          </p>
          <div className="flex space-x-4 mt-4 md:mt-0">
            <a 
              href="https://wa.me/0707330204" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-green-400 hover:text-green-300 transition-colors"
            >
              WhatsApp
            </a>
            <a 
              href="mailto:twoemcyber@gmail.com"
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              Email
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;