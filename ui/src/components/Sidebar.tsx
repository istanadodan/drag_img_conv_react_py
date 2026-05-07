import React, { useState, useEffect } from 'react';
import '../styles/Sidebar.css';

interface SidebarProps {
  defaultBasePath: string;
  onBasePathChange: (path: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ defaultBasePath, onBasePathChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [basePath, setBasePath] = useState(defaultBasePath);
  const [tempPath, setTempPath] = useState(defaultBasePath);

  useEffect(() => {
    setBasePath(defaultBasePath);
    setTempPath(defaultBasePath);
  }, [defaultBasePath]);

  const handleSelectFolder = async () => {
    try {
      if ((window as any).showDirectoryPicker) {
        const dirHandle = await (window as any).showDirectoryPicker();
        setTempPath(dirHandle.name);
      } else {
        alert('File System Access API not supported in this browser');
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Folder selection error:', err);
      }
    }
  };

  const handleSave = () => {
    setBasePath(tempPath);
    onBasePathChange(tempPath);
  };

  const handleReset = () => {
    setTempPath(basePath);
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <button
        className={`sidebar-toggle ${isOpen ? 'active' : ''}`}
        onClick={toggleSidebar}
        title={isOpen ? 'Hide sidebar' : 'Show sidebar'}
        aria-label="Toggle sidebar"
      >
        <span className="hamburger">
          <span className="line line-1"></span>
          <span className="line line-2"></span>
          <span className="line line-3"></span>
        </span>
      </button>

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Settings</h2>
          <button
            className="sidebar-close"
            onClick={toggleSidebar}
            title="Close sidebar"
          >
            ✕
          </button>
        </div>

        <div className="sidebar-content">
          <div className="settings-section">
            <h3>Base Directory</h3>
            <p className="setting-description">
              Set a default base directory for saving converted files.
            </p>

            <div className="setting-input-group">
              <label>Base Path</label>
              <div className="path-input-wrapper">
                <input
                  type="text"
                  value={tempPath}
                  onChange={(e) => setTempPath(e.target.value)}
                  placeholder="/mPictures/Album"
                  className="path-input"
                />
                <button
                  className="btn-browse-folder"
                  onClick={handleSelectFolder}
                  title="Select folder"
                >
                  📁
                </button>
              </div>
              <small>Current: {basePath}</small>
            </div>

            <div className="button-group">
              <button
                className="btn-save"
                onClick={handleSave}
              >
                Save
              </button>
              <button
                className="btn-cancel"
                onClick={handleReset}
              >
                Cancel
              </button>
            </div>
          </div>

          <div className="settings-section info-section">
            <h3>Info</h3>
            <p>
              When you drag and drop files, you can select a folder to save the converted files.
              The base directory setting is used as a prefix for all uploads.
            </p>
          </div>
        </div>
      </aside>

      {isOpen && <div className="sidebar-overlay" onClick={toggleSidebar} />}
    </>
  );
};

export default Sidebar;
