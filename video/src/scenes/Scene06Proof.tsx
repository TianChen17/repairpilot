import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 108, kind: 'video', video: 'assets/repairpilot-live.webm', headline: 'Live incident execution', subhead: 'Real browser capture · accelerated 3×', accent: palette.proof, badge: '3×', playbackRate: 3, trimBeforeSeconds: 0},
  {duration: 108, kind: 'metric', eyebrow: 'NEGATIVE CONTROL', metric: 'FAILED', headline: 'The original breaking change reproduces.', subhead: 'A repair is not trusted until the failure is observed.', accent: palette.block},
  {duration: 108, kind: 'diagram', eyebrow: 'ISOLATED EXECUTOR', headline: 'Temporary schemas prevent cross-run pollution.', bullets: ['rp_<run>_raw', 'rp_<run>_staging', 'rp_<run>_intermediate', 'rp_<run>_marts'], accent: palette.datahub},
  {duration: 108, kind: 'video', video: 'assets/repairpilot-live.webm', headline: 'dbt build validates the affected selection', subhead: 'Real browser capture · accelerated 3×', accent: palette.proof, badge: '3×', playbackRate: 3, trimBeforeSeconds: 48},
  {duration: 108, kind: 'metric', eyebrow: 'EXECUTABLE PROOF', metric: '14 tests', headline: 'PROVE: zero failures', subhead: 'Patch SHA 588e2b4b… recorded with the invocation.', accent: palette.proof, badge: 'PASS'},
];

export const Scene06Proof = () => <StoryScene shots={shots} shotOffset={25} />;
