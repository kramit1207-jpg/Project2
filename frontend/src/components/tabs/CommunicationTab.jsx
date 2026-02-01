import { useState } from 'react'
import { Mail, Phone, Users, CheckCircle, XCircle } from 'lucide-react'
import CopyButton from '../shared/CopyButton'
import Badge from '../shared/Badge'

function CommunicationTab({ profileData }) {
  const [activeSubTab, setActiveSubTab] = useState('email')
  const playbook = profileData?.communication_playbook

  if (!playbook) return null

  const renderEmailTab = () => {
    const email = playbook.email
    if (!email) return null

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Advice Checklist */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Email Guidelines</h3>
          <div className="space-y-4">
            {email.advice && Object.entries(email.advice).map(([key, value]) => {
              const isPositive = value && !value.toString().toLowerCase().includes('no') && !value.toString().toLowerCase().includes('skip') && !value.toString().toLowerCase().includes('avoid')
              const Icon = isPositive ? CheckCircle : XCircle
              const iconColor = isPositive ? 'text-green-600' : 'text-red-600'
              
              return (
                <div key={key} className="flex items-start gap-3">
                  <Icon className={`w-5 h-5 ${iconColor} flex-shrink-0 mt-0.5`} />
                  <div className="flex-1">
                    <p className="font-semibold text-gray-700 text-sm">{key.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-gray-600">{value}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right: Example Template */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 shadow-lg border border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">Example Template</h3>
            {email.example_template && (
              <CopyButton text={`Subject: ${email.example_template.subject}\n\n${email.example_template.body}`} />
            )}
          </div>
          
          {email.example_template && (
            <div className="bg-white rounded-lg p-4 border border-blue-300">
              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-600 mb-1">Subject:</p>
                <p className="text-sm font-bold text-gray-900">{email.example_template.subject}</p>
              </div>
              <div className="border-t border-gray-200 pt-4">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                  {email.example_template.body}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  const renderColdCallTab = () => {
    const call = playbook.cold_calling
    if (!call) return null

    return (
      <div className="space-y-6">
        {/* Key Insights */}
        {call.insights && (
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-6 shadow-lg border border-amber-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <span>🎯</span>
              <span>Key Insights</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(call.insights).map(([key, value]) => (
                <div key={key} className="bg-white rounded-lg p-4 border border-amber-200">
                  <p className="font-semibold text-amber-900 text-sm mb-2">{key.replace(/_/g, ' ')}</p>
                  <p className="text-sm text-gray-700">{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Script Template */}
        {call.script_template && (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                <span>📝</span>
                <span>Script Template</span>
              </h3>
              <CopyButton text={Object.entries(call.script_template).map(([key, value]) => `${key.toUpperCase()}\n${value}`).join('\n\n')} />
            </div>
            
            <div className="space-y-4">
              {Object.entries(call.script_template).map(([key, value], idx) => (
                <div key={key} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs font-semibold">
                      {idx + 1}
                    </span>
                    <p className="font-bold text-gray-800 uppercase text-sm">{key}</p>
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed ml-8">{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  const renderMeetingTab = () => {
    const meeting = playbook.meeting_strategy
    if (!meeting) return null

    return (
      <div className="space-y-6">
        {/* What to Say */}
        {meeting.what_to_say && (
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 shadow-lg border border-green-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <CheckCircle className="w-6 h-6 text-green-600" />
              <span>What to Say</span>
            </h3>
            <ul className="space-y-3">
              {meeting.what_to_say.map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500 text-white flex items-center justify-center text-sm font-semibold mt-0.5">
                    ✓
                  </span>
                  <span className="text-gray-700 leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* What to Avoid */}
        {meeting.what_to_avoid && (
          <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 shadow-lg border border-red-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <XCircle className="w-6 h-6 text-red-600" />
              <span>What to Avoid</span>
            </h3>
            <ul className="space-y-3">
              {meeting.what_to_avoid.map((item, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-red-500 text-white flex items-center justify-center text-sm font-semibold mt-0.5">
                    ✗
                  </span>
                  <span className="text-gray-700 leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Personality Descriptors */}
        {meeting.personality_descriptors && (
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Users className="w-6 h-6 text-purple-600" />
              <span>Expect This Personality</span>
            </h3>
            <div className="flex flex-wrap gap-3">
              {meeting.personality_descriptors.map((descriptor, idx) => (
                <Badge key={idx} variant="primary" size="lg">
                  {descriptor}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Sub-Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-2">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveSubTab('email')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
              activeSubTab === 'email'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Mail className="w-4 h-4" />
            <span>Email</span>
          </button>
          <button
            onClick={() => setActiveSubTab('call')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
              activeSubTab === 'call'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Phone className="w-4 h-4" />
            <span>Cold Call</span>
          </button>
          <button
            onClick={() => setActiveSubTab('meeting')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all ${
              activeSubTab === 'meeting'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Meeting</span>
          </button>
        </div>
      </div>

      {/* Sub-Tab Content */}
      {activeSubTab === 'email' && renderEmailTab()}
      {activeSubTab === 'call' && renderColdCallTab()}
      {activeSubTab === 'meeting' && renderMeetingTab()}
    </div>
  )
}

export default CommunicationTab
