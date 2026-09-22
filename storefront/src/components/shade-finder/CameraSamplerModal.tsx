'use client';

import React, { useRef, useState, useCallback } from 'react';

interface CameraSamplerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onColorSampled: (hex: string) => void;
}

export const CameraSamplerModal: React.FC<CameraSamplerModalProps> = ({
  isOpen,
  onClose,
  onColorSampled
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [streamActive, setStreamActive] = useState(false);
  const [sampledColor, setSampledColor] = useState<string | null>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setStreamActive(true);
      }
    } catch (err) {
      console.error('WebCam access denied:', err);
    }
  };

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setStreamActive(false);
    }
  }, []);

  const captureFrameAndSample = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    // Sample center pixel (e.g. cheek/jawline area)
    const pixel = ctx.getImageData(canvas.width / 2, canvas.height / 2, 1, 1).data;
    const hex = `#${((1 << 24) + (pixel[0] << 16) + (pixel[1] << 8) + pixel[2]).toString(16).slice(1)}`;
    setSampledColor(hex);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-lg p-6 bg-white rounded-2xl shadow-2xl">
        <h3 className="text-lg font-bold text-gray-900">Live Camera Shade Matcher</h3>
        <p className="mt-1 text-sm text-gray-600">
          Position your jawline within the central viewfinder under natural lighting.
        </p>

        <div className="relative mt-4 aspect-video bg-neutral-900 rounded-xl overflow-hidden flex items-center justify-center">
          <video ref={videoRef} className="w-full h-full object-cover" autoPlay playsInline muted />
          <canvas ref={canvasRef} width={640} height={480} className="hidden" />

          {/* Central Target Reticle */}
          <div className="absolute w-16 h-16 border-2 border-dashed border-white rounded-full pointer-events-none animate-pulse" />
        </div>

        {sampledColor && (
          <div className="mt-4 flex items-center gap-3 p-3 bg-neutral-50 rounded-lg border border-neutral-200">
            <span className="w-7 h-7 rounded-full border shadow" style={{ backgroundColor: sampledColor }} />
            <span className="text-sm font-mono text-gray-800">Sampled: {sampledColor}</span>
          </div>
        )}

        <div className="mt-6 flex justify-end gap-3">
          {!streamActive ? (
            <button
              onClick={startCamera}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              Start Camera
            </button>
          ) : (
            <button
              onClick={captureFrameAndSample}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700"
            >
              Sample Skin Tone
            </button>
          )}

          <button
            onClick={() => {
              if (sampledColor) onColorSampled(sampledColor);
              stopCamera();
              onClose();
            }}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Apply & Close
          </button>
        </div>
      </div>
    </div>
  );
};
