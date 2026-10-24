/* AudioWorklet: playback and capture advance on the same process() frame grid.
 * No microphone monitoring: input is copied only into a private capture buffer.
 * currentFrame detects missing worklet callbacks/chunks; it cannot expose every
 * hardware/driver xrun hidden behind the browser's audio pipeline. */
class SonicBenchProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.run = null;
    this.lastInputChannels = 0;
    this.port.onmessage = ({ data }) => {
      if (data.type === 'stop') { this.run = null; return; }
      if (data.type !== 'start' || this.run) return;
      this.run = {
        id: data.id, source: new Float32Array(data.source), position: 0,
        capture: Boolean(data.capture), mic: data.inputChannel - 1,
        reference: data.referenceChannel == null ? null : data.referenceChannel - 1,
        output: data.outputChannel - 1,
        referenceOutput: data.referenceOutputChannel == null ? null : data.referenceOutputChannel - 1,
        chunkSize: 4096, chunkOffset: 0, chunkStart: null,
        microphone: new Float32Array(4096), electrical: new Float32Array(4096),
        firstFrame: null, expectedFrame: null, processGaps: 0, inputChannelMin: Infinity,
        inputMissingFrames: 0, chunkIndex: 0, lastProgress: 0,
      };
    };
  }
  flush(run) {
    if (!run.chunkOffset) return;
    const microphone = run.microphone.slice(0, run.chunkOffset);
    const electrical = run.reference === null ? null : run.electrical.slice(0, run.chunkOffset);
    const message = { type: 'capture', id: run.id, index: run.chunkIndex++,
      start: run.position - run.chunkOffset, frame: run.chunkStart,
      count: run.chunkOffset, microphone: microphone.buffer,
      reference: electrical && electrical.buffer };
    this.port.postMessage(message, electrical ? [microphone.buffer, electrical.buffer] : [microphone.buffer]);
    run.chunkOffset = 0;
    run.chunkStart = null;
  }
  process(inputs, outputs) {
    const output = outputs[0] || [];
    for (const channel of output) channel.fill(0);
    const input = inputs[0] || [];
    if (input.length && input.length !== this.lastInputChannels) {
      this.lastInputChannels = input.length;
      this.port.postMessage({ type: 'input-ready', channels: input.length });
    }
    const run = this.run;
    if (!run) return true;
    const blockLength = output[0]?.length || 128;
    if (run.firstFrame === null) {
      run.firstFrame = currentFrame;
      this.port.postMessage({ type: 'started', id: run.id, frame: currentFrame });
    }
    if (run.expectedFrame !== null && run.expectedFrame !== currentFrame) run.processGaps++;
    run.expectedFrame = currentFrame + blockLength;
    if (run.capture) run.inputChannelMin = Math.min(run.inputChannelMin, input.length);
    const count = Math.min(blockLength, run.source.length - run.position);
    for (let sample = 0; sample < count; sample++) {
      const value = run.source[run.position];
      if (output[run.output]) output[run.output][sample] = value;
      if (run.referenceOutput !== null && output[run.referenceOutput]) output[run.referenceOutput][sample] = value;
      if (run.capture) {
        if (run.chunkStart === null) run.chunkStart = currentFrame + sample;
        const microphone = input[run.mic];
        const reference = run.reference === null ? null : input[run.reference];
        if (!microphone || (run.reference !== null && !reference)) run.inputMissingFrames++;
        run.microphone[run.chunkOffset] = microphone ? microphone[sample] : 0;
        run.electrical[run.chunkOffset] = reference ? reference[sample] : 0;
        run.chunkOffset++;
      }
      run.position++;
      if (run.capture && run.chunkOffset === run.chunkSize) this.flush(run);
    }
    if (run.position - run.lastProgress >= sampleRate / 4) {
      run.lastProgress = run.position;
      this.port.postMessage({ type: 'progress', id: run.id, position: run.position });
    }
    if (run.position === run.source.length) {
      this.flush(run);
      this.port.postMessage({ type: 'done', id: run.id, frames: run.position,
        firstFrame: run.firstFrame, endFrame: currentFrame + count,
        processGaps: run.processGaps, inputChannelMin: Number.isFinite(run.inputChannelMin) ? run.inputChannelMin : null,
        inputMissingFrames: run.inputMissingFrames, chunks: run.chunkIndex });
      this.run = null;
    }
    return true;
  }
}
registerProcessor('sonic-bench', SonicBenchProcessor);
