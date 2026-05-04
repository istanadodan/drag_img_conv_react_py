import React from 'react';
import { Job } from '../types';
import JobItem from './JobItem';
import '../styles/JobList.css';

interface JobListProps {
  jobs: Map<string, Job>;
  onJobUpdate: (job: Job) => void;
  onJobRemove: (jobId: string) => void;
}

const JobList: React.FC<JobListProps> = ({ jobs, onJobUpdate, onJobRemove }) => {
  const jobArray = Array.from(jobs.values());

  if (jobArray.length === 0) {
    return (
      <div className="job-list-empty">
        <div className="empty-state">
          <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" strokeWidth="2" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h8m-4-4v8" />
          </svg>
          <h3>No active jobs</h3>
          <p>Upload files from a zone to start converting</p>
        </div>
      </div>
    );
  }

  return (
    <div className="job-list">
      <div className="job-list-header">
        <h2>Conversion Jobs</h2>
        <span className="job-count">{jobArray.length} active</span>
      </div>
      <div className="job-list-container">
        {jobArray.map((job) => (
          <JobItem
            key={job.job_id}
            job={job}
            onJobUpdate={onJobUpdate}
            onJobRemove={onJobRemove}
          />
        ))}
      </div>
    </div>
  );
};

export default JobList;
