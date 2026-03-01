'use client';

import { useState, useRef } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Download, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VideoPlayerProps {
  src: string;
  poster?: string;
  title?: string;
  className?: string;
}

export function VideoPlayer({ src, poster, title, className }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [showControls, setShowControls] = useState(true);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (playing) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setPlaying(!playing);
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !muted;
    setMuted(!muted);
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    const curr = videoRef.current.currentTime;
    const dur = videoRef.current.duration;
    setCurrentTime(curr);
    setDuration(dur);
    setProgress(dur ? (curr / dur) * 100 : 0);
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!videoRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    videoRef.current.currentTime = pct * videoRef.current.duration;
  };

  const handleEnded = () => setPlaying(false);

  const handleFullscreen = () => {
    videoRef.current?.requestFullscreen?.();
  };

  const handleRestart = () => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = 0;
    videoRef.current.play();
    setPlaying(true);
  };

  const formatTime = (s: number) => {
    if (!s || isNaN(s)) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  return (
    <div
      className={cn(
        'relative bg-black rounded-xl overflow-hidden group aspect-[9/16] max-w-sm mx-auto',
        className
      )}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => playing && setShowControls(false)}
    >
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        className="w-full h-full object-contain"
        onTimeUpdate={handleTimeUpdate}
        onEnded={handleEnded}
        onLoadedMetadata={handleTimeUpdate}
        playsInline
        onClick={togglePlay}
      />

      {/* Center play button overlay (when paused) */}
      {!playing && (
        <div
          className="absolute inset-0 flex items-center justify-center cursor-pointer bg-black/20"
          onClick={togglePlay}
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 text-black shadow-lg hover:scale-110 transition-transform">
            <Play className="h-8 w-8 ml-1" />
          </div>
        </div>
      )}

      {/* Bottom controls */}
      <div
        className={cn(
          'absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 pt-8 transition-opacity',
          showControls ? 'opacity-100' : 'opacity-0'
        )}
      >
        {/* Progress bar */}
        <div
          className="h-1.5 bg-white/20 rounded-full cursor-pointer mb-3 group/bar"
          onClick={handleSeek}
        >
          <div
            className="h-full bg-white rounded-full relative"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-white opacity-0 group-hover/bar:opacity-100 transition-opacity" />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button onClick={togglePlay} className="text-white hover:text-white/80">
              {playing ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            </button>
            <button onClick={handleRestart} className="text-white/70 hover:text-white">
              <RotateCcw className="h-4 w-4" />
            </button>
            <button onClick={toggleMute} className="text-white/70 hover:text-white">
              {muted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </button>
            <span className="text-xs text-white/70 tabular-nums">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={src}
              download={title || 'video.mp4'}
              className="text-white/70 hover:text-white"
              onClick={(e) => e.stopPropagation()}
            >
              <Download className="h-4 w-4" />
            </a>
            <button onClick={handleFullscreen} className="text-white/70 hover:text-white">
              <Maximize className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Title overlay */}
      {title && showControls && (
        <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/60 to-transparent p-3 pb-8">
          <p className="text-white text-sm font-medium truncate">{title}</p>
        </div>
      )}
    </div>
  );
}
