import { Users, TrendingUp } from 'lucide-react'

function SocialTab({ profileData }) {
  const socialInsights = profileData?.professional_profile?.social_insights

  if (!socialInsights) return null

  const getIconForTopic = (label) => {
    const lowerLabel = label.toLowerCase()
    if (lowerLabel.includes('ai') || lowerLabel.includes('search')) return '🤖'
    if (lowerLabel.includes('leadership')) return '👔'
    if (lowerLabel.includes('product')) return '💻'
    if (lowerLabel.includes('ethics')) return '⚖️'
    if (lowerLabel.includes('generative')) return '🧠'
    return '📊'
  }

  return (
    <div className="space-y-6">
      {/* Engagement Metrics */}
      {socialInsights.engagement_metrics && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-blue-100">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-600" />
            <span>Engagement Metrics</span>
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {socialInsights.engagement_metrics.linkedin_followers && (
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <p className="text-sm font-semibold text-gray-600 mb-1">LinkedIn Followers</p>
                <p className="text-3xl font-bold text-blue-600">
                  {socialInsights.engagement_metrics.linkedin_followers.toLocaleString()}
                </p>
              </div>
            )}
            
            {socialInsights.engagement_metrics.social_activity_status && (
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <p className="text-sm font-semibold text-gray-600 mb-1">Activity Status</p>
                <p className="text-xl font-semibold text-gray-900 capitalize">
                  {socialInsights.engagement_metrics.social_activity_status}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Topics They Care About */}
      {socialInsights.topics_care_about && socialInsights.topics_care_about.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-800 mb-4">Topics They Care About</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {socialInsights.topics_care_about.map((topic, idx) => (
              <div
                key={idx}
                className="bg-white rounded-xl p-5 shadow-lg border border-gray-200 hover:border-blue-400 hover:shadow-xl transition-all"
              >
                <div className="flex items-start gap-3">
                  <span className="text-3xl flex-shrink-0">{getIconForTopic(topic.label)}</span>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 mb-2">{topic.label}</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">{topic.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Themes from Posts */}
      {socialInsights.recent_themes_from_posts && socialInsights.recent_themes_from_posts.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-green-600" />
            <span>Recent Themes from Posts</span>
          </h2>
          
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-gray-200"></div>
            
            <div className="space-y-4">
              {socialInsights.recent_themes_from_posts.map((theme, idx) => (
                <div key={idx} className="relative pl-8">
                  {/* Timeline dot */}
                  <div className="absolute left-0 w-4 h-4 rounded-full bg-green-500 border-2 border-white shadow-md"></div>
                  
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <p className="text-gray-700 leading-relaxed">{theme}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SocialTab
