import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from 'recharts'
import MetricBar from '../shared/MetricBar'

function PersonalityTab({ profileData }) {
  const ocean = profileData?.personality_scores?.ocean
  const disc = profileData?.personality_scores?.disc
  const archetype = profileData?.personality_scores?.archetype
  const interpretation = profileData?.analysis?.personality_interpretation

  if (!ocean || !disc) return null

  // Prepare OCEAN radar chart data
  const oceanRadarData = Object.entries(ocean).map(([key, value]) => ({
    subject: key.charAt(0).toUpperCase() + key.slice(1),
    value: value.percentile || 0,
    fullMark: 100,
  }))

  // Prepare DISC scatter data for quadrant visualization
  const discScatterData = [
    {
      x: disc.influence?.score || 0,
      y: disc.dominance?.score || 0,
      name: 'Current Position',
      color: '#ef4444'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: OCEAN Analysis */}
        <div className="space-y-6">
          {/* OCEAN Radar Chart */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Personality Profile (OCEAN)</h2>
            <div className="w-full h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={oceanRadarData}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ fill: '#374151', fontSize: 12, fontWeight: 'bold' }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 100]}
                    tick={{ fill: '#6b7280', fontSize: 10 }}
                    tickCount={6}
                  />
                  <Radar
                    name="Personality Scores"
                    dataKey="value"
                    stroke="#0ea5e9"
                    fill="#0ea5e9"
                    fillOpacity={0.6}
                    strokeWidth={2}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* OCEAN Scores Table */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">OCEAN Scores Breakdown</h3>
            <div className="space-y-6">
              {Object.entries(ocean).map(([key, value]) => (
                <MetricBar
                  key={key}
                  label={key.charAt(0).toUpperCase() + key.slice(1)}
                  score={value.score}
                  maxScore={10}
                  level={value.level}
                  percentile={value.percentile}
                  interpretation={value.interpretation}
                  color="blue"
                />
              ))}
            </div>
          </div>
        </div>

        {/* Right: DISC Analysis */}
        <div className="space-y-6">
          {/* DISC Quadrant */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h2 className="text-xl font-bold text-gray-800 mb-4">DISC Quadrant</h2>
            <div className="w-full h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    type="number" 
                    dataKey="x" 
                    name="Influence" 
                    domain={[0, 10]}
                    label={{ value: 'Influence (I)', position: 'bottom', offset: 0 }}
                  />
                  <YAxis 
                    type="number" 
                    dataKey="y" 
                    name="Dominance"
                    domain={[0, 10]}
                    label={{ value: 'Dominance (D)', angle: -90, position: 'left' }}
                  />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter name="DISC Profile" data={discScatterData} fill="#ef4444">
                    {discScatterData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="font-semibold text-gray-700">D: {disc.dominance?.score}</p>
                <p className="text-xs text-gray-600">{disc.dominance?.level}</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="font-semibold text-gray-700">I: {disc.influence?.score}</p>
                <p className="text-xs text-gray-600">{disc.influence?.level}</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="font-semibold text-gray-700">S: {disc.steadiness?.score}</p>
                <p className="text-xs text-gray-600">{disc.steadiness?.level}</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="font-semibold text-gray-700">C: {disc.calculativeness?.score}</p>
                <p className="text-xs text-gray-600">{disc.calculativeness?.level}</p>
              </div>
            </div>
          </div>

          {/* Archetype Deep Dive */}
          {archetype && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 shadow-lg border border-purple-200">
              <h3 className="text-lg font-bold text-gray-800 mb-4">Archetype Deep Dive</h3>
              
              <div className="mb-4">
                <p className="text-2xl font-bold text-purple-900">{archetype.name}</p>
                <p className="text-sm text-purple-700 mt-1">Group: {archetype.group}</p>
              </div>

              {archetype.description && (
                <div className="mb-4">
                  <p className="text-sm text-gray-700 leading-relaxed">{archetype.description}</p>
                </div>
              )}

              {interpretation?.disc_archetype_meaning && (
                <div className="mb-4 p-3 bg-white rounded-lg border border-purple-200">
                  <p className="text-xs font-semibold text-purple-800 mb-2">DISC Archetype Meaning</p>
                  <p className="text-sm text-gray-700 leading-relaxed">{interpretation.disc_archetype_meaning}</p>
                </div>
              )}

              {interpretation?.ocean_profile_narrative && (
                <div className="p-3 bg-white rounded-lg border border-purple-200">
                  <p className="text-xs font-semibold text-purple-800 mb-2">OCEAN Profile Narrative</p>
                  <p className="text-sm text-gray-700 leading-relaxed">{interpretation.ocean_profile_narrative}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PersonalityTab
