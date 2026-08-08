import {Video} from '@remotion/media';
import {
  AbsoluteFill,
  Easing,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {fontFamily, monoFamily, palette} from '../theme';

export type StoryShot = {
  duration: number;
  kind?: 'title' | 'image' | 'metric' | 'diagram' | 'receipt' | 'video';
  eyebrow?: string;
  headline: string;
  subhead?: string;
  image?: string;
  video?: string;
  trimBeforeSeconds?: number;
  playbackRate?: number;
  badge?: string;
  accent?: string;
  metric?: string;
  bullets?: string[];
  objectPosition?: string;
  zoom?: number;
};

const HighlightedText: React.FC<{text: string}> = ({text}) => {
  const parts = text.split(/(BLOCK|REPAIR|PROVE|REMEMBER|100\/100|14 tests|zero failures|LIVE|REAL)/gi);
  return (
    <>
      {parts.map((part, index) => {
        const normalized = part.toUpperCase();
        const accent =
          normalized === 'BLOCK'
            ? palette.block
            : normalized === 'REPAIR'
              ? palette.approval
              : normalized === 'PROVE' || normalized.includes('14 TESTS') || normalized.includes('ZERO FAILURES')
                ? palette.proof
                : normalized === 'REMEMBER'
                  ? palette.memory
                  : normalized === 'LIVE' || normalized === 'REAL' || normalized === '100/100'
                    ? palette.datahub
                    : undefined;
        return (
          <span key={`${part}-${index}`} style={{color: accent}}>
            {part}
          </span>
        );
      })}
    </>
  );
};

const Grid = () => (
  <AbsoluteFill
    style={{
      backgroundColor: palette.background,
      backgroundImage:
        'linear-gradient(rgba(59,130,246,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.045) 1px, transparent 1px)',
      backgroundSize: '48px 48px',
    }}
  />
);

const Shot: React.FC<{shot: StoryShot; index: number; duration: number}> = ({shot, index, duration}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const accent = shot.accent ?? palette.datahub;
  const reveal = interpolate(frame, [0, 10], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const scale = interpolate(frame, [0, Math.max(duration - 1, 1)], [shot.zoom ?? 1, (shot.zoom ?? 1) + 0.025], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const isVisual = shot.kind === 'image' || shot.kind === 'video';

  return (
    <AbsoluteFill style={{fontFamily, color: palette.text}}>
      <Grid />
      <div
        style={{
          position: 'absolute',
          left: 82,
          right: 82,
          top: 42,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          opacity: reveal,
        }}
      >
        <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
          <div
            style={{
              width: 30,
              height: 30,
              borderRadius: 9,
              background: accent,
              boxShadow: `0 0 26px ${accent}80`,
            }}
          />
          <span style={{fontWeight: 800, fontSize: 24, letterSpacing: 0.2}}>RepairPilot</span>
          <span style={{fontSize: 17, color: palette.muted}}>Incident-to-Repair Autopilot</span>
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
          {shot.badge ? (
            <span
              style={{
                color: accent,
                border: `1px solid ${accent}80`,
                background: `${accent}15`,
                borderRadius: 999,
                padding: '8px 14px',
                fontSize: 17,
                fontWeight: 800,
                letterSpacing: 1.2,
              }}
            >
              {shot.badge}
            </span>
          ) : null}
          <span style={{fontFamily: monoFamily, color: palette.muted, fontSize: 16}}>
            SHOT {String(index + 1).padStart(2, '0')}
          </span>
        </div>
      </div>

      {isVisual ? (
        <>
          <div
            style={{
              position: 'absolute',
              left: 90,
              right: 90,
              top: 126,
              height: 680,
              overflow: 'hidden',
              borderRadius: 24,
              border: `1px solid ${palette.line}`,
              background: '#080D18',
              boxShadow: '0 28px 80px rgba(0,0,0,0.45)',
              opacity: reveal,
            }}
          >
            <div
              style={{
                height: 42,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '0 18px',
                background: '#111827',
                borderBottom: `1px solid ${palette.line}`,
              }}
            >
              {[palette.block, palette.approval, palette.proof].map((color) => (
                <div key={color} style={{width: 11, height: 11, borderRadius: 99, background: color, opacity: 0.9}} />
              ))}
              <span style={{marginLeft: 12, fontFamily: monoFamily, color: palette.muted, fontSize: 14}}>
                VERIFIED LIVE CAPTURE
              </span>
            </div>
            <div style={{position: 'absolute', inset: '42px 0 0 0', overflow: 'hidden'}}>
              {shot.kind === 'video' && shot.video ? (
                <Video
                  src={staticFile(shot.video)}
                  trimBefore={(shot.trimBeforeSeconds ?? 0) * fps}
                  playbackRate={shot.playbackRate ?? 1}
                  muted
                  objectFit="cover"
                  style={{width: '100%', height: '100%', objectPosition: shot.objectPosition ?? 'center top', scale}}
                />
              ) : shot.image ? (
                <Img
                  src={staticFile(shot.image)}
                  style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: shot.objectPosition ?? 'center top', scale}}
                />
              ) : null}
            </div>
          </div>
          <div
            style={{
              position: 'absolute',
              left: 118,
              top: 700,
              maxWidth: 1350,
              padding: '18px 24px',
              background: 'rgba(11,16,32,0.91)',
              borderLeft: `5px solid ${accent}`,
              borderRadius: 12,
              opacity: reveal,
              translate: `${interpolate(frame, [0, 10], [24, 0], {extrapolateRight: 'clamp'})}px 0`,
            }}
          >
            <div style={{fontSize: 40, lineHeight: 1.08, fontWeight: 850}}>
              <HighlightedText text={shot.headline} />
            </div>
            {shot.subhead ? <div style={{fontSize: 21, marginTop: 7, color: palette.muted}}>{shot.subhead}</div> : null}
          </div>
        </>
      ) : (
        <div
          style={{
            position: 'absolute',
            inset: '112px 90px 180px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: shot.kind === 'diagram' || shot.kind === 'receipt' ? 'stretch' : 'center',
            opacity: reveal,
            translate: `0 ${interpolate(frame, [0, 12], [30, 0], {extrapolateRight: 'clamp'})}px`,
          }}
        >
          {shot.eyebrow ? (
            <div style={{fontSize: 22, fontWeight: 800, color: accent, letterSpacing: 4, marginBottom: 24}}>{shot.eyebrow}</div>
          ) : null}
          {shot.metric ? (
            <div style={{fontFamily: monoFamily, fontSize: 122, fontWeight: 900, color: accent, textShadow: `0 0 44px ${accent}55`}}>{shot.metric}</div>
          ) : null}
          <div
            style={{
              maxWidth: shot.kind === 'diagram' || shot.kind === 'receipt' ? 1520 : 1380,
              fontSize: shot.metric ? 58 : 96,
              lineHeight: 1.02,
              fontWeight: 900,
              letterSpacing: -3.5,
              textAlign: shot.kind === 'diagram' || shot.kind === 'receipt' ? 'left' : 'center',
            }}
          >
            <HighlightedText text={shot.headline} />
          </div>
          {shot.subhead ? (
            <div style={{maxWidth: 1320, marginTop: 26, fontSize: 34, lineHeight: 1.35, color: palette.muted, textAlign: shot.kind === 'diagram' || shot.kind === 'receipt' ? 'left' : 'center'}}>
              {shot.subhead}
            </div>
          ) : null}
          {shot.bullets ? (
            <div style={{display: 'grid', gridTemplateColumns: shot.bullets.length > 2 ? 'repeat(2, 1fr)' : '1fr', gap: 18, marginTop: 34}}>
              {shot.bullets.map((bullet, bulletIndex) => (
                <div key={bullet} style={{background: palette.card, border: `1px solid ${palette.line}`, borderRadius: 16, padding: '19px 24px', fontFamily: monoFamily, fontSize: 25, color: bulletIndex === 0 ? accent : palette.text}}>
                  <span style={{color: accent, marginRight: 12}}>✓</span>{bullet}
                </div>
              ))}
            </div>
          ) : null}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const StoryScene: React.FC<{shots: StoryShot[]; shotOffset: number}> = ({shots, shotOffset}) => {
  let cursor = 0;
  return (
    <AbsoluteFill>
      {shots.map((shot, index) => {
        const from = cursor;
        cursor += shot.duration;
        return (
          <Sequence key={`${shotOffset}-${index}`} from={from} durationInFrames={shot.duration} name={`Shot ${shotOffset + index}`}>
            <Shot shot={shot} index={shotOffset + index - 1} duration={shot.duration} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
