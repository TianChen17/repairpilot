import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import captions from '../../public/data/captions.json';
import {fontFamily, palette} from '../theme';

type Caption = {
  text: string;
  startMs: number;
  endMs: number;
};

const KEYWORD = /(DataHub|MCP|BLOCK|RepairPilot|DeepSeek|dbt|GitHub|real|synthetic|Evidence Receipt|fourteen tests|14 tests|zero failures)/gi;
const KEYWORD_HIGHLIGHT = /^(DataHub|MCP|BLOCK|RepairPilot|DeepSeek|dbt|GitHub|real|synthetic|Evidence Receipt|fourteen tests|14 tests|zero failures)$/i;

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
          left: 220,
          right: 220,
          bottom: 52,
          minHeight: 68,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '11px 24px',
          borderRadius: 15,
          background: 'rgba(7, 11, 23, 0.92)',
          border: `1px solid ${palette.line}`,
          boxShadow: '0 16px 48px rgba(0,0,0,0.42)',
          fontFamily,
          fontSize: 34,
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
