import {StoryScene, type StoryShot} from '../components/StoryScene';
import {palette} from '../theme';

const shots: StoryShot[] = [
  {duration: 100, kind: 'image', image: 'assets/github-pr.png', headline: 'A real public GitHub draft PR', subhead: 'The repair is reviewable—not silently deployed.', accent: palette.approval, badge: 'PR #1'},
  {duration: 95, kind: 'image', image: 'assets/github-pr.png', headline: 'Exactly four changed files', subhead: 'Alias · migration · schema test · guide', accent: palette.approval, zoom: 1.16, objectPosition: 'center 27%'},
  {duration: 95, kind: 'image', image: 'assets/github-pr.png', headline: 'Executable proof travels with the diff', subhead: 'Invocation, test count, commits, and Patch SHA.', accent: palette.proof, zoom: 1.18, objectPosition: 'center 53%'},
  {duration: 100, kind: 'image', image: 'assets/github-actions.png', headline: 'GitHub Actions stays green', subhead: 'Backend, safety, dbt, and frontend gates rebuild in CI.', accent: palette.proof, badge: 'CHECKS PASS'},
];

export const Scene08PullRequest = () => <StoryScene shots={shots} shotOffset={34} />;
