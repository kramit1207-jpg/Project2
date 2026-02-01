import { TrendingUp, AlertTriangle } from 'lucide-react'
import Accordion from '../shared/Accordion'

function EngagementTab({ profileData }) {
  const analysis = profileData?.analysis
  const blueprint = analysis?.communication_blueprint

  if (!analysis) return null

  return (
    <div className="space-y-6">
      {/* Communication Blueprint */}
      {blueprint?.preferred_communication_style && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 shadow-lg border border-purple-200">
          <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
            <span>🎨</span>
            <span>Preferred Communication Style</span>
          </h2>
          <p className="text-gray-700 leading-relaxed">{blueprint.preferred_communication_style}</p>
        </div>
      )}

      {/* Two Column: Do's vs Don'ts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Strengths and Effective Approaches */}
        <div className="space-y-6">
          {/* Professional Strengths */}
          {analysis.professional_strengths && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 shadow-lg border border-green-200">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-6 h-6 text-green-600" />
                <h3 className="text-lg font-bold text-gray-800">Professional Strengths</h3>
              </div>
              <ul className="space-y-3">
                {analysis.professional_strengths.map((strength, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500 text-white flex items-center justify-center text-sm font-semibold mt-0.5">
                      {idx + 1}
                    </span>
                    <span className="text-sm text-gray-700 leading-relaxed">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Effective Approaches */}
          {blueprint?.effective_approaches && (
            <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-green-300">
              <h3 className="text-lg font-bold text-green-800 mb-4 flex items-center gap-2">
                <span>✅</span>
                <span>Effective Approaches</span>
              </h3>
              <ul className="space-y-3">
                {blueprint.effective_approaches.map((approach, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="flex-shrink-0 text-green-600 mt-1">•</span>
                    <span className="text-sm text-gray-700 leading-relaxed">{approach}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Right: Blind Spots and Approaches to Avoid */}
        <div className="space-y-6">
          {/* Approaches to Avoid */}
          {blueprint?.approaches_to_avoid && (
            <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-red-300">
              <h3 className="text-lg font-bold text-red-800 mb-4 flex items-center gap-2">
                <span>🚫</span>
                <span>Approaches to Avoid</span>
              </h3>
              <ul className="space-y-3">
                {blueprint.approaches_to_avoid.map((approach, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="flex-shrink-0 text-red-600 mt-1">•</span>
                    <span className="text-sm text-gray-700 leading-relaxed">{approach}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Potential Blind Spots */}
          {analysis.potential_blind_spots && (
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 shadow-lg border border-amber-200">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-6 h-6 text-amber-600" />
                <h3 className="text-lg font-bold text-gray-800">Potential Blind Spots</h3>
              </div>
              <ul className="space-y-3">
                {analysis.potential_blind_spots.map((blindSpot, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center text-sm font-semibold mt-0.5">
                      {idx + 1}
                    </span>
                    <span className="text-sm text-gray-700 leading-relaxed">{blindSpot}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Engagement Recommendations */}
      {analysis.engagement_recommendations && (
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Engagement Recommendations</h2>
          <div className="space-y-3">
            {analysis.engagement_recommendations.map((rec, idx) => {
              // Extract title from first sentence or use index
              const title = rec.split(':')[0] || `Recommendation ${idx + 1}`
              
              return (
                <Accordion key={idx} title={title} defaultOpen={idx === 0}>
                  <p className="text-sm text-gray-700 leading-relaxed">{rec}</p>
                </Accordion>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default EngagementTab
