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

type AccentName = 'block' | 'approval' | 'proof' | 'memory' | 'datahub';

export type StoryShot = {
  id?: string;
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
  accent?: AccentName | string;
  metric?: string;
  bullets?: string[];
  objectPosition?: string;
  zoom?: number;
  fit?: 'cover' | 'contain';
  transition?: 'hard' | 'soft';
  chapter?: string;
};

const accentValue = (accent?: string) => {
  if (!accent) return palette.datahub;
  return palette[accent as keyof typeof palette] ?? accent;
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
        return <span key={`${part}-${index}`} style={{color: accent}}>{part}</span>;
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

const Header: React.FC<{shot: StoryShot}> = ({shot}) => {
  const accent = accentValue(shot.accent);
  return <div style={{position:'absolute',left:70,right:70,top:31,height:44,display:'flex',alignItems:'center',justifyContent:'space-between'}}>
    <div style={{display:'flex',alignItems:'center',gap:13}}>
      <div style={{width:30,height:30,borderRadius:9,background:accent,boxShadow:`0 0 24px ${accent}66`}} />
      <strong style={{fontSize:24,letterSpacing:-0.3}}>RepairPilot</strong>
      <span style={{fontSize:16,color:palette.muted}}>Incident-to-Repair Autopilot</span>
    </div>
    <div style={{display:'flex',alignItems:'center',gap:12}}>
      <span style={{fontFamily:monoFamily,fontSize:14,color:palette.muted,letterSpacing:1.3}}>{shot.chapter}</span>
      {shot.badge ? <span style={{color:accent,border:`1px solid ${accent}77`,background:`${accent}15`,borderRadius:999,padding:'7px 12px',fontSize:14,fontWeight:850,letterSpacing:1}}>{shot.badge}</span> : null}
    </div>
  </div>;
};

const VisualShot: React.FC<{shot: StoryShot}> = ({shot}) => {
  const {fps} = useVideoConfig();
  const accent = accentValue(shot.accent);
  const mediaStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: shot.fit ?? 'contain',
    objectPosition: shot.objectPosition ?? 'center top',
    transform: `scale(${shot.zoom ?? 1})`,
  };
  return <div style={{position:'absolute',left:70,right:70,top:94,height:824,overflow:'hidden',borderRadius:18,border:`1px solid ${palette.line}`,background:'#080d18',boxShadow:'0 26px 74px rgba(0,0,0,.44)'}}>
    <div style={{height:38,display:'flex',alignItems:'center',gap:7,padding:'0 14px',background:'#111827',borderBottom:`1px solid ${palette.line}`}}>
      {[palette.block,palette.approval,palette.proof].map((color)=><i key={color} style={{width:9,height:9,borderRadius:99,background:color,opacity:.9}} />)}
      <span style={{marginLeft:10,fontFamily:monoFamily,color:accent,fontSize:13,fontWeight:800,letterSpacing:1.1}}>{shot.headline}</span>
      {shot.subhead ? <span style={{marginLeft:'auto',color:palette.muted,fontSize:12}}>{shot.subhead}</span> : null}
    </div>
    <div style={{position:'absolute',inset:'38px 0 0',overflow:'hidden',display:'grid',placeItems:'center'}}>
      {shot.kind === 'video' && shot.video ? <Video
        src={staticFile(shot.video)}
        trimBefore={(shot.trimBeforeSeconds ?? 0) * fps}
        playbackRate={shot.playbackRate ?? 1}
        muted
        style={mediaStyle}
      /> : shot.image ? <Img src={staticFile(shot.image)} style={mediaStyle} /> : null}
    </div>
  </div>;
};

const GraphicShot: React.FC<{shot: StoryShot}> = ({shot}) => {
  const frame = useCurrentFrame();
  const accent = accentValue(shot.accent);
  // A soft shot may settle by ten pixels, but it is fully opaque from its first
  // frame. This retains restrained motion without the dark flash created by
  // fading the complete graphic layer from opacity zero.
  const settle = shot.transition === 'soft' ? interpolate(frame,[0,6],[10,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:Easing.bezier(.16,1,.3,1)}) : 0;
  return <div style={{position:'absolute',inset:'102px 90px 176px',display:'flex',flexDirection:'column',justifyContent:'center',alignItems:shot.kind === 'diagram' || shot.kind === 'receipt' ? 'stretch' : 'center',transform:`translateY(${settle}px)`}}>
    {shot.eyebrow ? <div style={{fontSize:20,fontWeight:850,color:accent,letterSpacing:3.5,marginBottom:20}}>{shot.eyebrow}</div> : null}
    {shot.metric ? <div style={{fontFamily:monoFamily,fontSize:112,fontWeight:900,color:accent,textShadow:`0 0 42px ${accent}4d`,lineHeight:.95}}>{shot.metric}</div> : null}
    <div style={{maxWidth:shot.kind === 'diagram' || shot.kind === 'receipt' ? 1510 : 1440,fontSize:shot.metric ? 56 : 84,lineHeight:1.03,fontWeight:900,letterSpacing:-3,textAlign:shot.kind === 'diagram' || shot.kind === 'receipt' ? 'left' : 'center'}}><HighlightedText text={shot.headline} /></div>
    {shot.subhead ? <div style={{maxWidth:1340,marginTop:23,fontSize:31,lineHeight:1.32,color:palette.muted,textAlign:shot.kind === 'diagram' || shot.kind === 'receipt' ? 'left' : 'center'}}>{shot.subhead}</div> : null}
    {shot.bullets ? <div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:16,marginTop:31}}>{shot.bullets.map((bullet,index)=><div key={bullet} style={{background:palette.card,border:`1px solid ${palette.line}`,borderRadius:14,padding:'17px 21px',fontFamily:monoFamily,fontSize:23,color:index===0?accent:palette.text}}><span style={{color:accent,marginRight:11}}>✓</span>{bullet}</div>)}</div> : null}
  </div>;
};

const Shot: React.FC<{shot: StoryShot}> = ({shot}) => {
  const isVisual = shot.kind === 'image' || shot.kind === 'video';
  return <AbsoluteFill style={{fontFamily,color:palette.text}}>
    <Grid />
    <Header shot={shot} />
    {isVisual ? <VisualShot shot={shot} /> : <GraphicShot shot={shot} />}
  </AbsoluteFill>;
};

export const StoryScene: React.FC<{shots: StoryShot[]; shotOffset?: number}> = ({shots}) => {
  let cursor = 0;
  return <AbsoluteFill>{shots.map((shot)=>{
    const from=cursor;
    cursor+=shot.duration;
    return <Sequence key={shot.id ?? `${from}`} from={from} durationInFrames={shot.duration} name={`Shot ${shot.id ?? ''}`}><Shot shot={shot} /></Sequence>;
  })}</AbsoluteFill>;
};
