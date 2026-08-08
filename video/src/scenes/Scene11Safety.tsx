import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 140, kind: 'metric', eyebrow: 'THREE CONSECUTIVE LIVE RUNS', metric: '30 · 31 · 28s', headline: 'One patch hash. One Runbook.', subhead: 'No terminal intervention and under the 150-second target.', accent: palette.proof},
  {duration: 140, kind: 'diagram', eyebrow: 'PRODUCTION-MINDED RAILS', headline: 'Safe by construction.', bullets: ['Fail closed', 'Path + operation allowlist', 'Secrets never reach the browser', '0 residual schemas or worktrees'], accent: palette.proof},
  {duration: 140, kind: 'diagram', eyebrow: 'HONEST DEMONSTRATION', headline: 'Synthetic data. REAL execution.', bullets: ['1,200 synthetic orders', 'Real DataHub + MCP', 'Real Postgres + dbt', 'Real DeepSeek + GitHub'], accent: palette.datahub},
];

export const Scene11Safety = () => <StoryScene shots={shots} shotOffset={47} />;
