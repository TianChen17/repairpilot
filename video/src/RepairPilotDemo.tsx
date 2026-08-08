import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {TransitionSeries} from '@remotion/transitions';
import {AudioTracks} from './components/AudioTracks';
import {Captions} from './components/Captions';
import {Scene01ColdOpen} from './scenes/Scene01ColdOpen';
import {Scene02Promise} from './scenes/Scene02Promise';
import {Scene03Context} from './scenes/Scene03Context';
import {Scene04Policy} from './scenes/Scene04Policy';
import {Scene05Repair} from './scenes/Scene05Repair';
import {Scene06Proof} from './scenes/Scene06Proof';
import {Scene07Approval} from './scenes/Scene07Approval';
import {Scene08PullRequest} from './scenes/Scene08PullRequest';
import {Scene09Writeback} from './scenes/Scene09Writeback';
import {Scene10Receipt} from './scenes/Scene10Receipt';
import {Scene11Safety} from './scenes/Scene11Safety';
import {Scene12Close} from './scenes/Scene12Close';
import {palette} from './theme';

const ProgressRail = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 7, background: '#111827'}}>
      <div
        style={{
          width: `${interpolate(frame, [0, durationInFrames - 1], [0, 100], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}%`,
          height: '100%',
          background: `linear-gradient(90deg, ${palette.block}, ${palette.approval}, ${palette.proof}, ${palette.memory})`,
        }}
      />
    </div>
  );
};

export const RepairPilotDemo = () => (
  <AbsoluteFill style={{background: palette.background}}>
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={390} name="01 Cold open"><Scene01ColdOpen /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={330} name="02 Promise"><Scene02Promise /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={570} name="03 DataHub context"><Scene03Context /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={390} name="04 Policy"><Scene04Policy /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={480} name="05 Repair"><Scene05Repair /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={540} name="06 Proof"><Scene06Proof /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={330} name="07 Approval"><Scene07Approval /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={390} name="08 Pull request"><Scene08PullRequest /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={630} name="09 Write-back"><Scene09Writeback /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={480} name="10 Evidence receipt"><Scene10Receipt /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={420} name="11 Safety"><Scene11Safety /></TransitionSeries.Sequence>
      <TransitionSeries.Sequence durationInFrames={300} name="12 Close"><Scene12Close /></TransitionSeries.Sequence>
    </TransitionSeries>
    <AudioTracks />
    <Captions />
    <ProgressRail />
  </AbsoluteFill>
);
