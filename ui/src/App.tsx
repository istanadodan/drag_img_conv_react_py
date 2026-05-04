import React, { useState, useEffect } from 'react';
import { Zone, Job } from './types';
import { getZones, deleteZone } from './api';
import DropZone from './components/DropZone';
import AddZoneModal from './components/AddZoneModal';
import JobList from './components/JobList';
import './styles/App.css';

const App: React.FC = () => {
  const [zones, setZones] = useState<Zone[]>([]);
  const [jobs, setJobs] = useState<Map<string, Job>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddZoneModal, setShowAddZoneModal] = useState(false);
  const [editingZone, setEditingZone] = useState<Zone | null>(null);

  useEffect(() => {
    const loadZones = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const fetchedZones = await getZones();
        setZones(fetchedZones);
      } catch (err) {
        console.error('Failed to load zones:', err);
        setError('Failed to load zones. Please refresh the page.');
      } finally {
        setIsLoading(false);
      }
    };

    loadZones();
  }, []);

  const handleJobCreated = (job: Job) => {
    setJobs((prevJobs) => {
      const newJobs = new Map(prevJobs);
      newJobs.set(job.job_id, job);
      return newJobs;
    });
  };

  const handleJobUpdate = (updatedJob: Job) => {
    setJobs((prevJobs) => {
      const newJobs = new Map(prevJobs);
      newJobs.set(updatedJob.job_id, updatedJob);
      return newJobs;
    });
  };

  const handleJobRemove = (jobId: string) => {
    setJobs((prevJobs) => {
      const newJobs = new Map(prevJobs);
      newJobs.delete(jobId);
      return newJobs;
    });
  };

  const handleZoneAdded = (newZone: Zone) => {
    setZones((prevZones) => [...prevZones, newZone]);
  };

  const handleZoneClick = (zone: Zone) => {
    setEditingZone(zone);
    setShowAddZoneModal(true);
  };

  const handleZoneUpdated = (updatedZone: Zone) => {
    setZones((prevZones) =>
      prevZones.map((z) => (z.id === updatedZone.id ? updatedZone : z))
    );
    setEditingZone(null);
  };

  const handleZoneDelete = async (zoneId: string) => {
    try {
      await deleteZone(zoneId);
      setZones((prevZones) => prevZones.filter((z) => z.id !== zoneId));
    } catch (err) {
      console.error('Failed to delete zone:', err);
      alert('Failed to delete profile. Please try again.');
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">HEIC to JPG Converter</h1>
          <p className="app-subtitle">Drag and drop HEIC images to convert. Choose quality profile.</p>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span>{error}</span>
          </div>
        )}

        {isLoading ? (
          <div className="loading-container">
            <div className="spinner" />
            <p>Loading zones...</p>
          </div>
        ) : zones.length === 0 ? (
          <div className="error-container">
            <p>No zones available. Please check your server configuration.</p>
          </div>
        ) : (
          <>
            <section className="zones-section">
              <div className="section-header">
                <h2 className="section-title">Conversion Profiles</h2>
                <button
                  className="btn-add-zone"
                  onClick={() => setShowAddZoneModal(true)}
                >
                  + Add Profile
                </button>
              </div>
              <div className="zones-grid">
                {zones.map((zone) => (
                  <DropZone
                    key={zone.id}
                    zone={zone}
                    onJobCreated={handleJobCreated}
                    onZoneClick={handleZoneClick}
                    onZoneDelete={handleZoneDelete}
                  />
                ))}
              </div>
            </section>

            {jobs.size > 0 && (
              <section className="jobs-section">
                <h2 className="section-title">Conversion Jobs</h2>
                <JobList
                  jobs={jobs}
                  onJobUpdate={handleJobUpdate}
                  onJobRemove={handleJobRemove}
                />
              </section>
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 HEIC to JPG Converter. All rights reserved.</p>
      </footer>

      <AddZoneModal
        isOpen={showAddZoneModal}
        onClose={() => {
          setShowAddZoneModal(false);
          setEditingZone(null);
        }}
        onZoneAdded={handleZoneAdded}
        editZone={editingZone}
        onZoneUpdated={handleZoneUpdated}
      />
    </div>
  );
};

export default App;
