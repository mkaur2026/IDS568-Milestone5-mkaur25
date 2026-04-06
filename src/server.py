import asyncio
import time
from contextlib import asynccontextmanager
from typing import List

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.config import settings
from src.caching import cache
from src.batching import DynamicBatcher


# ----------------------------
# Use smaller safer model
# ----------------------------
MODEL_NAME = "sshleifer/tiny-gpt2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

device = "cpu"
model = model.to(device)
model.eval()

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# ----------------------------
# Request / Response
# ----------------------------
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = settings.default_max_new_tokens
    temperature: float = settings.default_temperature


class GenerateResponse(BaseModel):
    generated_text: str
    cached: bool
    latency_ms: float


# ----------------------------
# Batch processor
# ----------------------------
async def process_batch(
    prompts: List[str],
    temperatures: List[float],
    max_tokens_list: List[int],
):

    batch_max_tokens = max(max_tokens_list)

    def _generate():

        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=settings.max_sequence_length,
        )

        inputs = {k: v.to(device) for k, v in inputs.items()}

        generate_kwargs = {
            "max_new_tokens": batch_max_tokens,
            "pad_token_id": tokenizer.eos_token_id,
        }

        if temperatures[0] > 0:
            generate_kwargs["temperature"] = temperatures[0]
            generate_kwargs["do_sample"] = True
        else:
            generate_kwargs["do_sample"] = False

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                **generate_kwargs
            )

        decoded = []

        for i, output in enumerate(outputs):

            full_text = tokenizer.decode(
                output,
                skip_special_tokens=True
            )

            prompt_text = prompts[i]

            if full_text.startswith(prompt_text):
                generated = full_text[len(prompt_text):].strip()
            else:
                generated = full_text.strip()

            decoded.append(generated)

        return decoded

    return await asyncio.to_thread(_generate)


# ----------------------------
# Batcher
# ----------------------------
batcher = DynamicBatcher(process_batch_fn=process_batch)


# ----------------------------
# FastAPI
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Milestone 5 LLM Server",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "LLM inference server is running",
        "model_name": MODEL_NAME
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):

    start_time = time.time()

    use_cache = (
        settings.enable_cache and
        request.temperature == 0.0
    )

    # Cache check
    if use_cache:
        cached_result = cache.get(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        if cached_result is not None:
            latency = round(
                (time.time() - start_time) * 1000,
                2
            )

            return GenerateResponse(
                generated_text=cached_result,
                cached=True,
                latency_ms=latency
            )

    # Batch submit
    result = await batcher.submit(
        prompt=request.prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )

    # Cache store
    if use_cache:
        cache.set(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            value=result
        )

    latency = round(
        (time.time() - start_time) * 1000,
        2
    )

    return GenerateResponse(
        generated_text=result,
        cached=False,
        latency_ms=latency
    )
