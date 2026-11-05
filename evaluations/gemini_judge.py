"""Native DeepEval Gemini judgments with one bounded call and owned cleanup."""
from contextvars import ContextVar
from deepeval.models import GeminiModel
from company_system.security.quota import check_quota, record_quota

_client = ContextVar("companyai_deepeval_client", default=None)


class QuotaAwareGeminiJudge(GeminiModel):
    def load_model(self):
        # DeepEvalBaseLLM calls this during __init__. Avoid its otherwise unused
        # eager client; each async generation owns exactly one scoped client.
        return _client.get()

    def generate(self, *args, **kwargs):
        raise RuntimeError("CompanyAI judge requires asynchronous metric execution.")

    async def a_generate(self, prompt, schema=None, audio=None):
        check_quota()
        client = self._build_client()
        marker = _client.set(client)
        try:
            # Preserve DeepEval 4.3.2 native prompts/schema/cost behavior. Skip its
            # retry decorator so daily 429 cannot trigger duplicate HTTP calls.
            return await GeminiModel.a_generate.__wrapped__(self, prompt, schema, audio)
        except Exception as exc:
            record_quota(exc)
            raise
        finally:
            _client.reset(marker)
            try:
                await client.aio.aclose()
            finally:
                client.close()
