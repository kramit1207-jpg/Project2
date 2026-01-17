import { useState } from 'react'
import { Search, AlertCircle } from 'lucide-react'

function SearchInput({ onSearch, isLoading }) {
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [error, setError] = useState('')

  const validateLinkedInUrl = (url) => {
    if (!url.trim()) {
      return 'Please enter a LinkedIn URL'
    }
    
    // Basic LinkedIn URL validation
    const linkedinPattern = /^(https?:\/\/)?(www\.)?(linkedin\.com\/in\/|linkedin\.com\/pub\/)[\w-]+\/?/
    if (!linkedinPattern.test(url)) {
      return 'Please enter a valid LinkedIn profile URL (e.g., linkedin.com/in/username)'
    }
    
    return ''
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const validationError = validateLinkedInUrl(linkedinUrl)
    
    if (validationError) {
      setError(validationError)
      return
    }

    setError('')
    onSearch(linkedinUrl.trim())
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-2">
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={linkedinUrl}
              onChange={(e) => {
                setLinkedinUrl(e.target.value)
                setError('')
              }}
              placeholder="Enter LinkedIn profile URL (e.g., linkedin.com/in/username)"
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 placeholder-gray-400"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold rounded-lg hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
          >
            {isLoading ? 'Analyzing...' : 'Analyze Profile'}
          </button>
        </div>
        {error && (
          <div className="flex items-center gap-2 text-red-600 text-sm">
            <AlertCircle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}
      </form>
    </div>
  )
}

export default SearchInput
