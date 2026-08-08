import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from '../timeline.json';
import {AudioTracks} from './components/AudioTracks';
import {Captions} from './components/Captions';
import {StoryScene, type StoryShot} from './components/StoryScene';
import {palette} from './theme';

const shots = timeline.chapters.flatMap((chapter) =>
  chapter.shots.map((shot) => ({...shot, chapter: chapter.label})),
) as StoryShot[];

const ProgressRail = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  return <div style={{position:'absolute',left:0,right:0,bottom:0,height:6,background:'#111827'}}><div style={{width:`${interpolate(frame,[0,durationInFrames-1],[0,100],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}%`,height:'100%',background:`linear-gradient(90deg,${palette.block},${palette.approval},${palette.proof},${palette.memory})`}} /></div>;
};

export const RepairPilotDemo = () => <AbsoluteFill style={{background:palette.background}}>
  <StoryScene shots={shots} />
  <AudioTracks />
  <Captions />
  <ProgressRail />
</AbsoluteFill>;
