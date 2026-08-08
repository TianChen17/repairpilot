import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 120, kind: 'receipt', eyebrow: 'IMMUTABLE EVIDENCE RECEIPT', headline: 'One record joins every proof point.', bullets: ['DataHub URNs + MCP tools', 'Policy version + risk score', 'Base + repair commits', 'dbt invocation + results'], accent: palette.datahub},
  {duration: 120, kind: 'receipt', eyebrow: 'TRACEABILITY', headline: 'Context → decision → code → test', bullets: ['owner: Revenue Analytics', 'policy: 1.0.0 · BLOCK', 'tests: 14 · failures: 0', 'mode: LIVE'], accent: palette.datahub},
  {duration: 120, kind: 'metric', eyebrow: 'PATCH INTEGRITY', metric: 'SHA-256', headline: 'Same bytes. Same repair.', subhead: '588e2b4ba90abf9c…', accent: palette.proof},
  {duration: 120, kind: 'metric', eyebrow: 'VERIFIED RUN', metric: 'LIVE', headline: 'Approval and write-back addresses included.', subhead: 'Replay mode is separately and honestly labeled.', accent: palette.datahub, badge: 'NOT REPLAY'},
];

export const Scene10Receipt = () => <StoryScene shots={shots} shotOffset={43} />;
