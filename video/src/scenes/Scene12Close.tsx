import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {
    duration: 300,
    kind: 'title',
    eyebrow: 'REPAIRPILOT · AGENTS THAT DO REAL WORK',
    headline: 'BLOCK. REPAIR. PROVE. REMEMBER.',
    subhead: 'repairpilot.145-241-207-154.sslip.io  ·  github.com/TianChen17/repairpilot',
    accent: palette.memory,
    badge: 'PUBLIC DEMO',
  },
];

export const Scene12Close = () => <StoryScene shots={shots} shotOffset={50} />;
