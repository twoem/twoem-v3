import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ComputerDesktopIcon, 
  PrinterIcon, 
  DocumentTextIcon,
  WifiIcon,
  CheckIcon
} from '@heroicons/react/24/outline';

const Services = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await axios.get(`${API}/services`);
      setServices(response.data);
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  };

  const getServiceDetails = (category) => {
    const details = {
      'government': {
        icon: DocumentTextIcon,
        color: 'blue',
        items: [
          'Logbook Transfer',
          'Vehicle Inspection',
          'Smart DL Application',
          'Handbook DL Renewal',
          'PSV Badge Applications'
        ]
      },
      'tax': {
        icon: DocumentTextIcon,
        color: 'green',
        items: [
          'Tax Compliance Certificate',
          'Individual Tax Return',
          'Advanced Tax',
          'Company Returns',
          'Group KRA PIN Application',
          'KRA PIN Retrieval',
          'Turnover Tax Return'
        ]
      },
      'printing': {
        icon: PrinterIcon,
        color: 'purple',
        items: [
          'Business Cards',
          'Award Certificates',
          'Brochures',
          'Funeral Programs',
          'Handouts',
          'Flyers',
          'Maps',
          'Posters',
          'Letterheads',
          'Calendars'
        ]
      },
      'cyber': {
        icon: ComputerDesktopIcon,
        color: 'indigo',
        items: [
          'Printing',
          'Lamination',
          'Photocopy',
          'Internet Browsing',
          'Typesetting',
          'Instant Passport Photos',
          'HELB Applications',
          'TSC Online Applications'
        ]
      },
      'other': {
        icon: WifiIcon,
        color: 'orange',
        items: [
          'High-Speed Internet',
          'Online Services',
          'Scanning & Photocopy',
          'Design & Layout',
          'Instant Passport Photos'
        ]
      }
    };

    return details[category] || {
      icon: ComputerDesktopIcon,
      color: 'gray',
      items: []
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading services...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Our Services</h1>
            <p className="text-xl text-blue-100 max-w-2xl mx-auto">
              Comprehensive digital services to meet all your cyber café and business needs
            </p>
          </div>
        </div>
      </div>

      {/* Services List */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-12">
            {services.map((service, index) => {
              const details = getServiceDetails(service.category);
              const IconComponent = details.icon;
              const isEven = index % 2 === 0;

              return (
                <div 
                  key={service.id} 
                  className={`flex flex-col ${isEven ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center gap-12`}
                >
                  {/* Image */}
                  <div className="flex-1">
                    <div className="relative h-64 lg:h-80 rounded-xl overflow-hidden shadow-lg">
                      <img 
                        src={service.image_url} 
                        alt={service.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          // Fallback images for each service type
                          const fallbacks = {
                            'government': 'https://cdn.pixabay.com/photo/2017/06/10/07/38/driver-license-2384917_960_720.jpg',
                            'tax': 'https://cdn.pixabay.com/photo/2017/04/16/10/35/business-2232970_960_720.jpg',
                            'printing': 'https://cdn.pixabay.com/photo/2019/05/15/18/02/poster-4201976_960_720.jpg',
                            'cyber': 'https://cdn.pixabay.com/photo/2014/12/16/22/25/computer-570932_960_720.jpg',
                            'other': 'https://cdn.pixabay.com/photo/2016/03/27/19/06/passport-1284701_960_720.jpg'
                          };
                          e.target.src = fallbacks[service.category] || fallbacks.other;
                        }}
                      />
                      <div className={`absolute inset-0 bg-gradient-to-t from-${details.color}-600/50 to-transparent`}></div>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className={`bg-white rounded-xl shadow-lg p-8 border-l-4 border-${details.color}-500`}>
                      <div className="flex items-center mb-6">
                        <div className={`bg-${details.color}-100 p-3 rounded-lg`}>
                          <IconComponent className={`h-8 w-8 text-${details.color}-600`} />
                        </div>
                        <h2 className="text-2xl lg:text-3xl font-bold text-gray-900 ml-4">
                          {service.name}
                        </h2>
                      </div>

                      <p className="text-gray-600 text-lg mb-6">
                        {service.description}
                      </p>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {details.items.map((item, itemIndex) => (
                          <div key={itemIndex} className="flex items-center space-x-3">
                            <CheckIcon className={`h-5 w-5 text-${details.color}-500`} />
                            <span className="text-gray-700">{item}</span>
                          </div>
                        ))}
                      </div>

                      <div className="mt-8">
                        <a
                          href="#contact"
                          className={`inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-${details.color}-600 hover:bg-${details.color}-700 transition-colors`}
                        >
                          Get This Service
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Contact CTA */}
          <div className="mt-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl text-white p-8 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Contact us today to discuss your specific needs and get a customized solution
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://wa.me/0707330204"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
              >
                WhatsApp Us
              </a>
              <a
                href="tel:0707330204"
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                Call Now
              </a>
              <a
                href="mailto:twoemcyber@gmail.com"
                className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
              >
                Email Us
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Services;