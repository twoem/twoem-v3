import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { 
  FolderIcon, 
  ArrowDownTrayIcon,
  EyeIcon,
  EyeSlashIcon,
  PlusIcon,
  DocumentIcon,
  CalendarIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/LoadingSpinner';
import ProtectedRoute from '../components/ProtectedRoute';

const Downloads = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showPublicOnly, setShowPublicOnly] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    filename: '',
    description: '',
    is_public: false,
    file: null
  });

  const { user, isAdmin } = useAuth();
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    fetchFiles();
  }, [showPublicOnly]);

  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${API}/files`, {
        params: { public_only: showPublicOnly }
      });
      setFiles(response.data);
    } catch (error) {
      console.error('Error fetching files:', error);
      toast.error('Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Check file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        toast.error('File size must be less than 50MB');
        e.target.value = '';
        return;
      }
      
      setUploadForm({ 
        ...uploadForm, 
        file,
        filename: uploadForm.filename || file.name
      });
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
      toast.error('Please select a file');
      return;
    }

    setUploading(true);

    try {
      const base64Content = await convertFileToBase64(uploadForm.file);
      
      const uploadData = {
        filename: uploadForm.filename,
        file_type: uploadForm.file.type,
        file_size: uploadForm.file.size,
        description: uploadForm.description,
        content: base64Content,
        is_public: uploadForm.is_public
      };

      await axios.post(`${API}/files`, uploadData);
      
      toast.success('File uploaded successfully!');
      setShowUploadForm(false);
      setUploadForm({ filename: '', description: '', is_public: false, file: null });
      fetchFiles();
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to upload file';
      toast.error(message);
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (file) => {
    try {
      const response = await axios.get(`${API}/files/${file.id}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', file.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('File downloaded successfully');
      fetchFiles(); // Refresh to update download count
    } catch (error) {
      if (error.response?.status === 403) {
        toast.error('Access denied. You do not have permission to download this file.');
      } else if (error.response?.status === 404) {
        toast.error('File not found');
      } else {
        toast.error('Failed to download file');
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    const iconClass = "h-8 w-8";
    
    if (['pdf'].includes(extension)) {
      return <DocumentIcon className={`${iconClass} text-red-600`} />;
    } else if (['doc', 'docx'].includes(extension)) {
      return <DocumentIcon className={`${iconClass} text-blue-600`} />;
    } else if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
      return <DocumentIcon className={`${iconClass} text-green-600`} />;
    } else {
      return <DocumentIcon className={`${iconClass} text-gray-600`} />;
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 pt-20">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold mb-4">Downloads</h1>
              <p className="text-xl text-green-100 max-w-2xl mx-auto mb-8">
                Access your files and documents securely
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button
                  onClick={() => setShowUploadForm(true)}
                  className="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-flex items-center"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Upload File
                </button>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowPublicOnly(!showPublicOnly)}
                    className="flex items-center space-x-2 bg-white bg-opacity-20 px-4 py-2 rounded-lg hover:bg-opacity-30 transition-colors"
                  >
                    {showPublicOnly ? (
                      <EyeIcon className="h-5 w-5" />
                    ) : (
                      <EyeSlashIcon className="h-5 w-5" />
                    )}
                    <span>{showPublicOnly ? 'Public Files Only' : 'All Accessible Files'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Upload Form Modal */}
        {showUploadForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-md w-full p-6">
              <h3 className="text-xl font-bold mb-4">Upload File</h3>
              <form onSubmit={handleUpload} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filename
                  </label>
                  <input
                    type="text"
                    required
                    value={uploadForm.filename}
                    onChange={(e) => setUploadForm({ ...uploadForm, filename: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="Enter filename"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (Optional)
                  </label>
                  <textarea
                    value={uploadForm.description}
                    onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    rows={3}
                    placeholder="Enter description"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    File
                  </label>
                  <input
                    type="file"
                    required
                    onChange={handleFileChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Maximum file size: 50MB</p>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_public"
                    checked={uploadForm.is_public}
                    onChange={(e) => setUploadForm({ ...uploadForm, is_public: e.target.checked })}
                    className="h-4 w-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                  />
                  <label htmlFor="is_public" className="ml-2 text-sm text-gray-700">
                    Make this file publicly accessible
                  </label>
                </div>

                <div className="flex space-x-4 pt-4">
                  <button
                    type="submit"
                    disabled={uploading}
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:opacity-50"
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

        {/* Files List */}
        <div className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {loading ? (
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-gray-600">Loading files...</p>
              </div>
            ) : files.length === 0 ? (
              <div className="text-center py-12">
                <FolderIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {showPublicOnly ? 'No public files available' : 'No files available'}
                </h3>
                <p className="text-gray-600">
                  Upload your first file to get started.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {files.map((file) => (
                  <div key={file.id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      {getFileIcon(file.filename)}
                      <div className="flex space-x-2">
                        {file.is_public ? (
                          <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                            Public
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
                            Private
                          </span>
                        )}
                      </div>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2 truncate">
                      {file.filename}
                    </h3>

                    <div className="space-y-2 text-sm text-gray-600 mb-4">
                      <div className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-2" />
                        <span>{formatDate(file.uploaded_at)}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <DocumentIcon className="h-4 w-4 mr-2" />
                        <span>{formatFileSize(file.file_size)}</span>
                      </div>

                      <div className="flex items-center">
                        <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                        <span>{file.download_count} downloads</span>
                      </div>

                      {(file.uploaded_by === user?.id || isAdmin) && (
                        <div className="flex items-center">
                          <UserIcon className="h-4 w-4 mr-2" />
                          <span>Uploaded by you</span>
                        </div>
                      )}
                    </div>

                    {file.description && (
                      <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                        {file.description}
                      </p>
                    )}

                    <button
                      onClick={() => handleDownload(file)}
                      className="w-full bg-green-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-green-700 transition-colors inline-flex items-center justify-center"
                    >
                      <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                      Download
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Info section */}
            <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">
                🔒 File Access Information
              </h3>
              <div className="text-blue-700 space-y-2">
                <p>• <strong>Public files:</strong> Accessible to all registered users</p>
                <p>• <strong>Private files:</strong> Only accessible to the uploader and administrators</p>
                <p>• <strong>File types supported:</strong> PDF, DOC, DOCX, JPG, JPEG, PNG, TXT</p>
                <p>• <strong>Maximum file size:</strong> 50MB per file</p>
                <p>• Files are stored securely and encrypted</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default Downloads;