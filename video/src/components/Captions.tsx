import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import captions from '../../public/data/captions.json';
import {fontFamily, palette} from '../theme';

type Caption = {
  text: string;
  startMs: number;
  endMs: number;
};

const KEYWORD = /(DataHub|MCP|BLOCK|RepairPilot|DeepSeek|dbt|GitHub|real|synthetic|Evidence Receipt|fourteen tests|zero failures)/gi;
const KEYWORD_HIGHLIGHT = /^(DataHub|MCP|BLOCK|RepairPilot|DeepSeek|dbt|GitHub|real|synthetic|Evidence Receipt|fourteen tests|zero failures)$/i;

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = (frame / fps) * 1000;
  const active = (captions as Caption[]).find((caption) => caption.startMs <= now && caption.endMs >= now);
  if (!active) return null;

  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 190,
          right: 190,
          bottom: 100,
          minHeight: 74,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '14px 28px',
          borderRadius: 18,
          background: 'rgba(7, 11, 23, 0.92)',
          border: `1px solid ${palette.line}`,
          boxShadow: '0 16px 48px rgba(0,0,0,0.42)',
          fontFamily,
          fontSize: 38,
          lineHeight: 1.18,
          fontWeight: 720,
          color: palette.text,
          textAlign: 'center',
          whiteSpace: 'pre-wrap',
        }}
      >
        {active.text.split(KEYWORD).map((part, index) => (
          <span key={`${part}-${index}`} style={{color: KEYWORD_HIGHLIGHT.test(part) ? palette.datahub : palette.text}}>
            {part}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
