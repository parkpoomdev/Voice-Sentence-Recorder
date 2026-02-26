# Voice Recorder Web Application Specification

## Project Overview
- **Project name**: Voice Sentence Recorder
- **Type**: Web application (Python Flask + HTML/CSS/JS)
- **Core functionality**: Split text into sentences, record audio for each, and export individual/combined WAV files
- **Target users**: Language learners, voice actors, audio content creators

## UI/UX Specification

### Layout Structure
- **Header**: App title with professional branding
- **Input Section**: Textarea for entering text with "Split" button
- **Cards Section**: Grid of sentence cards with recording controls
- **Export Section**: Export buttons for individual and combined audio files

### Visual Design
- **Color Palette**:
  - Primary: #1a1a2e (dark navy)
  - Secondary: #16213e (deep blue)
  - Accent: #0f3460 (medium blue)
  - Highlight: #e94560 (coral red for record button)
  - Success: #00d9a5 (teal green)
  - Text: #eaeaea (light gray)
  - Card bg: #1f1f3d (dark purple-gray)
- **Typography**:
  - Font: 'Inter', sans-serif
  - Headings: 600 weight
  - Body: 400 weight
- **Spacing**: 16px base unit
- **Effects**: Subtle shadows, smooth transitions (0.3s)

### Components
1. **Text Input Area**
   - Large textarea with placeholder text
   - "Split Text" button (primary style)
   - "Clear All" button (secondary style)

2. **Sentence Card**
   - Card container with sentence text
   - Status indicator (pending/recorded)
   - Three buttons: Record (red), Playback (green), Reset (gray)
   - Audio waveform visualization during recording

3. **Export Panel**
   - "Export Individual" button - downloads each sentence as separate WAV
   - "Export Combined (1s)" button - combines with 1s silence
   - "Export Combined (0.8s)" button - combines with 0.8s silence
   - "Export Combined (0.5s)" button - combines with 0.5s silence

### Responsive Breakpoints
- Desktop: > 768px (cards in grid)
- Mobile: <= 768px (single column)

## Functionality Specification

### Core Features
1. **Text Splitting**
   - Split text by punctuation (. ! ?)
   - Trim whitespace
   - Remove empty sentences

2. **Audio Recording**
   - Use MediaRecorder API in browser
   - Record in WAV format (or convert to WAV)
   - Store audio as base64 in cards

3. **Audio Playback**
   - Play recorded audio for each card
   - Visual feedback during playback

4. **Reset Function**
   - Clear recorded audio for individual card

5. **Export Functions**
   - Individual: Each sentence audio as separate WAV file
   - Combined: Concatenate all with specified silence gap

### Backend Endpoints (Python/Flask)
- `POST /api/save_audio` - Save audio data
- `POST /api/export_individual` - Export individual WAV files (zip)
- `POST /api/export_combined` - Export combined WAV with specified gap

### Audio Processing
- Use pydub or scipy for audio manipulation
- Add silence between sentences in combined export

## Acceptance Criteria
1. User can enter text and split into sentences
2. Each sentence becomes a card with Record/Playback/Reset
3. User can record audio for each sentence
4. User can play back recorded audio
5. User can reset individual recordings
6. Export produces correct WAV files in current directory
7. Combined exports have correct silence gaps
8. UI is responsive and professional-looking
