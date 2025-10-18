import React, { useState, useEffect } from 'react';
import { Upload, FileText, Calendar, DollarSign, Clock, CheckCircle, XCircle, Loader, Eye } from 'lucide-react';

const App = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [invoiceHistory, setInvoiceHistory] = useState([]);
  const [error, setError] = useState(null);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [activeTab, setActiveTab] = useState('upload');
  const [loading, setLoading] = useState(false);

  const API_BASE_URL = 'http://localhost:8000';

  // Fetch invoice history
  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/invoice/v1/?skip=0&limit=100`);
      const data = await response.json();
      if (data.status) {
        setInvoiceHistory(data.data || []);
      }
    } catch (err) {
      console.error('Error fetching invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
      const allowedExtensions = ['pdf', 'png', 'jpg', 'jpeg'];
      
      if (!allowedExtensions.includes(fileExtension)) {
        setError('Invalid file type. Only PDF, PNG, JPG, and JPEG are allowed.');
        return;
      }
      
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
      setExtractedData(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/invoice/v1/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.status) {
        setExtractedData(data.data);
        setFile(null);
        fetchInvoices();
        setActiveTab('results');
      } else {
        setError(data.message || 'Failed to extract invoice data');
      }
    } catch (err) {
      setError('Network error. Please ensure the backend server is running.');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const fakeEvent = { target: { files: [droppedFile] } };
      handleFileChange(fakeEvent);
    }
  };

  const viewInvoiceDetails = async (invoiceId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/invoice/v1/${invoiceId}`);
      const data = await response.json();
      if (data.status) {
        setSelectedInvoice(data.data);
        setActiveTab('details');
      }
    } catch (err) {
      console.error('Error fetching invoice details:', err);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return dateString;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Invoice Extractor</h1>
                <p className="text-sm text-gray-500">AI-Powered Invoice Data Extraction</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm">
              <div className="flex items-center space-x-1 text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span>LLM Powered</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 py-3 px-4 rounded-md font-medium transition-all ${
              activeTab === 'upload'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Upload className="w-5 h-5 inline-block mr-2" />
            Upload Invoice
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex-1 py-3 px-4 rounded-md font-medium transition-all ${
              activeTab === 'history'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Clock className="w-5 h-5 inline-block mr-2" />
            History ({invoiceHistory.length})
          </button>
          {(extractedData || selectedInvoice) && (
            <button
              onClick={() => setActiveTab(extractedData ? 'results' : 'details')}
              className={`flex-1 py-3 px-4 rounded-md font-medium transition-all ${
                activeTab === 'results' || activeTab === 'details'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Eye className="w-5 h-5 inline-block mr-2" />
              Details
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            {/* Upload Area */}
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className={`border-3 border-dashed rounded-xl p-12 text-center transition-all ${
                  file
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 hover:border-blue-400 bg-gray-50 hover:bg-blue-50'
                }`}
              >
                {!file ? (
                  <>
                    <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <h3 className="text-xl font-semibold text-gray-700 mb-2">
                      Drop your invoice here
                    </h3>
                    <p className="text-gray-500 mb-6">
                      or click to browse (PDF, PNG, JPG, JPEG - Max 10MB)
                    </p>
                    <label className="inline-block">
                      <span className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium cursor-pointer hover:shadow-lg transition-all">
                        Choose File
                      </span>
                      <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={handleFileChange}
                      />
                    </label>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
                    <h3 className="text-xl font-semibold text-gray-700 mb-2">
                      File Selected
                    </h3>
                    <p className="text-gray-600 mb-4 font-medium">{file.name}</p>
                    <p className="text-sm text-gray-500 mb-6">
                      Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <div className="flex justify-center space-x-4">
                      <button
                        onClick={handleUpload}
                        disabled={uploading}
                        className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {uploading ? (
                          <>
                            <Loader className="w-5 h-5 inline-block mr-2 animate-spin" />
                            Extracting...
                          </>
                        ) : (
                          <>
                            <Upload className="w-5 h-5 inline-block mr-2" />
                            Extract Data
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => setFile(null)}
                        className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-all"
                      >
                        Cancel
                      </button>
                    </div>
                  </>
                )}
              </div>

              {error && (
                <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                  <XCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-red-800">Error</h4>
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Instructions */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">How It Works</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-start space-x-3">
                  <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    1
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Upload Invoice</h4>
                    <p className="text-sm text-gray-600">
                      Drop or select your PDF/image file
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="bg-purple-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    2
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">AI Extraction</h4>
                    <p className="text-sm text-gray-600">
                      LLM analyzes and extracts data
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="bg-green-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    3
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">Get Results</h4>
                    <p className="text-sm text-gray-600">
                      View structured invoice data
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && extractedData && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Extracted Invoice Data</h2>
              <span className="px-4 py-2 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                Successfully Extracted
              </span>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                <div className="flex items-center mb-3">
                  <FileText className="w-6 h-6 text-blue-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Invoice Number</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {extractedData.invoice_number || 'Not Found'}
                </p>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                <div className="flex items-center mb-3">
                  <DollarSign className="w-6 h-6 text-green-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Total Amount</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(extractedData.amount)}
                </p>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
                <div className="flex items-center mb-3">
                  <Calendar className="w-6 h-6 text-purple-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Invoice Date</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatDate(extractedData.invoice_date)}
                </p>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 border border-orange-200">
                <div className="flex items-center mb-3">
                  <Clock className="w-6 h-6 text-orange-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Due Date</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatDate(extractedData.due_date)}
                </p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">File Name</p>
                  <p className="font-semibold text-gray-800">{extractedData.file_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Extraction Method</p>
                  <p className="font-semibold text-gray-800 capitalize">
                    {extractedData.extraction_method}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6 flex space-x-4">
              <button
                onClick={() => {
                  setExtractedData(null);
                  setActiveTab('upload');
                }}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all"
              >
                Extract Another Invoice
              </button>
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Invoice History</h2>

            {loading ? (
              <div className="text-center py-12">
                <Loader className="w-12 h-12 mx-auto text-blue-600 animate-spin mb-4" />
                <p className="text-gray-600">Loading invoices...</p>
              </div>
            ) : invoiceHistory.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-600">No invoices found. Upload your first invoice!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {invoiceHistory.map((invoice) => (
                  <div
                    key={invoice.id}
                    className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-all cursor-pointer"
                    onClick={() => viewInvoiceDetails(invoice.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="bg-gradient-to-br from-blue-500 to-purple-500 p-3 rounded-lg">
                          <FileText className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-800 text-lg">
                            {invoice.invoice_number || 'No Invoice Number'}
                          </h3>
                          <p className="text-sm text-gray-500">{invoice.file_name}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-6">
                        <div className="text-right">
                          <p className="text-sm text-gray-500">Amount</p>
                          <p className="font-bold text-gray-900">
                            {formatCurrency(invoice.amount)}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">Date</p>
                          <p className="font-semibold text-gray-900">
                            {formatDate(invoice.invoice_date)}
                          </p>
                        </div>
                        <Eye className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Details Tab */}
        {activeTab === 'details' && selectedInvoice && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Invoice Details</h2>
              <button
                onClick={() => {
                  setSelectedInvoice(null);
                  setActiveTab('history');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
              >
                Back to History
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                <div className="flex items-center mb-3">
                  <FileText className="w-6 h-6 text-blue-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Invoice Number</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {selectedInvoice.invoice_number || 'Not Found'}
                </p>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                <div className="flex items-center mb-3">
                  <DollarSign className="w-6 h-6 text-green-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Total Amount</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(selectedInvoice.amount)}
                </p>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
                <div className="flex items-center mb-3">
                  <Calendar className="w-6 h-6 text-purple-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Invoice Date</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatDate(selectedInvoice.invoice_date)}
                </p>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 border border-orange-200">
                <div className="flex items-center mb-3">
                  <Clock className="w-6 h-6 text-orange-600 mr-3" />
                  <h3 className="font-semibold text-gray-700">Due Date</h3>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {formatDate(selectedInvoice.due_date)}
                </p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">File Name</p>
                  <p className="font-semibold text-gray-800">{selectedInvoice.file_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Extraction Method</p>
                  <p className="font-semibold text-gray-800 capitalize">
                    {selectedInvoice.extraction_method}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Invoice ID</p>
                  <p className="font-mono text-xs text-gray-800">{selectedInvoice.id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Created At</p>
                  <p className="text-sm text-gray-800">
                    {new Date(selectedInvoice.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            Invoice Extractor • Powered by AI (Ollama) • Built with FastAPI & React
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;