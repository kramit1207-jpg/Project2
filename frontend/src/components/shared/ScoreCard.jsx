function ScoreCard({ title, value, subtitle, icon, className = '' }) {
  return (
    <div className={`bg-white rounded-lg p-4 shadow-md border border-gray-200 ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        {icon && <span className="text-2xl">{icon}</span>}
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
    </div>
  )
}

export default ScoreCard
