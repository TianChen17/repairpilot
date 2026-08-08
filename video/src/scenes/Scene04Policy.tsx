import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 95, kind: 'metric', eyebrow: 'DETERMINISTIC POLICY · V1.0.0', metric: '100/100', headline: 'HIGH RISK', subhead: 'Breaking change plus governed downstream impact.', accent: palette.block},
  {duration: 95, kind: 'diagram', eyebrow: 'FOUR MATCHED RULES', headline: 'The policy—not the LLM—decides.', bullets: ['Breaking schema change', 'Governed or Tier-1 asset', 'Three or more downstream assets', 'Dashboard impact'], accent: palette.block},
  {duration: 95, kind: 'diagram', eyebrow: 'AUTHORITY BOUNDARY', headline: 'The model cannot override BLOCK.', bullets: ['No risk mutation', 'No approval bypass', 'No direct publish', 'No arbitrary execution'], accent: palette.block},
  {duration: 105, kind: 'metric', eyebrow: 'FAIL-CLOSED DEFAULT', metric: 'LOCKED', headline: 'No DataHub context, no release.', subhead: 'Unavailable context and failed builds remain blocked.', accent: palette.block, badge: 'SAFE DEFAULT'},
];

export const Scene04Policy = () => <StoryScene shots={shots} shotOffset={16} />;
