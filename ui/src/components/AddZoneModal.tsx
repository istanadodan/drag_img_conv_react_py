import React, { useState, useEffect } from 'react';
import { Zone } from '../types';
import { createZone, updateZone } from '../api';
import '../styles/AddZoneModal.css';

interface AddZoneModalProps {
  isOpen: boolean;
  onClose: () => void;
  onZoneAdded: (zone: Zone) => void;
  editZone?: Zone | null;
  onZoneUpdated?: (zone: Zone) => void;
}

const AddZoneModal: React.FC<AddZoneModalProps> = ({ isOpen, onClose, onZoneAdded, editZone, onZoneUpdated }) => {
  const [id, setId] = useState('');
  const [label, setLabel] = useState('');
  const [description, setDescription] = useState('');
  const [quality, setQuality] = useState(90);
  const [color, setColor] = useState('#4CAF50');
  const [resizeMode, setResizeMode] = useState<'none' | 'ratio' | 'fixed'>('none');
  const [ratio, setRatio] = useState<number | ''>('');
  const [longSideLength, setLongSideLength] = useState<number | ''>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (editZone) {
      setId(editZone.id);
      setLabel(editZone.label);
      setDescription(editZone.description || '');
      setQuality(editZone.quality);
      setColor(editZone.color || '#4CAF50');

      if (editZone.resize) {
        setResizeMode(editZone.resize.mode as 'ratio' | 'fixed' || 'none');
        if (editZone.resize.ratio !== undefined) {
          setRatio(editZone.resize.ratio * 100);
        }
        if (editZone.resize.long_side_length !== undefined) {
          setLongSideLength(editZone.resize.long_side_length);
        }
      } else {
        setResizeMode('none');
        setRatio('');
        setLongSideLength('');
      }
    } else {
      resetForm();
    }
  }, [editZone, isOpen]);

  const resetForm = () => {
    setId('');
    setLabel('');
    setDescription('');
    setQuality(90);
    setColor('#4CAF50');
    setResizeMode('none');
    setRatio('');
    setLongSideLength('');
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!id.trim() || !label.trim() || !quality) {
      setError('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      let resize;
      if (resizeMode === 'ratio' && ratio) {
        resize = {
          mode: 'ratio',
          ratio: (ratio as number) / 100,
        };
      } else if (resizeMode === 'fixed' && longSideLength) {
        resize = {
          mode: 'fixed',
          long_side_length: longSideLength as number,
        };
      }

      const zoneData = {
        id,
        label,
        description: description || undefined,
        quality,
        color: color || undefined,
        resize,
      };

      if (editZone) {
        // Update existing zone
        const updatedZone = await updateZone(editZone.id, zoneData);
        if (onZoneUpdated) {
          onZoneUpdated(updatedZone);
        }
      } else {
        // Create new zone
        const newZone = await createZone(zoneData);
        onZoneAdded(newZone);
      }

      resetForm();
      onClose();
    } catch (err) {
      setError(editZone ? 'Failed to update zone. Please try again.' : 'Failed to create zone. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{editZone ? 'Edit Conversion Profile' : 'Add New Conversion Profile'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="modal-error">{error}</div>}

          <div className="form-group">
            <label htmlFor="id">Profile ID *</label>
            <input
              id="id"
              type="text"
              value={id}
              onChange={(e) => setId(e.target.value)}
              placeholder="e.g., custom-profile"
              disabled={isLoading || !!editZone}
            />
            <small>Unique identifier (alphanumeric, hyphens, underscores)</small>
          </div>

          <div className="form-group">
            <label htmlFor="label">Profile Name *</label>
            <input
              id="label"
              type="text"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g., Custom Quality"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <input
              id="description"
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="quality">Quality *</label>
            <div className="quality-input">
              <input
                id="quality"
                type="number"
                value={quality}
                onChange={(e) => setQuality(parseInt(e.target.value) || 90)}
                min="1"
                max="100"
                disabled={isLoading}
              />
              <span className="quality-value">{quality}%</span>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="color">Color</label>
            <div className="color-input">
              <input
                id="color"
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                disabled={isLoading}
              />
              <span className="color-preview" style={{ backgroundColor: color }}></span>
            </div>
          </div>

          <div className="form-group">
            <label>Resize Mode</label>
            <div className="resize-options">
              <label className="radio-group">
                <input
                  type="radio"
                  value="none"
                  checked={resizeMode === 'none'}
                  onChange={(e) => setResizeMode(e.target.value as 'none' | 'ratio' | 'fixed')}
                  disabled={isLoading}
                />
                <span>No Resize</span>
              </label>

              <label className="radio-group">
                <input
                  type="radio"
                  value="ratio"
                  checked={resizeMode === 'ratio'}
                  onChange={(e) => setResizeMode(e.target.value as 'none' | 'ratio' | 'fixed')}
                  disabled={isLoading}
                />
                <span>Ratio Scale %</span>
              </label>

              <label className="radio-group">
                <input
                  type="radio"
                  value="fixed"
                  checked={resizeMode === 'fixed'}
                  onChange={(e) => setResizeMode(e.target.value as 'none' | 'ratio' | 'fixed')}
                  disabled={isLoading}
                />
                <span>Max Length px</span>
              </label>
            </div>
          </div>

          {resizeMode === 'ratio' && (
            <div className="form-group">
              <label htmlFor="ratio">Scale (%)</label>
              <input
                id="ratio"
                type="number"
                value={ratio}
                onChange={(e) => setRatio(e.target.value ? parseInt(e.target.value) : '')}
                placeholder="e.g., 80"
                min="1"
                max="100"
                disabled={isLoading}
              />
            </div>
          )}

          {resizeMode === 'fixed' && (
            <div className="form-group">
              <label htmlFor="longSideLength">Max Length (px)</label>
              <input
                id="longSideLength"
                type="number"
                value={longSideLength}
                onChange={(e) => setLongSideLength(e.target.value ? parseInt(e.target.value) : '')}
                placeholder="e.g., 1920"
                min="10"
                max="8000"
                disabled={isLoading}
              />
            </div>
          )}

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
            >
              {editZone ? (isLoading ? 'Updating...' : 'Update Profile') : (isLoading ? 'Creating...' : 'Create Profile')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddZoneModal;
