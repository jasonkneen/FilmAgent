import PipelinePage from '@/components/pipelines/PipelinePage';

export default function StandardPipelinePage() {
  return (
    <PipelinePage
      pipeline="standard"
      title="静态短视频"
      subtitle="输入旁白文案，按句号切分片段，为每句生成图片并合成为静态短视频"
    />
  );
}
