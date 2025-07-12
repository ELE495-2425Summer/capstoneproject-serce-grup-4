from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import pickle

encoder = VoiceEncoder()

with open("/home/bitirme/Desktop/robot_code/saved_embeddings.pkl", "rb") as f:
    speaker_embeddings = pickle.load(f)

def verify_speaker(incoming_audio_path: str, threshold: float = 0.6) -> str:
    wav = preprocess_wav(incoming_audio_path)
    test_emb = encoder.embed_utterance(wav)

    best_score = -1
    best_match = "unknown"

    for name, ref_emb in speaker_embeddings.items():
        similarity = np.dot(test_emb, ref_emb) / (np.linalg.norm(test_emb) * np.linalg.norm(ref_emb))
        if similarity > best_score:
            best_score = similarity
            best_match = name

    return best_match if best_score > threshold else "unknown"
