---
name: talking-head-reel
description: Turn a raw talking-head video into a finished vertical reel - clean cut, word-timed animated subtitles (RTL and LTR: Kurdish Sorani, Arabic, English, ...), flowing motion graphics, voice polish, subtle SFX, 1080x1920 export. Use when the user wants a talking video cut, subtitled or animated for Reels, TikTok or Shorts.
---

# Talking-head reel

Uses the scripts in this repository (`cut/`, `subs/`, `graphics/`, `compose/`, `sound/`). Read `README.md` for the commands. This file is about judgement: order of work, what to check, what to avoid.

## Work in stages and get approval between them

1. **Clean cut.** Send a low-res numbered preview (`cut/preview.py`) and the table of kept clips with their source times. Wait for the OK. People answer with clip numbers.
2. **High-quality clean export**, then an **MP3/WAV of the clean cut** for transcription. Transcribe the clean cut, not the raw file, so word times match the video being animated.
3. **Subtitle proof.** Give the numbered `subs.txt`. Apply the user's corrections exactly and add recurring ones to their fixes file so they never have to repeat them.
4. **Animated reel**, then fix rounds on the same file name.

Do not run ahead a stage. Do not make content decisions (which section to drop to hit a length) for the user: list sections with their seconds and let them pick.

## Clean cut rules

- Work in source frame numbers. Always ffprobe frame rate, rotation and colour range first.
- Never run full-resolution video through a slow link; make a small proxy and a 16 kHz mono WAV for analysis.
- Repeated line: keep the last clean take. No transcript yet: `cut/repeats.py`, then confirm by looking at frames. If two readings are plausible, export two previews and let the user choose.
- Word endings: use `cut/bounds.py` (sound ends when the level stays below -72 dB for 100 ms; pads 0.12 s before, 0.22 s after). Use `hard_start`/`hard_end` only when two takes are closer than the pads.
- Also shorten pauses inside kept material that run longer than about 0.6 s.
- Verify: frame count equals the sum of clip lengths; look at stills around every join.

## Subtitles

- Set `TEXT.dir` and `TEXT.font` in `graphics/config.js` to the language of the video first (`rtl` + Vazirmatn for Sorani, `ltr` + Inter for English). Wrong direction shows the words of a line in reverse order.
- Word-level timing is required for good results. Without it, timing is guesswork; ask for the JSON.
- 1 to 4 words per chunk, never split a noun from its modifier, break at commas and breaths. Hand-pick `--sizes`.
- In RTL text, keep loanwords the user writes in Latin as Latin, without commas or full stops stuck to them (`chunks.py` does this when Latin words are the minority). English text keeps its punctuation.
- Sorani: normalise ي/ى to ی and ك to ک; speech-to-text misspells common words consistently, so read every line against its context and list doubtful words for the user instead of guessing silently.
- The first chunk is visible from frame 0.

## Graphics

- Plan from the transcript: jump-cut times, lists, named things, the one or two strongest words, the call to action. A visual beat every 2 to 4 seconds, varied; never the same device twice in a row.
- Use split screens for lists and explanations, return to the speaker for personal or emphatic lines, hide jump cuts with a zoom change and a soft light dip.
- Never cut the speaker out, never put anything behind them, never frame them in a box.
- Prefer drawn lines, mask reveals, drifting and gentle push-ins over boxes, pills, glows and neon.
- Take the palette from the user's brand (two accent tones, an ink colour, a paper colour). Few colours.
- Real logos only from files the user supplies or official sources; place them, do not redraw them.
- Respect safe zones: top 220 px, bottom 420 px, right column x > 940 between y 900 and 1500. Subtitles at y 1330, y 800 in split mode, lower them when a title sits on the chest area (`CAPDOWN`), hide them when a title says the same words (`CAPHIDE`).
- Tell the user about any on-screen text they did not say.
- Check a still sheet (`graphics/shot.py`) of every scene with your own eyes before a full render: overlap, overflow, clipped tops, captions crossing the face.
- Everything must be a pure function of `t`. No CSS animations, timers or `Math.random`.

## Compositing and sound

- Render layers in parts whose frame ranges match the composite parts exactly; give `comp.py` the matching layer files. Never seek into layer files.
- Zoom range 1.00 to about 1.08, slow. If the user dislikes camera movement, set every zoom to 1.0 and recomposite; layers do not need re-rendering.
- Zoom/shift change = recomposite only. Text or graphic change = re-render that part. Audio change = re-mux.
- SFX quiet: whooshes -22 to -25 dB, ticks -27 to -31, at most one impact. Voice chain and mix are in `sound/voice.sh`; aim for about -14 LUFS.

## Before handing over

- ffprobe: 1080x1920, expected frame rate, frame count equals the clean cut, AAC 48 kHz.
- Pixel-compare frame 0 of the result with the clean video to prove the overlay is present from the start.
- Still sheet across the final file; loudness measured; no test numbers left.
- Report in a few lines: file name, what changed, anything you added, and what you could not judge without watching playback (motion smoothness, timing feel).
