import time, uuid
from dataclasses import dataclass, asdict
from .config import settings
@dataclass
class RequestMetrics:
    request_id: str
    started: float
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    def finish(self):
        elapsed=max(time.perf_counter()-self.started, 1e-6)
        tokens=self.input_tokens+self.output_tokens
        cost=(self.input_tokens*settings.input_usd_per_1m_tokens+self.output_tokens*settings.output_usd_per_1m_tokens)/1_000_000
        return {"latency_ms":round(elapsed*1000,2),"input_tokens":self.input_tokens,"output_tokens":self.output_tokens,
          "tokens_per_second":round(tokens/elapsed,2),"estimated_cost_usd":round(cost,8),"model":self.model}
def new_metrics(): return RequestMetrics(str(uuid.uuid4()), time.perf_counter())
