void droidSpeak (int soundPin, uint8_t wordCount) {
  int toneDuration;
  int toneFreq;     // frequency of tone created

  // generate the random set of words
  for ( int i=0; i < wordCount; i++) {
    toneDuration = random (50, 300);
    toneFreq = random (200, 1500);
    tone(soundPin, toneFreq);
    delay(toneDuration);
    noTone(soundPin);

  }

}

unsigned int unpackInt(const byte *buffer) {
    unsigned int temp = 0;
    temp = ((buffer[0] << 24) |
            (buffer[1] << 16) |
            (buffer[2] <<  8) |
             buffer[3]);
    return temp;
}