import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 80, kind: 'title', eyebrow: 'NOT AN INCIDENT CHATBOT', headline: 'BLOCK', subhead: 'Enforce a release decision before damage.', accent: palette.block},
  {duration: 80, kind: 'title', eyebrow: 'INCIDENT-TO-REPAIR', headline: 'REPAIR', subhead: 'Generate a compatibility-safe code change.', accent: palette.approval},
  {duration: 80, kind: 'title', eyebrow: 'EXECUTABLE EVIDENCE', headline: 'PROVE', subhead: 'Run the affected dbt build in isolation.', accent: palette.proof},
  {duration: 90, kind: 'title', eyebrow: 'INSTITUTIONAL MEMORY', headline: 'REMEMBER', subhead: 'Write the incident, assertion, and runbook back to DataHub.', accent: palette.memory},
];

export const Scene02Promise = () => <StoryScene shots={shots} shotOffset={6} />;
