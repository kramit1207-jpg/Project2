import { useState } from 'react'
import ProfileHeader from './ProfileHeader'
import TabNavigation from './TabNavigation'
import OverviewTab from './tabs/OverviewTab'
import PersonalityTab from './tabs/PersonalityTab'
import CommunicationTab from './tabs/CommunicationTab'
import EngagementTab from './tabs/EngagementTab'
import ProfessionalTab from './tabs/ProfessionalTab'
import ContextTab from './tabs/ContextTab'
import SocialTab from './tabs/SocialTab'

function Dashboard({ profileData }) {
  const [activeTab, setActiveTab] = useState('overview')

  if (!profileData) return null

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab profileData={profileData} onTabChange={setActiveTab} />
      case 'personality':
        return <PersonalityTab profileData={profileData} />
      case 'communication':
        return <CommunicationTab profileData={profileData} />
      case 'engagement':
        return <EngagementTab profileData={profileData} />
      case 'professional':
        return <ProfessionalTab profileData={profileData} />
      case 'context':
        return <ContextTab profileData={profileData} />
      case 'social':
        return <SocialTab profileData={profileData} />
      default:
        return <OverviewTab profileData={profileData} onTabChange={setActiveTab} />
    }
  }

  return (
    <div className="w-full space-y-6">
      <ProfileHeader profileData={profileData} />
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="min-h-[400px]">
        {renderActiveTab()}
      </div>
    </div>
  )
}

export default Dashboard
