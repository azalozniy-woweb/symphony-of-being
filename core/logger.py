import os
import inspect
from core.config import LOG_EVERY_N_TICKS, LOG_PATH

log_dir = os.path.dirname(LOG_PATH)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)

_tick_buffer = {}
_input_buffer = {}
_last_written_tick = 0

def log_trace_call(tick, class_name, method_name, args=None, kwargs=None):
    args_str = ",".join(repr(a) for a in args) if args else ""
    kwargs_str = ",".join(f"{k}={v!r}" for k, v in (kwargs or {}).items())
    all_args = ",".join(filter(None, [args_str, kwargs_str]))
    line = f"{class_name}.{method_name}({all_args})"
    _tick_buffer.setdefault(tick, []).append(line)

def log_input(tick, input_str):
    _input_buffer[tick] = input_str

def flush_tick(tick):
    global _last_written_tick

    if tick <= _last_written_tick:
        return

    if tick % LOG_EVERY_N_TICKS != 0:
        return

    start_tick = _last_written_tick + 1
    end_tick = tick
    skipped = 0
    wrote_any = False

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        for t in range(start_tick, end_tick + 1):
            lines = _tick_buffer.pop(t, [])
            input_str = _input_buffer.pop(t, None)

            meaningful_lines = [
                line for line in lines
                if not (
                    line.startswith("State.update()") or
                    line.startswith("VibrationalBeing.update()")
                )
            ]

            if input_str is None and not meaningful_lines:
                skipped += 1
                continue

            if skipped > 0:
                f.write(f"# ⏳ Пропущено {skipped} пустых тиков\n")
                skipped = 0

            if input_str:
                log_line = f"T={t} INPUT='{input_str}'"
                if meaningful_lines:
                    log_line += " → " + " → ".join(meaningful_lines)
            elif meaningful_lines:
                log_line = f"T={t} > " + " → ".join(meaningful_lines)
            else:
                continue

            f.write(log_line + "\n")
            wrote_any = True

    _last_written_tick = end_tick

def trace_method(class_name):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            tick = getattr(self, "tick", None)
            if tick is None:
                for frame in inspect.stack():
                    local_self = frame.frame.f_locals.get("self")
                    if local_self and hasattr(local_self, "tick"):
                        tick = getattr(local_self, "tick")
                        break
            if tick is None:
                tick = 0
            log_trace_call(tick, class_name, method.__name__, args, kwargs)
            return method(self, *args, **kwargs)
        return wrapper
    return decorator

def log_message(tick, *, being=None, signal=None, reaction=None, vibration=None, response=None):
    parts = [f"T={tick}"]
    if signal:
        parts.append(f"INPUT='{signal}'")
    if reaction:
        parts.append(f"→ {reaction}")
    if vibration:
        parts.append(f"VIBE={getattr(vibration, 'word', '...')}")
    if response:
        parts.append(f"OUTPUT={response.get('word', '...')}")
    print(" ".join(parts))