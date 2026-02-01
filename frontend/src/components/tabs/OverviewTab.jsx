import { ArrowRight } from 'lucide-react'
import Badge from '../shared/Badge'

function OverviewTab({ profileData, onTabChange }) {
  const analysis = profileData?.analysis
  const archetype = profileData?.personality_scores?.archetype
  const ocean = profileData?.personality_scores?.ocean
  const disc = profileData?.personality_scores?.disc

  if (!analysis) return null

  // Find top OCEAN score
  const topOceanTrait = ocean
    ? Object.entries(ocean).reduce((max, [key, value]) => 
        value.score > (max?.score || 0) ? { name: key, ...value } : max
      , null)
    : null

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      {analysis.executive_summary && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-blue-100">
          <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
            <span>📊</span>
            <span>Executive Summary</span>
          </h2>
          <p className="text-gray-700 leading-relaxed">{analysis.executive_summary}</p>
        </div>
      )}

      {/* Three Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Archetype Card */}
        {archetype && (
          <div className={`rounded-xl p-6 shadow-lg border-2 ${
            archetype.color === 'red' ? 'bg-red-50 border-red-300' :
            archetype.color === 'blue' ? 'bg-blue-50 border-blue-300' :
            archetype.color === 'green' ? 'bg-green-50 border-green-300' :
            archetype.color === 'yellow' ? 'bg-yellow-50 border-yellow-300' :
            'bg-gray-50 border-gray-300'
          }`}>
            <div className="text-center mb-4">
              <div className="text-5xl mb-3">🎯</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">{archetype.name}</h3>
              <Badge variant={archetype.color} size="lg">
                {archetype.color.toUpperCase()}
              </Badge>
            </div>
            
            <div className="space-y-2 mt-4">
              <p className="text-sm font-semibold text-gray-700">Primary Traits:</p>
              {archetype.primary_traits?.map((trait, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-gray-600">•</span>
                  <span className="text-sm text-gray-700">{trait}</span>
                </div>
              ))}
            </div>

            {archetype.description && (
              <div className="mt-4 pt-4 border-t border-gray-300">
                <p className="text-sm text-gray-600 leading-relaxed">{archetype.description}</p>
              </div>
            )}
          </div>
        )}

        {/* Key Metrics Card */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Key Metrics</h3>
          
          {/* OCEAN Top Score */}
          {topOceanTrait && (
            <div className="mb-6">
              <p className="text-sm font-semibold text-gray-600 mb-2">OCEAN Top Score</p>
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <p className="text-xl font-bold text-blue-900 capitalize">{topOceanTrait.name}</p>
                <p className="text-3xl font-bold text-blue-600 mt-1">{topOceanTrait.score.toFixed(2)}</p>
                <p className="text-sm text-blue-700 mt-1">{topOceanTrait.percentile}th percentile</p>
                <p className="text-xs text-gray-600 mt-2">{topOceanTrait.level}</p>
              </div>
            </div>
          )}

          {/* DISC Pattern */}
          {disc && (
            <div>
              <p className="text-sm font-semibold text-gray-600 mb-2">DISC Pattern</p>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">Dominance (D)</span>
                  <span className="font-bold text-gray-900">{disc.dominance?.score}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">Influence (I)</span>
                  <span className="font-bold text-gray-900">{disc.influence?.score}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">Steadiness (S)</span>
                  <span className="font-bold text-gray-900">{disc.steadiness?.score}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">Calculativeness (C)</span>
                  <span className="font-bold text-gray-900">{disc.calculativeness?.score}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Behavioral Signature Card */}
        {analysis.personality_interpretation?.behavioral_signature && (
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 shadow-lg border border-purple-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Behavioral Signature</h3>
            <div className="space-y-3">
              {analysis.personality_interpretation.behavioral_signature.map((signature, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-500 text-white flex items-center justify-center text-xs font-semibold mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="text-sm text-gray-700 leading-relaxed">{signature}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => onTabChange('communication')}
          className="flex items-center justify-between p-4 bg-white rounded-lg border-2 border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition-all group"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">💬</span>
            <span className="font-semibold text-gray-800">View Communication Playbook</span>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
        </button>

        <button
          onClick={() => onTabChange('engagement')}
          className="flex items-center justify-between p-4 bg-white rounded-lg border-2 border-gray-200 hover:border-green-400 hover:bg-green-50 transition-all group"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <span className="font-semibold text-gray-800">See Engagement Strategies</span>
          </div>
          <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-green-600 group-hover:translate-x-1 transition-all" />
        </button>
      </div>
    </div>
  )
}

export default OverviewTab
