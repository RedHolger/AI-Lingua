from fastapi import FastAPI, Request, Header
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from transcriber import Transcriber
import os, hmac, hashlib, re, json

class Line(BaseModel):
    start_time: float
    end_time: float
    text: str

class LinesPayload(BaseModel):
    lines: List[Line]

app = FastAPI()
transcriber = Transcriber()

def verify_signature(body: bytes, signature: str | None) -> bool:
    secret = os.getenv("AI_HMAC_SECRET")
    if not secret or not signature:
        return True
    mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, signature)

@app.post("/simplify")
async def simplify(request: Request) -> Dict:
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Signature")):
        return {"error":"invalid signature"}
    payload_json = json.loads(body.decode())
    lines = [Line(**l) for l in payload_json.get("lines", [])]
    data = {"lines": [l.dict() for l in lines]}
    res = await transcriber.simplify_text(data)
    return res

@app.post("/analyze_language")
async def analyze_language(request: Request) -> Dict:
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Signature")):
        return {"error":"invalid signature"}
    payload_json = json.loads(body.decode())
    texts = [l.get("text","") for l in payload_json.get("lines", [])]
    words = []
    freq = {}
    for t in texts:
        toks = re.findall(r"[A-Za-z']+", t.lower())
        for w in toks:
            if len(w) <= 2: continue
            words.append(w)
            freq[w] = freq.get(w,0)+1
    top = sorted(freq.items(), key=lambda x:(-x[1],x[0]))[:10]
    vocab = [w for w,_ in top]
    grammar = []
    joined = "\n".join(texts).lower()
    if "?" in "\n".join(texts): grammar.append("Questions used")
    if " not " in joined or "n't" in joined: grammar.append("Negation patterns")
    if " will " in joined or "going to" in joined: grammar.append("Future constructions")
    if any(k in joined for k in [" was "," were "," had "]): grammar.append("Past forms")
    nouns = [w for w in vocab if re.match(r"^[a-z]+$", w)]
    return {"elements": {"vocab": vocab, "grammar": grammar, "nouns": nouns}}

@app.post("/generate_previews")
async def generate_previews(request: Request) -> Dict:
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Signature")):
        return {"error":"invalid signature"}
    payload_json = json.loads(body.decode())
    scenes = payload_json.get("scenes", {}).get("scenes", [])
    lines_out = []
    for sc in scenes:
        start = max(0.0, float(sc.get("start",0.0)) - 5.0)
        texts = [l.get("text","") for l in sc.get("lines", [])]
        freq = {}
        for t in texts:
            for w in re.findall(r"[A-Za-z']+", t.lower()):
                if len(w) <= 2: continue
                freq[w] = freq.get(w,0)+1
        topw = [w for w,_ in sorted(freq.items(), key=lambda x:(-x[1],x[0]))[:5]]
        phrases = [t.strip() for t in texts if 0 < len(t.strip()) <= 60][:2]
        tcur = start
        items = []
        if topw: items.append("Words: " + ", ".join(topw))
        for p in phrases: items.append("Phrase: " + p)
        for item in items:
            lines_out.append({"start_time": tcur, "end_time": tcur+3.0, "text": item})
            tcur += 3.0
    return {"lines": lines_out}

@app.post("/generate_recaps")
async def generate_recaps(request: Request) -> Dict:
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Signature")):
        return {"error":"invalid signature"}
    payload_json = json.loads(body.decode())
    elements = payload_json.get("elements", {})
    all_elems = elements.get("elements", [])
    vocab_set = set()
    grammar_set = set()
    for el in all_elems:
        e = el.get("elements", {})
        for v in e.get("vocab", []): vocab_set.add(v)
        for g in e.get("grammar", []): grammar_set.add(g)
    vocab_list = list(vocab_set)[:8]
    grammar_list = list(grammar_set)[:4] or ["Core sentence patterns"]
    lines_out = []
    t = 0.0
    if vocab_list:
        lines_out.append({"start_time": t, "end_time": t+4.0, "text": "Vocab: " + ", ".join(vocab_list)})
        t += 4.0
    if grammar_list:
        lines_out.append({"start_time": t, "end_time": t+4.0, "text": "Grammar: " + ", ".join(grammar_list)})
        t += 4.0
    return {"lines": lines_out}

@app.post("/generate_quizzes")
async def generate_quizzes(request: Request) -> Dict:
    body = await request.body()
    if not verify_signature(body, request.headers.get("X-Signature")):
        return {"error":"invalid signature"}
    payload_json = json.loads(body.decode())
    elements = payload_json.get("elements", {}).get("elements", [])
    quizzes = []
    for el in elements:
        vocab = el.get("elements", {}).get("vocab", [])
        if not vocab: continue
        target = vocab[0]
        choices = list({target})
        for w in vocab:
            if len(choices) >= 4: break
            choices.append(w)
        random_choices = choices[:]
        import random
        random.shuffle(random_choices)
        quizzes.append({"type":"mcq", "prompt":"Choose the correct word", "choices": random_choices, "answer": target})
    return {"quizzes": quizzes}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
