# Governance Memo

## Subject: Governance Considerations for LLM Inference Batching and Caching

This project implements a FastAPI-based LLM inference server with dynamic batching and in-memory caching. These optimizations improve performance, but they also introduce governance concerns involving privacy, data retention, misuse, and compliance.

## 1. Privacy Considerations

Caching introduces privacy risk because prompts and generated outputs may contain sensitive or personal information. Even if caching is used only for performance, stored responses may still expose information if the system is inspected, misconfigured, or shared improperly.

To reduce this risk, the cache in this project does not use plaintext user identifiers. Instead, cache keys are generated through hashing based on the request content and parameters. This design is consistent with the class guidance that cache keys should be hashed and should not store raw user identifiers directly. :contentReference[oaicite:10]{index=10}

In a stronger production design, additional privacy safeguards would include:
- encryption of cache storage
- prompt redaction before storage
- bypassing cache for sensitive prompts
- stronger access controls around cache inspection

## 2. Data Retention and Expiration

Inference caches should never retain data forever. This project uses both a configurable TTL and a maximum cache size, so old entries expire and cache growth remains bounded. This reduces both privacy risk and stale-response risk.

Retention settings create a trade-off. A longer TTL improves hit rate, but also increases the chance that stale or sensitive content remains stored for too long. A shorter TTL improves freshness and limits retention exposure, but it may reduce cache efficiency. The class materials emphasize TTL-based expiration as the most common invalidation strategy for LLM response caching. :contentReference[oaicite:11]{index=11}

## 3. Potential Misuse Scenarios

Several misuse risks apply to a system like this:

- malicious or harmful prompts may still be repeatedly served if cached
- stale outputs may be returned after conditions have changed
- shared cache logic could expose content across users if poorly designed
- repeated automated traffic could abuse system resources
- concurrent request handling could cause operational issues if not protected correctly

Batching itself also creates operational governance concerns. If the batcher is not implemented safely, concurrent requests can lead to race conditions, request delays, or incorrect response handling. The checklist and lecture materials specifically warn about using appropriate async locking to avoid concurrency issues. :contentReference[oaicite:12]{index=12} :contentReference[oaicite:13]{index=13}

## 4. Mitigation Strategies

This project already includes several mitigations:
- hashed cache keys
- TTL-based expiration
- bounded cache size
- deterministic-only caching (`temperature = 0.0`)
- async lock protection in the batcher

Additional mitigations recommended for production:
- allow explicit cache bypass for sensitive requests
- add user opt-out for caching
- support administrative cache invalidation
- apply request rate limiting
- monitor for unusual or malicious usage patterns
- move to a dedicated cache backend with stronger operational controls

The class materials also discuss data retention policies, cache bypass options, and user opt-out as practical governance safeguards for real deployments. :contentReference[oaicite:14]{index=14}

## 5. Compliance Implications

If prompts include personal or regulated information, compliance obligations may apply. GDPR-style concerns can affect:
- data retention length
- deletion rights
- access controls
- auditability
- data storage location

Data residency also becomes important when systems are deployed across regions or external infrastructure. Although this project is a local educational implementation, a production system would need clearly documented retention policies, deletion procedures, audit controls, and infrastructure decisions aligned with applicable regulations.

## Conclusion

Batching and caching are powerful performance optimizations, but they must be implemented responsibly. A safe deployment should treat caching not only as a speed feature, but also as a governance responsibility. This project uses basic safeguards such as hashed keys, TTL expiration, bounded cache size, and async-safe batching, while also highlighting where stronger production controls would still be needed.
