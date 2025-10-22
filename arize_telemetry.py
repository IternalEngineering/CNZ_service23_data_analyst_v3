"""
Arize Telemetry for Service23
Provides OpenTelemetry instrumentation for LiteLLM and OpenAI API calls
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ArizeTelemetry:
    """Simple Arize telemetry initialization for Service23"""

    def __init__(self):
        self.tracer_provider = None
        self.enabled = False

    def initialize(self, project_name: str = "Service23-DataAnalyst"):
        """Initialize Arize telemetry with OpenTelemetry instrumentation (EU region)"""
        try:
            # Get credentials from environment (EU region uses ARIZE_SPACE_KEY)
            space_key = os.environ.get("ARIZE_SPACE_KEY") or os.environ.get("ARIZE_SPACE_ID")
            api_key = os.environ.get("ARIZE_API_KEY")

            if not space_key or not api_key:
                logger.warning("Arize credentials not found (ARIZE_SPACE_KEY/ARIZE_SPACE_ID, ARIZE_API_KEY). Telemetry disabled.")
                return False

            # Import Arize and instrumentation libraries
            from arize.otel import register
            from arize.otel.otel import Transport, Endpoint
            from openinference.instrumentation.litellm import LiteLLMInstrumentor
            from openinference.instrumentation.openai import OpenAIInstrumentor

            # Register with Arize AX (EU region)
            self.tracer_provider = register(
                space_id=space_key,
                api_key=api_key,
                project_name=project_name,
                endpoint=Endpoint.ARIZE_EUROPE,  # EU region endpoint
                transport=Transport.HTTP,         # HTTP transport (required for EU)
            )

            # Instrument LiteLLM and OpenAI for automatic tracing
            LiteLLMInstrumentor().instrument(tracer_provider=self.tracer_provider)
            OpenAIInstrumentor().instrument(tracer_provider=self.tracer_provider)

            self.enabled = True
            logger.info(f"Arize AX telemetry initialized for project: {project_name}")
            logger.info("Region: EU (eu-west-1a)")
            logger.info("LiteLLM and OpenAI API calls will be automatically traced")
            return True

        except ImportError as e:
            logger.warning(f"Arize libraries not installed: {e}")
            logger.info("Install with: pip install arize openinference-instrumentation-litellm openinference-instrumentation-openai")
            return False

        except Exception as e:
            logger.error(f"Failed to initialize Arize telemetry: {e}")
            return False

    def flush(self):
        """Flush any pending telemetry data"""
        if self.enabled and self.tracer_provider:
            try:
                if hasattr(self.tracer_provider, 'force_flush'):
                    self.tracer_provider.force_flush(timeout_millis=5000)
                    logger.debug("Successfully flushed telemetry data to Arize")
            except Exception as e:
                logger.warning(f"Failed to flush telemetry: {e}")


# Global instance
_telemetry_instance: Optional[ArizeTelemetry] = None


def get_telemetry() -> ArizeTelemetry:
    """Get or create the global telemetry instance"""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = ArizeTelemetry()
    return _telemetry_instance


def initialize_telemetry(project_name: str = "Service23-DataAnalyst") -> bool:
    """Initialize Arize telemetry (call once at startup)"""
    telemetry = get_telemetry()
    return telemetry.initialize(project_name)


def flush_telemetry():
    """Flush telemetry data (call before shutdown)"""
    telemetry = get_telemetry()
    telemetry.flush()
