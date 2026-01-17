import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown } from 'lucide-react'

function Dashboard({ analysis, rawScores }) {
  // Prepare data for radar chart
  const radarData = [
    {
      subject: 'Openness',
      value: rawScores?.openness || 50,
      fullMark: 100,
    },
    {
      subject: 'Conscientiousness',
      value: rawScores?.conscientiousness || 50,
      fullMark: 100,
    },
    {
      subject: 'Extraversion',
      value: rawScores?.extraversion || 50,
      fullMark: 100,
    },
    {
      subject: 'Agreeableness',
      value: rawScores?.agreeableness || 50,
      fullMark: 100,
    },
    {
      subject: 'Neuroticism',
      value: rawScores?.neuroticism || 50,
      fullMark: 100,
    },
  ]

  return (
    <div className="w-full space-y-8">
      {/* Summary Section */}
      {analysis?.summary && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-blue-100">
          <h2 className="text-xl font-bold text-gray-800 mb-3">Personality Summary</h2>
          <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
        </div>
      )}

      {/* Main Content Section - Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Radar Chart */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Personality Profile</h2>
          <div className="w-full h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
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

        {/* Right: Strengths and Weaknesses Cards */}
        <div className="space-y-6">
          {/* Strengths Card */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 shadow-lg border border-green-200">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-6 h-6 text-green-600" />
              <h2 className="text-xl font-bold text-gray-800">Strengths</h2>
            </div>
            {analysis?.strengths && analysis.strengths.length > 0 ? (
              <ul className="space-y-3">
                {analysis.strengths.map((strength, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 text-gray-700"
                  >
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500 text-white flex items-center justify-center text-sm font-semibold mt-0.5">
                      {index + 1}
                    </span>
                    <span className="leading-relaxed">{strength}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-600">No strengths data available</p>
            )}
          </div>

          {/* Weaknesses Card */}
          <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 shadow-lg border border-red-200">
            <div className="flex items-center gap-2 mb-4">
              <TrendingDown className="w-6 h-6 text-red-600" />
              <h2 className="text-xl font-bold text-gray-800">Areas for Growth</h2>
            </div>
            {analysis?.weaknesses && analysis.weaknesses.length > 0 ? (
              <ul className="space-y-3">
                {analysis.weaknesses.map((weakness, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 text-gray-700"
                  >
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center text-sm font-semibold mt-0.5">
                      {index + 1}
                    </span>
                    <span className="leading-relaxed">{weakness}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-600">No weaknesses data available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
