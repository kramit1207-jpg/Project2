import { useState } from 'react'
import { Users, Briefcase, Target, AlertTriangle, Zap, Ban } from 'lucide-react'
import Badge from '../shared/Badge'
import MetricBar from '../shared/MetricBar'

function ContextTab({ profileData }) {
  const [activeView, setActiveView] = useState('sales')
  const contextInsights = profileData?.context_specific_insights

  if (!contextInsights) return null

  const renderSalesView = () => {
    const sales = contextInsights.for_sales
    if (!sales) return null

    return (
      <div className="space-y-6">
        {/* Decision Characteristics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Decision Drivers */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-blue-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              <span>Decision Drivers</span>
            </h3>
            
            {sales.decision_drivers && (
              <div className="space-y-3">
                <div className="bg-white rounded-lg p-4 border border-blue-300">
                  <p className="text-xs font-semibold text-blue-800 mb-1">PRIMARY</p>
                  <p className="text-gray-900 font-bold">{sales.decision_drivers.primary}</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-blue-300">
                  <p className="text-xs font-semibold text-blue-800 mb-1">SECONDARY</p>
                  <p className="text-gray-900 font-bold">{sales.decision_drivers.secondary}</p>
                </div>
              </div>
            )}
          </div>

          {/* Decision Characteristics */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-600" />
              <span>Decision Characteristics</span>
            </h3>
            
            <div className="space-y-4">
              {sales.risk_appetite && (
                <div className="border-l-4 border-amber-500 pl-4 py-2">
                  <p className="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    Risk Appetite
                  </p>
                  <p className="text-sm text-gray-600">{sales.risk_appetite}</p>
                </div>
              )}
              
              {sales.ability_to_say_no && (
                <div className="border-l-4 border-red-500 pl-4 py-2">
                  <p className="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
                    <Ban className="w-4 h-4 text-red-600" />
                    Ability to Say No
                  </p>
                  <p className="text-sm text-gray-600">{sales.ability_to_say_no}</p>
                </div>
              )}
              
              {sales.decision_speed && (
                <div className="border-l-4 border-green-500 pl-4 py-2">
                  <p className="text-sm font-semibold text-gray-700 mb-1 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-green-600" />
                    Decision Speed
                  </p>
                  <p className="text-sm text-gray-600">{sales.decision_speed}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Key Traits */}
        {sales.key_traits && (
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 shadow-lg border border-purple-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">🏆 Key Traits</h3>
            <div className="flex flex-wrap gap-3">
              {sales.key_traits.map((trait, idx) => (
                <Badge key={idx} variant="primary" size="lg">
                  {trait}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Engagement Tactics */}
        {sales.engagement_tactics && (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">💡 Engagement Tactics</h3>
            <ol className="space-y-3">
              {sales.engagement_tactics.map((tactic, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-7 h-7 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold">
                    {idx + 1}
                  </span>
                  <span className="text-gray-700 leading-relaxed flex-1">{tactic}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    )
  }

  const renderHiringView = () => {
    const hiring = contextInsights.for_hiring
    if (!hiring) return null

    return (
      <div className="space-y-6">
        {/* Behavioral Factors */}
        {hiring.behavioral_factors && (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">📊 Behavioral Factors</h3>
            <div className="space-y-6">
              {Object.entries(hiring.behavioral_factors).map(([key, value]) => (
                <div key={key}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-gray-800 capitalize">{key.replace(/_/g, ' ')}</span>
                    {value.priority === 1 && (
                      <Badge variant="warning" size="sm">
                        ⭐ Priority {value.priority}
                      </Badge>
                    )}
                  </div>
                  <MetricBar
                    label=""
                    score={value.score}
                    maxScore={10}
                    level={value.level}
                    color="purple"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Two Column: Motivators and Management */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Motivators */}
          {hiring.motivators && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 shadow-lg border border-green-200">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span>🎯</span>
                <span>Motivators</span>
              </h3>
              <ul className="space-y-3">
                {hiring.motivators.map((motivator, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="flex-shrink-0 text-green-600 mt-1">•</span>
                    <span className="text-sm text-gray-700 leading-relaxed">{motivator}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Management Style */}
          {hiring.management_style && (
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 shadow-lg border border-amber-200">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                <span>Management Insight</span>
              </h3>
              <p className="text-sm text-gray-700 leading-relaxed">{hiring.management_style}</p>
            </div>
          )}
        </div>

        {/* Ideal Pitch Elements */}
        {hiring.ideal_pitch_elements && (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">💼 Ideal Pitch Elements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {hiring.ideal_pitch_elements.map((element, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                  <span className="flex-shrink-0 text-green-600 text-xl">✅</span>
                  <span className="text-sm text-gray-700">{element}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* View Selector */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-2">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveView('sales')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all flex-1 ${
              activeView === 'sales'
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Users className="w-5 h-5" />
            <span>For Sales</span>
          </button>
          <button
            onClick={() => setActiveView('hiring')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all flex-1 ${
              activeView === 'hiring'
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Briefcase className="w-5 h-5" />
            <span>For Hiring</span>
          </button>
        </div>
      </div>

      {/* View Content */}
      {activeView === 'sales' && renderSalesView()}
      {activeView === 'hiring' && renderHiringView()}
    </div>
  )
}

export default ContextTab
