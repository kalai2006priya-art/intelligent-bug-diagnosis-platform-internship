import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { ProtectedRoute } from './components/ProtectedRoute';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { DashboardPage } from './pages/DashboardPage';
import { SubmitBugPage } from './pages/SubmitBugPage';
import { BugHistoryPage } from './pages/BugHistoryPage';
import { DiagnosisReportPage } from './pages/DiagnosisReportPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ProfilePage } from './pages/ProfilePage';

function AppContent() {
  const { isAuthenticated } = useAuth();
  const [currentRoute, setCurrentRoute] = useState(() => (
    localStorage.getItem('bug_platform_token') ? 'dashboard' : 'landing'
  ));
  const [selectedBugId, setSelectedBugId] = useState(null);

  const isWorkspaceRoute = [
    'dashboard',
    'submit-bug',
    'bug-history',
    'diagnosis-report',
    'analytics',
    'knowledge-base',
    'profile'
  ].includes(currentRoute);

  const renderContent = () => {
    switch (currentRoute) {
      case 'landing':
        return <LandingPage setCurrentRoute={setCurrentRoute} />;
      case 'login':
        return <LoginPage setCurrentRoute={setCurrentRoute} />;
      case 'signup':
        return <SignupPage setCurrentRoute={setCurrentRoute} />;
      case 'dashboard':
        return (
          <ProtectedRoute setCurrentRoute={setCurrentRoute}>
            <DashboardPage setCurrentRoute={setCurrentRoute} setSelectedBugId={setSelectedBugId} />
          </ProtectedRoute>
        );
      case 'submit-bug':
        return (
          <ProtectedRoute setCurrentRoute={setCurrentRoute}>
            <SubmitBugPage setCurrentRoute={setCurrentRoute} setSelectedBugId={setSelectedBugId} />
          </ProtectedRoute>
        );
      case 'bug-history':
        return (
          <ProtectedRoute setCurrentRoute={setCurrentRoute}>
            <BugHistoryPage setCurrentRoute={setCurrentRoute} setSelectedBugId={setSelectedBugId} />
          </ProtectedRoute>
        );
      case 'diagnosis-report':
        return (
          <ProtectedRoute setCurrentRoute={setCurrentRoute}>
            <DiagnosisReportPage bugId={selectedBugId} setCurrentRoute={setCurrentRoute} />
          </ProtectedRoute>
        );
      case 'analytics':
        return (
          <ProtectedRoute setCurrentRoute={setCurrentRoute}>
            <AnalyticsPage />
          </ProtectedRoute>
        );
      case 'knowledge-base':
        return (
          <ProtectedRoute setCurrentRoute={setCurrentRoute}>
            <KnowledgeBasePage />
          </ProtectedRoute>
        );
      case 'profile':
        return (
          <ProtectedRoute setCurrentRoute={setCurrentRoute}>
            <ProfilePage setCurrentRoute={setCurrentRoute} />
          </ProtectedRoute>
        );
      default:
        return <LandingPage setCurrentRoute={setCurrentRoute} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      <Navbar currentRoute={currentRoute} setCurrentRoute={setCurrentRoute} />

      {isWorkspaceRoute && isAuthenticated ? (
        <div className="flex-1 max-w-7xl w-full mx-auto flex">
          <Sidebar currentRoute={currentRoute} setCurrentRoute={setCurrentRoute} />
          <main className="flex-1 p-6 sm:p-8 overflow-y-auto">
            {renderContent()}
          </main>
        </div>
      ) : (
        <main className="flex-1">
          {renderContent()}
        </main>
      )}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
