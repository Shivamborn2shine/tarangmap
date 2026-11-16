import { useState } from 'react';
import { Building2, Laptop, MapPin, Smartphone, Wifi, X } from 'lucide-react';

interface SurveyWizardModalProps {
  open: boolean;
  hasWindowsCollector: boolean;
  onClose: () => void;
  onStart: (config: {
    sessionName: string;
    mapMode: 'indoor' | 'outdoor';
    measureWhat: 'wifi' | 'cellular' | 'both';
    roomLabel: string;
  }) => void;
}

export function SurveyWizardModal({
  open,
  hasWindowsCollector,
  onClose,
  onStart,
}: SurveyWizardModalProps) {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [mapMode, setMapMode] = useState<'indoor' | 'outdoor'>('indoor');
  const [measureWhat, setMeasureWhat] = useState<'wifi' | 'cellular' | 'both'>('wifi');
  const [sessionName, setSessionName] = useState('Living Room & Study Check');
  const [roomLabel, setRoomLabel] = useState('Living Room');

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-[#102A43]/40 p-0 sm:items-center sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="wizard-title"
    >
      <div className="w-full max-w-lg rounded-t-2xl border border-[#D9E2EC] bg-white p-6 shadow-xl sm:rounded-2xl">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[#087F8C]">
              Step {step} of 3
            </p>
            <h2 id="wizard-title" className="mt-0.5 text-xl font-semibold text-[#102A43]">
              {step === 1 && 'Where are you surveying?'}
              {step === 2 && 'What should TARANG measure?'}
              {step === 3 && 'Name & starting point'}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close setup wizard"
            className="flex h-11 w-11 items-center justify-center rounded-xl text-[#486581] hover:bg-[#F0F4F8]"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-5">
          {step === 1 && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={() => setMapMode('indoor')}
                className={`flex min-h-[120px] flex-col items-start justify-between rounded-2xl border-2 p-4 text-left transition ${
                  mapMode === 'indoor'
                    ? 'border-[#087F8C] bg-[#E6F6F7]/50'
                    : 'border-[#D9E2EC] bg-white hover:border-[#9FB3C8]'
                }`}
              >
                <Building2 className="h-7 w-7 text-[#087F8C]" />
                <div>
                  <div className="font-semibold text-[#102A43]">Indoor Floor Plan</div>
                  <p className="mt-1 text-xs text-[#486581]">
                    Tap rooms as you walk. Honest manual position — no fake indoor GPS.
                  </p>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setMapMode('outdoor')}
                className={`flex min-h-[120px] flex-col items-start justify-between rounded-2xl border-2 p-4 text-left transition ${
                  mapMode === 'outdoor'
                    ? 'border-[#087F8C] bg-[#E6F6F7]/50'
                    : 'border-[#D9E2EC] bg-white hover:border-[#9FB3C8]'
                }`}
              >
                <MapPin className="h-7 w-7 text-[#3978CF]" />
                <div>
                  <div className="font-semibold text-[#102A43]">Outdoor GPS Walk</div>
                  <p className="mt-1 text-xs text-[#486581]">
                    Tags readings with GPS coordinates and +/- accuracy radius.
                  </p>
                </div>
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-3">
              <button
                type="button"
                onClick={() => setMeasureWhat('wifi')}
                className={`flex w-full items-center gap-4 rounded-2xl border-2 p-4 text-left transition ${
                  measureWhat === 'wifi'
                    ? 'border-[#087F8C] bg-[#E6F6F7]/50'
                    : 'border-[#D9E2EC] bg-white'
                }`}
              >
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#E6F6F7] text-[#087F8C]">
                  <Wifi className="h-6 w-6" />
                </div>
                <div>
                  <div className="font-semibold text-[#102A43]">Wi-Fi Signal</div>
                  <div className="text-xs text-[#486581]">
                    {hasWindowsCollector
                      ? 'Live Windows WLAN adapter ready (Signal quality %, band, channel).'
                      : 'Measures Wi-Fi RSSI / quality %, band, and channel.'}
                  </div>
                </div>
              </button>

              <button
                type="button"
                disabled={hasWindowsCollector}
                onClick={() => setMeasureWhat('both')}
                className={`flex w-full items-center gap-4 rounded-2xl border-2 p-4 text-left transition ${
                  hasWindowsCollector
                    ? 'cursor-not-allowed border-[#E2E8F0] bg-[#F8FAFC] opacity-65'
                    : measureWhat === 'both'
                    ? 'border-[#087F8C] bg-[#E6F6F7]/50'
                    : 'border-[#D9E2EC] bg-white'
                }`}
              >
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#EAF2FC] text-[#3978CF]">
                  {hasWindowsCollector ? <Laptop className="h-6 w-6" /> : <Smartphone className="h-6 w-6" />}
                </div>
                <div>
                  <div className="font-semibold text-[#102A43]">Wi-Fi + Cellular (LTE / 5G)</div>
                  <div className="text-xs text-[#486581]">
                    {hasWindowsCollector
                      ? 'Unavailable on Windows laptop collector — cellular radio telemetry requires Android.'
                      : 'Android handset mode: collects Wi-Fi RSSI and LTE/5G RSRP where permitted.'}
                  </div>
                </div>
              </button>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#102A43]" htmlFor="survey-name">
                  Survey session name
                </label>
                <input
                  id="survey-name"
                  type="text"
                  value={sessionName}
                  onChange={(e) => setSessionName(e.target.value)}
                  className="mt-1.5 w-full rounded-xl border border-[#CBD5E1] px-3.5 py-2.5 text-sm text-[#102A43]"
                />
              </div>

              {mapMode === 'indoor' && (
                <div>
                  <label className="block text-sm font-medium text-[#102A43]" htmlFor="start-room">
                    Starting room
                  </label>
                  <select
                    id="start-room"
                    value={roomLabel}
                    onChange={(e) => setRoomLabel(e.target.value)}
                    className="mt-1.5 w-full rounded-xl border border-[#CBD5E1] bg-white px-3.5 py-2.5 text-sm text-[#102A43]"
                  >
                    <option>Living Room</option>
                    <option>Study</option>
                    <option>Hallway</option>
                    <option>Kitchen &amp; Dining</option>
                    <option>Master Bedroom</option>
                    <option>Balcony</option>
                  </select>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="mt-6 flex items-center justify-between gap-3">
          {step > 1 ? (
            <button
              type="button"
              onClick={() => setStep((s) => (s === 3 ? 2 : 1))}
              className="min-h-[44px] rounded-xl border border-[#CBD5E1] px-4 text-sm font-medium text-[#334E68] hover:bg-[#F0F4F8]"
            >
              Back
            </button>
          ) : (
            <div />
          )}

          {step < 3 ? (
            <button
              type="button"
              onClick={() => setStep((s) => (s === 1 ? 2 : 3))}
              className="min-h-[44px] rounded-xl bg-[#087F8C] px-6 text-sm font-semibold text-white hover:bg-[#066974]"
            >
              Continue
            </button>
          ) : (
            <button
              type="button"
              onClick={() => {
                onStart({ sessionName: sessionName.trim() || 'New Survey', mapMode, measureWhat, roomLabel });
                setStep(1);
              }}
              className="min-h-[44px] rounded-xl bg-[#087F8C] px-6 text-sm font-semibold text-white hover:bg-[#066974]"
            >
              Start Survey
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
