import {Audio} from '@remotion/media';
import {Sequence, staticFile, useVideoConfig} from 'remotion';
import manifest from '../../public/data/voiceover-manifest.json';
import timeline from '../../timeline.json';

type VoiceScene = {
  id: number;
  audio: string;
  startMs: number;
  durationMs: number;
};

export const AudioTracks: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <>
      {(manifest.scenes as VoiceScene[]).map((scene) => (
        <Sequence key={scene.id} from={Math.round((scene.startMs / 1000) * fps)} durationInFrames={Math.ceil((scene.durationMs / 1000) * fps)}>
          <Audio src={staticFile(scene.audio)} volume={1} />
        </Sequence>
      ))}
      {timeline.chapters.map((chapter) => Math.round((chapter.startMs / 1000) * fps)).map((from) => (
        <Sequence key={from} from={from} durationInFrames={12}>
          <Audio src={staticFile('audio/interface-tone.wav')} volume={0.1} />
        </Sequence>
      ))}
    </>
  );
};
