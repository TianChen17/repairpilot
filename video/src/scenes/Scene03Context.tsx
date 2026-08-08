import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 95, kind: 'image', image: 'assets/datahub-context.png', headline: 'DataHub knows the actual dbt asset', subhead: 'Real OSS UI · real ingested metadata', accent: palette.datahub, badge: 'LIVE DATAHUB'},
  {duration: 95, kind: 'image', image: 'assets/datahub-context.png', headline: 'Revenue Analytics owns the decision', subhead: 'Finance Analytics domain', accent: palette.datahub, zoom: 1.14, objectPosition: '78% 15%'},
  {duration: 95, kind: 'image', image: 'assets/datahub-context.png', headline: 'Tier1 · FinancialMetric · SLA-1h', subhead: 'Governance context changes the release outcome.', accent: palette.datahub, zoom: 1.17, objectPosition: '70% 24%'},
  {duration: 95, kind: 'image', image: 'assets/datahub-lineage.png', headline: 'Field lineage reveals downstream exposure', subhead: 'Read through official DataHub MCP tools.', accent: palette.datahub, badge: 'GET_LINEAGE'},
  {duration: 95, kind: 'image', image: 'assets/datahub-queries.png', headline: 'Three stored usage queries', subhead: 'Synthetic query metadata · honestly labeled.', accent: palette.datahub, badge: 'GET_DATASET_QUERIES'},
  {duration: 95, kind: 'image', image: 'assets/repairpilot-learned.png', headline: 'Four impacted assets, one accountable owner', subhead: 'Every context card traces back to MCP evidence.', accent: palette.datahub, zoom: 1.07, objectPosition: 'center 40%'},
];

export const Scene03Context = () => <StoryScene shots={shots} shotOffset={10} />;
