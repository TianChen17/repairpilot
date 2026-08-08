import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 75, kind: 'metric', eyebrow: 'SCHEMA CHANGE DETECTED', metric: '01', headline: 'gross_amount → gross_revenue', subhead: 'A harmless-looking rename enters review.', accent: palette.block},
  {duration: 75, kind: 'image', image: 'assets/repairpilot-ready.png', headline: 'One renamed field.', subhead: 'Northstar Commerce · change control', accent: palette.block, zoom: 1.01},
  {duration: 75, kind: 'image', image: 'assets/repairpilot-ready.png', headline: 'Four downstream failures.', subhead: 'Models, dashboard, and scheduled decisions are exposed.', accent: palette.block, zoom: 1.09, objectPosition: 'center 22%'},
  {duration: 75, kind: 'image', image: 'assets/repairpilot-ready.png', headline: 'Breaking contract detected before merge', subhead: 'The unsafe source change never reaches production.', accent: palette.block, zoom: 1.18, objectPosition: '76% 18%'},
  {duration: 90, kind: 'metric', eyebrow: 'RELEASE DECISION', metric: 'BLOCK', headline: 'Stop the blast radius before it starts.', subhead: 'Deterministic policy—not model confidence—holds the gate.', accent: palette.block, badge: 'BEFORE MERGE'},
];

export const Scene01ColdOpen = () => <StoryScene shots={shots} shotOffset={1} />;
