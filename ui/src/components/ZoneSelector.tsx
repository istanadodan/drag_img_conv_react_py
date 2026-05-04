import React from 'react';
import { Zone } from '../types';
import '../styles/ZoneSelector.css';

interface ZoneSelectorProps {
  zones: Zone[];
  selectedZoneId?: string;
  onSelectZone: (zone: Zone) => void;
}

const ZoneSelector: React.FC<ZoneSelectorProps> = ({
  zones,
  selectedZoneId,
  onSelectZone,
}) => {
  return (
    <div className="zone-selector-container">
      <div className="zone-selector-header">
        <h2>🎯 Select Conversion Profile</h2>
        <p>Choose the profile that best suits your needs</p>
      </div>

      <div className="zone-selector-grid">
        {zones.map((zone) => (
          <div
            key={zone.id}
            className={`zone-card-selector ${
              selectedZoneId === zone.id ? 'selected' : ''
            }`}
            style={zone.color ? { borderTopColor: zone.color } : {}}
            onClick={() => onSelectZone(zone)}
          >
            <div className="zone-icon">{zone.label.split(' ')[0]}</div>
            <h3 className="zone-title">{zone.label}</h3>
            {zone.description && (
              <p className="zone-description">{zone.description}</p>
            )}

            <div className="zone-specs">
              <div className="spec-item">
                <span className="spec-label">Quality</span>
                <span className="spec-value">{zone.quality}%</span>
              </div>
              {zone.resize && (
                <div className="spec-item">
                  <span className="spec-label">
                    {zone.resize.mode === 'ratio' ? 'Scale' : 'Max Size'}
                  </span>
                  <span className="spec-value">
                    {zone.resize.mode === 'ratio'
                      ? `${(zone.resize.ratio! * 100).toFixed(0)}%`
                      : `${zone.resize.long_side_length}px`}
                  </span>
                </div>
              )}
            </div>

            {selectedZoneId === zone.id && (
              <div className="zone-selected-badge">✓ Selected</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ZoneSelector;
