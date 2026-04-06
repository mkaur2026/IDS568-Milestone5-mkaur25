import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, List

from src.config import settings


@dataclass
class PendingRequest:
    prompt: str
    temperature: float
    max_tokens: int
    future: asyncio.Future
    created_at: float


class DynamicBatcher:
    def __init__(self, process_batch_fn: Callable):
        self.process_batch_fn = process_batch_fn
        self.pending: List[PendingRequest] = []
        self.lock = asyncio.Lock()
        self.timeout_task = None

    async def submit(self, prompt: str, temperature: float, max_tokens: int) -> Any:
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        request = PendingRequest(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            future=future,
            created_at=time.time(),
        )

        async with self.lock:
            self.pending.append(request)

            should_process = len(self.pending) >= settings.max_batch_size

            if should_process:
                batch = self.pending[:settings.max_batch_size]
                self.pending = self.pending[settings.max_batch_size:]
                asyncio.create_task(self._process_batch(batch))
            elif self.timeout_task is None or self.timeout_task.done():
                self.timeout_task = asyncio.create_task(self._timeout_processor())

        return await future

    async def _timeout_processor(self):
        await asyncio.sleep(settings.batch_timeout_ms / 1000.0)

        async with self.lock:
            if not self.pending:
                return

            batch = self.pending[:settings.max_batch_size]
            self.pending = self.pending[settings.max_batch_size:]

        await self._process_batch(batch)

    async def _process_batch(self, batch: List[PendingRequest]):
        try:
            prompts = [req.prompt for req in batch]
            temperatures = [req.temperature for req in batch]
            max_tokens_list = [req.max_tokens for req in batch]

            results = await self.process_batch_fn(
                prompts=prompts,
                temperatures=temperatures,
                max_tokens_list=max_tokens_list,
            )

            for req, result in zip(batch, results):
                if not req.future.done():
                    req.future.set_result(result)

        except Exception as e:
            for req in batch:
                if not req.future.done():
                    req.future.set_exception(e)
