import { Briefcase, GraduationCap, Target, Award } from 'lucide-react'
import Badge from '../shared/Badge'

function ProfessionalTab({ profileData }) {
  const profile = profileData?.professional_profile
  const contextInsights = profileData?.analysis?.professional_context_insights

  if (!profile) return null

  return (
    <div className="space-y-6">
      {/* Headline Section */}
      {profile.identity?.headline && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-blue-100">
          <p className="text-lg text-gray-700 leading-relaxed">{profile.identity.headline}</p>
        </div>
      )}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Career Timeline (2 columns width) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Work History */}
          {profile.work_history && profile.work_history.length > 0 && (
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
              <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <Briefcase className="w-6 h-6 text-blue-600" />
                <span>Career Timeline</span>
              </h3>
              
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                
                <div className="space-y-6">
                  {profile.work_history.map((job, idx) => (
                    <div key={idx} className="relative pl-12">
                      {/* Timeline dot */}
                      <div className="absolute left-0 w-8 h-8 rounded-full bg-blue-500 border-4 border-white shadow-md flex items-center justify-center">
                        <div className="w-2 h-2 rounded-full bg-white"></div>
                      </div>
                      
                      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:border-blue-300 transition-colors">
                        <p className="font-bold text-gray-900 text-lg">{job.title}</p>
                        <p className="text-blue-600 font-semibold mt-1">{job.organization}</p>
                        <p className="text-sm text-gray-600 mt-2">{job.period}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Career Trajectory Analysis */}
          {contextInsights?.career_trajectory_analysis && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 shadow-lg border border-purple-200">
              <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
                <Target className="w-5 h-5 text-purple-600" />
                <span>Career Trajectory Analysis</span>
              </h3>
              <p className="text-gray-700 leading-relaxed">{contextInsights.career_trajectory_analysis}</p>
            </div>
          )}
        </div>

        {/* Right: Education & Skills */}
        <div className="space-y-6">
          {/* Education */}
          {profile.education && profile.education.length > 0 && (
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-green-600" />
                <span>Education</span>
              </h3>
              
              <div className="space-y-4">
                {profile.education.map((edu, idx) => (
                  <div key={idx} className="border-l-4 border-green-500 pl-4 py-2">
                    <p className="font-bold text-gray-900">{edu.institution}</p>
                    <p className="text-sm text-gray-700 mt-1">{edu.degree}</p>
                    <p className="text-xs text-gray-600 mt-1">
                      {edu.year || edu.period}
                      {edu.status && ` (${edu.status})`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skills */}
          {profile.skills && profile.skills.length > 0 && (
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
              <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-amber-600" />
                <span>Skills</span>
              </h3>
              
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill, idx) => (
                  <Badge key={idx} variant="primary" size="md">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Current Focus Areas */}
      {contextInsights?.current_focus_areas && (
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span>🎯</span>
            <span>Current Focus Areas</span>
          </h3>
          <div className="flex flex-wrap gap-3">
            {contextInsights.current_focus_areas.map((area, idx) => (
              <Badge key={idx} variant="success" size="lg">
                {area}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Expertise Domains */}
      {contextInsights?.expertise_domains && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 shadow-lg border border-indigo-200">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span>💼</span>
            <span>Expertise Domains</span>
          </h3>
          <div className="flex flex-wrap gap-3">
            {contextInsights.expertise_domains.map((domain, idx) => (
              <Badge key={idx} variant="primary" size="md">
                {domain}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Social Insights - Topics Care About */}
      {profile.social_insights?.topics_care_about && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {profile.social_insights.topics_care_about.map((topic, idx) => (
            <div key={idx} className="bg-white rounded-lg p-4 shadow-md border border-gray-200 hover:border-blue-400 transition-colors">
              <div className="flex items-start gap-3">
                <span className="text-2xl">
                  {topic.label.toLowerCase().includes('ai') ? '🤖' :
                   topic.label.toLowerCase().includes('leadership') ? '👔' :
                   topic.label.toLowerCase().includes('product') ? '💻' :
                   topic.label.toLowerCase().includes('ethics') ? '⚖️' : '📊'}
                </span>
                <div className="flex-1">
                  <p className="font-bold text-gray-900 mb-1">{topic.label}</p>
                  <p className="text-xs text-gray-600 leading-relaxed">{topic.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProfessionalTab
