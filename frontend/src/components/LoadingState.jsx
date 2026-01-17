import { Loader2 } from 'lucide-react'

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
      <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
      <p className="text-lg font-medium text-gray-700">
        Analyzing Behavioral Patterns...
      </p>
      <p className="text-sm text-gray-500">
        This may take up to a minute
      </p>
    </div>
  )
}

export default LoadingState
