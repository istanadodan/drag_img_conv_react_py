import React, { useEffect, useState } from 'react';
import { Job, JobUpdate } from '../types';
import { connectJobWS, downloadFile, saveFileToLocal } from '../api';
import '../styles/JobItem.css';

interface JobItemProps {
  job: Job;
  onJobUpdate: (job: Job) => void;
  onJobRemove: (jobId: string) => void;
}

const JobItem: React.FC<JobItemProps> = ({ job, onJobUpdate, onJobRemove }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [isResultsExpanded, setIsResultsExpanded] = useState(false);

  useEffect(() => {
    const ws = connectJobWS(job.job_id, (update: JobUpdate) => {
      const updatedJob: Job = {
        ...job,
        done: update.done,
        total: update.total,
        state: update.state as 'pending' | 'running' | 'done',
        results: update.results
          ? update.results  // 작업 완료 시 전체 results
          : (update.latest
            ? [update.latest, ...job.results]  // 진행 중 최신 결과만
            : job.results)
      };
      onJobUpdate(updatedJob);
      console.log("connectJobWS: id=", job.job_id);
    });

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    setWsConnection(ws);

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [job.job_id]);

  const progress = job.total > 0 ? (job.done / job.total) * 100 : 0;
  const isComplete = job.state === 'done';

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'converted':
        return '#4CAF50';
      case 'skipped':
        return '#FF9800';
      case 'failed':
        return '#F44336';
      default:
        return '#999';
    }
  };

  const getStatusLabel = (status: string): string => {
    switch (status) {
      case 'converted':
        return 'Converted';
      case 'skipped':
        return 'Skipped';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  const handleSaveToLocal = async (filename: string) => {
    try {
      const blob = await downloadFile(job.job_id, filename);
      await saveFileToLocal(blob, filename);
      alert(`✅ File saved: ${filename}`);
    } catch (error) {
      console.error('Error saving file:', error);
      alert(`❌ Failed to save file: ${(error as Error).message}`);
    }
  };

  return (
    <div className={`job-item ${isComplete ? 'completed' : ''}`}>
      <div className="job-header">
        <h4 className="job-title">Job {job.job_id.substring(0, 8)}</h4>
        <div className="job-status-badge">
          <span
            className="connection-indicator"
            style={{
              backgroundColor: isConnected ? '#4CAF50' : '#F44336'
            }}
          />
          <span className="status-text">{job.state}</span>
        </div>
      </div>

      <div className="job-progress-section">
        <div className="progress-info">
          <span className="progress-text">
            {job.done} / {job.total} files
          </span>
          <span className="progress-percent">{Math.round(progress)}%</span>
        </div>
        <div className="progress-bar-container">
          <div
            className="progress-bar"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="job-results">
        <div className="results-header">
          <button
            className="results-toggle"
            onClick={() => setIsResultsExpanded(!isResultsExpanded)}
          >
            <span className="toggle-icon">{isResultsExpanded ? '▼' : '▶'}</span>
          </button>
          <h5 className="results-title">Results</h5>
        </div>
        {isResultsExpanded && (
          <>
            {job.results.length === 0 ? (
              <p className="no-results">Waiting for results...</p>
            ) : (
              <div className="results-list">
                {job.results.map((result, idx) => (
                  <div key={idx} className="result-item">
                    <div className="result-status">
                      <div
                        className="status-dot"
                        style={{ backgroundColor: getStatusColor(result.status) }}
                      />
                      <span className="result-filename">{result.file}</span>
                    </div>
                    <div className="result-details">
                      <span
                        className="result-status-label"
                        style={{ color: getStatusColor(result.status) }}
                      >
                        {getStatusLabel(result.status)}
                      </span>
                      {result.output && (
                        <div className="result-output-container">
                          <span className="result-output">{result.output}</span>
                          <button
                            className="save-local-button"
                            onClick={() => handleSaveToLocal(result.output!)}
                            title="Save to local directory"
                          >
                            💾 Save to Local
                          </button>
                        </div>
                      )}
                      {result.error && (
                        <span className="result-error">{result.error}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {isComplete && (
        <div className="job-actions">
          <button
            className="remove-button"
            onClick={() => onJobRemove(job.job_id)}
          >
            Remove
          </button>
        </div>
      )}
    </div>
  );
};

export default JobItem;
