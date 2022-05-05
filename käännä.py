from transformers import pipeline
import spacy

SPACY_MODELS = {
	"fi": spacy.load("spacy_fi_experimental_web_md"),
	"en": spacy.load("en_core_web_sm"),
}

class Kääntäjä:
	def __init__(self, src: str, tgt: str):
		assert src in SPACY_MODELS
		self.src = src
		self.tgt = tgt
		self.translator = pipeline(f"translation_{src}_to_{tgt}", model=f"Helsinki-NLP/opus-mt-{src}-{tgt}")

	def käännä(self, teksti):
		nlp = SPACY_MODELS[self.src]
		doc = nlp(teksti)
		lauseet = list(map(str, doc.sents))
		ans = []
		for lause in lauseet:
			if not lause.strip():
				ans.append(lause)
			else:
				ans.append(self.translator(lause)[0]["translation_text"])
		return " ".join(ans)


