function TabNavigation({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'personality', label: 'Personality', icon: '🧠' },
    { id: 'communication', label: 'Communication', icon: '💬' },
    { id: 'engagement', label: 'Engagement', icon: '🎯' },
    { id: 'professional', label: 'Professional', icon: '💼' },
    { id: 'context', label: 'Context', icon: '🔄' },
    { id: 'social', label: 'Social', icon: '🌐' },
  ]

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-2 mb-6 overflow-x-auto">
      <div className="flex gap-2 min-w-max">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default TabNavigation
