import { MapPin, Clock, ExternalLink } from 'lucide-react'
import ScoreCard from './shared/ScoreCard'

function ProfileHeader({ profileData }) {
  const identity = profileData?.professional_profile?.identity
  const currentRole = profileData?.professional_profile?.current_role
  const oceanScores = profileData?.personality_scores?.ocean
  const workHistory = profileData?.professional_profile?.work_history
  const socialInsights = profileData?.professional_profile?.social_insights
  const totalExperienceYears = profileData?.professional_profile?.total_experience_years

  if (!identity) return null

  // Find top OCEAN score
  const topOceanTrait = oceanScores
    ? Object.entries(oceanScores).reduce((max, [key, value]) => 
        value.score > (max?.score || 0) ? { name: key, ...value } : max
      , null)
    : null

  // Use calculated experience from backend, fallback to 0 if not available
  const totalYears = totalExperienceYears || 0

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-blue-100 mb-6">
      {/* Top Row: Name and Location */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">{identity.name}</h2>
          {currentRole && (
            <div className="space-y-1">
              <p className="text-lg font-semibold text-gray-700">{currentRole.title}</p>
              <p className="text-md text-gray-600">{currentRole.organization}</p>
            </div>
          )}
        </div>
        
        <div className="flex flex-col gap-2 text-sm text-gray-600">
          {identity.location && (
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              <span>{identity.location}</span>
            </div>
          )}
          {identity.timezone && (
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{identity.timezone}</span>
            </div>
          )}
          {identity.linkedin && (
            <a
              href={identity.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              <span>LinkedIn Profile</span>
            </a>
          )}
        </div>
      </div>

      {/* Bottom Row: Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {topOceanTrait && (
          <ScoreCard
            title={topOceanTrait.name.charAt(0).toUpperCase() + topOceanTrait.name.slice(1)}
            value={topOceanTrait.score.toFixed(2)}
            subtitle={`${topOceanTrait.percentile}th percentile`}
            icon="🎯"
          />
        )}
        
        {totalYears > 0 && (
          <ScoreCard
            title="Experience"
            value={`${totalYears}+ Years`}
            subtitle="Professional career"
            icon="💼"
          />
        )}
        
        {socialInsights?.engagement_metrics?.linkedin_followers && (
          <ScoreCard
            title="LinkedIn Reach"
            value={socialInsights.engagement_metrics.linkedin_followers.toLocaleString()}
            subtitle="Followers"
            icon="👥"
          />
        )}
      </div>
    </div>
  )
}

export default ProfileHeader
