import React, { useState, useRef } from 'react';
import { Zone, Job } from '../types';
import { uploadFiles } from '../api';
import '../styles/DropZone.css';

interface DropZoneProps {
  zone: Zone;
  onJobCreated: (job: Job) => void;
  onZoneClick?: (zone: Zone) => void;
  onZoneDelete?: (zoneId: string) => void;
}

const DropZone: React.FC<DropZoneProps> = ({ zone, onJobCreated, onZoneClick, onZoneDelete }) => {
  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${zone.label}"?`)) {
      onZoneDelete?.(zone.id);
    }
  };
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    if (e.dataTransfer.types.includes('Files')) {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    if (e.dataTransfer.types.includes('Files')) {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
    }
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    if (e.dataTransfer.types.includes('Files')) {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (files.length === 0) return;

      await handleFiles(files);
    }
  };

  const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.currentTarget.files || []);
    if (files.length === 0) return;

    await handleFiles(files);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleFiles = async (files: File[]) => {
    setIsLoading(true);
    try {
      const response = await uploadFiles(zone.id, files, zone.resize);
      const job: Job = {
        job_id: response.job_id,
        zone_id: zone.id,
        quality: zone.quality,
        resize: zone.resize,
        total: response.total,
        done: 0,
        state: 'pending',
        results: []
      };
      onJobCreated(job);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="zone-card">
      <h3
        style={{
          cursor: 'pointer',
          backgroundColor: zone.color || '#f5f5f5',
          color: zone.color ? '#fff' : '#333',
          margin: '-8px -8px 2px -8px',
          padding: '6px 8px',
          borderRadius: '6px 6px 0 0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
        onClick={() => onZoneClick?.(zone)}
      >
        <span>{zone.label}</span>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleDelete();
          }}
          style={{
            background: 'none',
            border: 'none',
            color: zone.color ? '#fff' : '#999',
            cursor: 'pointer',
            fontSize: '16px',
            padding: '0 4px',
            opacity: 0.7,
            transition: 'opacity 0.2s',
          }}
          onMouseEnter={(e) => {
            (e.target as HTMLButtonElement).style.opacity = '1';
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLButtonElement).style.opacity = '0.7';
          }}
          title="Delete profile"
        >
          ✕
        </button>
      </h3>
      {zone.description && <p className="zone-description">{zone.description}</p>}
      <p className="quality-info">Quality: {zone.quality}</p>
      <p className="preset-resize-info" style={{ visibility: zone.resize ? 'visible' : 'hidden' }}>
        {zone.resize ? (
          <>Preset: {zone.resize.mode === 'ratio'
            ? `${(zone.resize.ratio! * 100).toFixed(0)}% scale`
            : `Max ${zone.resize.long_side_length}px`}</>
        ) : (
          'Preset: None'
        )}
      </p>

      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${isLoading ? 'loading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="drop-zone-content">
          <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
          <p className="drop-text">Drop files</p>
          <button
            className="file-input-label"
            onClick={handleBrowseClick}
            disabled={isLoading}
          >
            Browse
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".heic,.heif"
            onChange={handleInputChange}
            disabled={isLoading}
            className="file-input-hidden"
          />
        </div>
      </div>
    </div>
  );
};

export default DropZone;
