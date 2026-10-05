"""Lab 04 - AWS managed AI services: no model, no training, just APIs.

Domain 1.2 (capabilities of Comprehend, Translate, Polly). Rekognition/Textract/Transcribe work the same way
but need an image, a document or an audio file in S3.
Run: python labs/lab04_ai_services.py
"""

import boto3

REVIEW = ("I ordered a coffee machine from Lyon on 3 March. Delivery was late and the box was crushed, "
          "but Sarah from support called me at +33 6 12 34 56 78 and fixed it fast. Great service!")

comprehend = boto3.client("comprehend")
translate = boto3.client("translate")
polly = boto3.client("polly")


def main():
    s = comprehend.detect_sentiment(Text=REVIEW, LanguageCode="en")
    print("Comprehend sentiment:", s["Sentiment"], {k: round(v, 2) for k, v in s["SentimentScore"].items()})

    ents = comprehend.detect_entities(Text=REVIEW, LanguageCode="en")["Entities"]
    print("Comprehend entities: ", [(e["Text"], e["Type"]) for e in ents])

    pii = comprehend.detect_pii_entities(Text=REVIEW, LanguageCode="en")["Entities"]
    redacted = REVIEW
    for e in sorted(pii, key=lambda e: e["BeginOffset"], reverse=True):
        redacted = redacted[:e["BeginOffset"]] + f"[{e['Type']}]" + redacted[e["EndOffset"]:]
    print("Comprehend PII redacted:", redacted)

    fr = translate.translate_text(Text=REVIEW, SourceLanguageCode="en", TargetLanguageCode="fr")["TranslatedText"]
    print("Translate -> fr:", fr)

    audio = polly.synthesize_speech(Text=fr, OutputFormat="mp3", VoiceId="Lea", Engine="neural")
    with open("review.mp3", "wb") as f:
        f.write(audio["AudioStream"].read())
    print("Polly: wrote review.mp3 (French neural voice Lea)")
    print("\nNote: no ML expertise needed -> that's the exam's cue for managed AI services.")


if __name__ == "__main__":
    main()
