import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 126, kind: 'title', eyebrow: 'DATAHUB WRITE-BACK', headline: 'REMEMBER', subhead: 'The verified outcome becomes institutional memory.', accent: palette.memory},
  {duration: 126, kind: 'image', image: 'assets/datahub-assertions.png', headline: 'A successful gross_revenue assertion', subhead: 'Real Assertion entity and passing run state.', accent: palette.memory, badge: 'WRITE-BACK'},
  {duration: 126, kind: 'image', image: 'assets/datahub-documents.png', headline: 'Incident Documents persist root cause and proof', subhead: 'Every run has a traceable DataHub address.', accent: palette.memory, badge: 'DOCUMENT'},
  {duration: 126, kind: 'image', image: 'assets/datahub-runbook.png', headline: 'One idempotent safe-column-rename Runbook', subhead: 'The next responder starts from verified knowledge.', accent: palette.memory, badge: 'RUNBOOK'},
  {duration: 126, kind: 'image', image: 'assets/repairpilot-learned.png', headline: 'The next incident starts smarter', subhead: 'Incident · Assertion · Runbook · GitHub PR', accent: palette.memory, zoom: 1.13, objectPosition: 'center 86%'},
];

export const Scene09Writeback = () => <StoryScene shots={shots} shotOffset={38} />;
