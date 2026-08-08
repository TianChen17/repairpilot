import {Composition} from 'remotion';
import {RepairPilotDemo} from './RepairPilotDemo';

export const RemotionRoot = () => (
  <Composition
    id="RepairPilotDemo"
    component={RepairPilotDemo}
    durationInFrames={4740}
    fps={30}
    width={1920}
    height={1080}
  />
);
