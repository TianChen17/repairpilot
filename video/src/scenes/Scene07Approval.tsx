import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 80, kind: 'image', image: 'assets/repairpilot-awaiting.png', headline: 'Approval unlocks only after proof', subhead: 'Risk remains blocked while authority is pending.', accent: palette.approval, badge: 'AWAITING OWNER'},
  {duration: 80, kind: 'metric', eyebrow: 'HUMAN AUTHORITY', metric: 'OWNER', headline: 'Revenue Analytics decides.', subhead: 'The accountable DataHub owner—not the model.', accent: palette.approval},
  {duration: 80, kind: 'image', image: 'assets/repairpilot-awaiting.png', headline: 'Approve repair', subhead: 'The decision is timestamped into the evidence record.', accent: palette.approval, zoom: 1.2, objectPosition: 'center 79%'},
  {duration: 90, kind: 'image', image: 'assets/repairpilot-learned.png', headline: 'APPROVED → LEARNED', subhead: 'A rejection would create no pull request.', accent: palette.proof, badge: 'AUTHORITY RECORDED'},
];

export const Scene07Approval = () => <StoryScene shots={shots} shotOffset={30} />;
