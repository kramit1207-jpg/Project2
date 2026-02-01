function MetricBar({ label, score, maxScore = 10, level, percentile, interpretation, color = 'blue' }) {
  const percentage = (score / maxScore) * 100
  
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
    red: 'bg-red-500',
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-baseline">
        <span className="font-semibold text-gray-800">{label}</span>
        <span className="text-2xl font-bold text-gray-900">{score}</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full ${colorClasses[color] || colorClasses.blue} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-600">{level}</span>
        {percentile && <span className="text-gray-500">{percentile}%</span>}
      </div>
      
      {interpretation && (
        <p className="text-sm text-gray-600 leading-relaxed">{interpretation}</p>
      )}
    </div>
  )
}

export default MetricBar
