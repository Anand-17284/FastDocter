from dataclasses import dataclass


@dataclass
class RuntimeFailure:
    exception_type: str
    message: str
    endpoint: str
    method: str
    status_code: int | None = None
    source_file: str | None = None
    source_line: int | None = None


def capture_runtime_failure(
    exception: Exception,
    *,
    endpoint: str,
    method: str,
    status_code: int | None = None,
) -> RuntimeFailure:

    source_file = None
    source_line = None

    # FastAPI ResponseValidationError provides
    # structured endpoint metadata.
    endpoint_ctx = getattr(
        exception,
        "endpoint_ctx",
        None,
    )

    if endpoint_ctx:
        source_file = endpoint_ctx.get("file")
        source_line = endpoint_ctx.get("line")

    # Fallback to traceback inspection when
    # structured framework metadata is unavailable.
    if source_file is None:
        traceback = exception.__traceback__

        while traceback is not None:
            filename = traceback.tb_frame.f_code.co_filename

            if "site-packages" not in filename:
                source_file = filename
                source_line = traceback.tb_lineno
                break

            traceback = traceback.tb_next

    return RuntimeFailure(
        exception_type=type(exception).__name__,
        message=str(exception),
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        source_file=source_file,
        source_line=source_line,
    )