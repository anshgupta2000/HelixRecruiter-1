import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="app-header bg-white border-b px-4 py-3 flex items-center justify-between">
      <div className="flex items-center">
        <h1 className="text-xl font-bold">Helix AI</h1>
        <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
          3 Active Tasks
        </span>
      </div>
      
      <div className="header-actions">
        {/* Placeholder for user profile or other actions */}
        <button className="p-2 hover:bg-gray-100 rounded-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="1"></circle>
            <circle cx="19" cy="12" r="1"></circle>
            <circle cx="5" cy="12" r="1"></circle>
          </svg>
        </button>
      </div>
    </header>
  );
};

export default Header;
