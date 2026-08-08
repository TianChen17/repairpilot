import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 96, kind: 'diagram', eyebrow: 'DEEPSEEK V4 FLASH', headline: 'A bounded repair contract', subhead: 'Strict JSON output enters a deterministic validator.', accent: palette.approval, badge: 'AI PROPOSAL'},
  {duration: 96, kind: 'image', image: 'assets/repairpilot-learned.png', headline: 'Preserve gross_amount as a compatibility alias', subhead: 'Existing consumers keep working during migration.', accent: palette.approval, zoom: 1.16, objectPosition: 'center 58%'},
  {duration: 96, kind: 'image', image: 'assets/repairpilot-learned.png', headline: 'Migrate the controlled downstream model', subhead: 'The new gross_revenue contract becomes available.', accent: palette.approval, zoom: 1.19, objectPosition: '62% 58%'},
  {duration: 96, kind: 'image', image: 'assets/repairpilot-learned.png', headline: 'Add a real dbt schema test', subhead: 'The migration gains an executable guardrail.', accent: palette.approval, zoom: 1.22, objectPosition: '83% 59%'},
  {duration: 96, kind: 'diagram', eyebrow: 'EXECUTION SANDBOX', headline: 'Three operations. Three allowlisted paths.', bullets: ['No model-generated shell', 'No arbitrary SQL', 'Detached Git worktree', 'Temporary Postgres schemas'], accent: palette.approval},
];

export const Scene05Repair = () => <StoryScene shots={shots} shotOffset={20} />;
