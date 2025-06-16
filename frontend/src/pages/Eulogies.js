import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { 
  DocumentIcon, 
  CalendarIcon, 
  UserIcon,
  ArrowDownTrayIcon,
  PlusIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';

const Eulogies = () => {
  const [eulogies, setEulogies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    title: '',
    deceased_name: '',
    description: '',
    file: null
  });

  const { isAuthenticated } = useAuth();
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchEulogies();
  }, []);

  const fetchEulogies = async () => {
    try {
      const response = await axios.get(`${API}/eulogies`);
      setEulogies(response.data);
    } catch (error) {
      console.error('Error fetching eulogies:', error);
      toast.error('Failed to load eulogies');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setUploadForm({ ...uploadForm, file });
    } else {
      toast.error('Please select a PDF file');
      e.target.value = '';
    }
  };

  const convertFileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = error => reject(error);
    });
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!uploadForm.file) {
      toast.error('Please select a PDF file');
      return;
    }

    setUploading(true);

    try {
      const base64Content = await convertFileToBase64(uploadForm.file);
      
      const uploadData = {
        title: uploadForm.title,
        deceased_name: uploadForm.deceased_name,
        description: uploadForm.description,
        content: base64Content
      };

      await axios.post(`${API}/eulogies`, uploadData);
      
      toast.success('Eulogy uploaded successfully!');
      setShowUploadForm(false);
      setUploadForm({ title: '', deceased_name: '', description: '', file: null });
      fetchEulogies();
    } catch (error) {
      toast.error('Failed to upload eulogy');
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (eulogy) => {
    try {
      const response = await axios.get(`${API}/eulogies/${eulogy.id}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', eulogy.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Eulogy downloaded successfully');
      fetchEulogies(); // Refresh to update download count
    } catch (error) {
      if (error.response?.status === 410) {
        toast.error('This eulogy has expired');
      } else {
        toast.error('Failed to download eulogy');
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTimeRemaining = (expiresAt) => {
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diff = expiry - now;
    
    if (diff <= 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) {
      return `${days} day${days !== 1 ? 's' : ''} remaining`;
    } else {
      return `${hours} hour${hours !== 1 ? 's' : ''} remaining`;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-gray-600">Loading eulogies...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Eulogies</h1>
            <p className="text-xl text-purple-100 max-w-2xl mx-auto mb-8">
              Access and download eulogies. Note that they expire after 3 days.
            </p>
            {isAuthenticated && (
              <button
                onClick={() => setShowUploadForm(true)}
                className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-flex items-center"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Upload Eulogy
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Upload Form Modal */}
      {showUploadForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold mb-4">Upload Eulogy</h3>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  required
                  value={uploadForm.title}
                  onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter eulogy title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deceased Name
                </label>
                <input
                  type="text"
                  required
                  value={uploadForm.deceased_name}
                  onChange={(e) => setUploadForm({ ...uploadForm, deceased_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter deceased person's name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={uploadForm.description}
                  onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows={3}
                  placeholder="Enter description"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  PDF File
                </label>
                <input
                  type="file"
                  accept=".pdf"
                  required
                  onChange={handleFileChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="submit"
                  disabled={uploading}
                  className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50"
                >
                  {uploading ? <LoadingSpinner size="sm" color="white" /> : 'Upload'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUploadForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg font-semibold hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Eulogies List */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {eulogies.length === 0 ? (
            <div className="text-center py-12">
              <DocumentIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No eulogies available</h3>
              <p className="text-gray-600">
                {isAuthenticated 
                  ? 'Upload the first eulogy to get started.' 
                  : 'Please check back later or contact us if you need access.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {eulogies.map((eulogy) => (
                <div key={eulogy.id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <DocumentIcon className="h-8 w-8 text-purple-600" />
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      getTimeRemaining(eulogy.expires_at) === 'Expired' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {getTimeRemaining(eulogy.expires_at)}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {eulogy.title}
                  </h3>

                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <div className="flex items-center">
                      <UserIcon className="h-4 w-4 mr-2" />
                      <span>{eulogy.deceased_name}</span>
                    </div>
                    
                    <div className="flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-2" />
                      <span>{formatDate(eulogy.uploaded_at)}</span>
                    </div>

                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-2" />
                      <span>Expires: {formatDate(eulogy.expires_at)}</span>
                    </div>

                    <div className="flex items-center">
                      <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                      <span>{eulogy.download_count} downloads</span>
                    </div>
                  </div>

                  {eulogy.description && (
                    <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                      {eulogy.description}
                    </p>
                  )}

                  <button
                    onClick={() => handleDownload(eulogy)}
                    disabled={getTimeRemaining(eulogy.expires_at) === 'Expired'}
                    className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                    {getTimeRemaining(eulogy.expires_at) === 'Expired' ? 'Expired' : 'Download PDF'}
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Note about expiration */}
          <div className="mt-12 bg-amber-50 border border-amber-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-amber-800 mb-2">
              📅 Important Note
            </h3>
            <p className="text-amber-700">
              All eulogies expire automatically after 3 days from upload date. 
              Please download them within this period. If you need access to an expired eulogy, 
              please contact us at{' '}
              <a href="mailto:twoemcyber@gmail.com" className="underline font-medium">
                twoemcyber@gmail.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Eulogies;