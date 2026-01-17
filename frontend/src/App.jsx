import { useState } from 'react'
import axios from 'axios'
import SearchInput from './components/SearchInput'
import Dashboard from './components/Dashboard'
import LoadingState from './components/LoadingState'
import { AlertCircle, X } from 'lucide-react'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [rawScores, setRawScores] = useState(null)
  const [error, setError] = useState(null)

  const handleSearch = async (linkedinUrl) => {
    setIsLoading(true)
    setError(null)
    setAnalysis(null)
    setRawScores(null)

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/analyze`,
        { linkedin_url: linkedinUrl },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 120000, // 2 minutes timeout for the long-running analysis
        }
      )

      if (response.data) {
        setAnalysis(response.data.analysis)
        setRawScores(response.data.raw_scores)
      }
    } catch (err) {
      let errorMessage = 'An error occurred while analyzing the profile.'
      
      if (err.response) {
        // Server responded with error status
        errorMessage = err.response.data?.detail || errorMessage
      } else if (err.request) {
        // Request made but no response
        errorMessage = 'Unable to connect to the server. Please ensure the backend is running.'
      } else {
        // Something else happened
        errorMessage = err.message || errorMessage
      }

      setError(errorMessage)
      console.error('Error analyzing profile:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDismissError = () => {
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
            InsightProfile
          </h1>
          <p className="text-gray-600 mt-1">AI-Powered Personality Analysis Dashboard</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <SearchInput onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start justify-between">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-800 mb-1">Error</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
            <button
              onClick={handleDismissError}
              className="text-red-600 hover:text-red-800 flex-shrink-0"
              aria-label="Dismiss error"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Loading State */}
        {isLoading && <LoadingState />}

        {/* Dashboard */}
        {!isLoading && analysis && rawScores && (
          <Dashboard analysis={analysis} rawScores={rawScores} />
        )}

        {/* Empty State */}
        {!isLoading && !analysis && !error && (
          <div className="text-center py-16">
            <div className="max-w-md mx-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-3">
                Get Started with Personality Analysis
              </h2>
              <p className="text-gray-600 mb-6">
                Enter a LinkedIn profile URL above to analyze personality traits, strengths, and areas for growth using AI-powered insights.
              </p>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-left">
                <p className="text-sm text-blue-800">
                  <strong>Example:</strong> linkedin.com/in/username
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600 text-sm">
            Powered by Humantic AI and Google Gemini
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
