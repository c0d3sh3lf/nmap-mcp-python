import shlex
import subprocess
import time
import xmltodict
from typing import Tuple, Optional, List, Dict
from .models import ScanResult
from .job_store import job_store
from .config import MAX_SCAN_SECONDS

def build_nmap_command(target: str, args: List[str]) -> List[str]:
    # Always produce XML to stdout so we can parse it.
    cmd = ["nmap", "-oX", "-"]  # - means stdout as XML
    if args:
        # prevent injection - assume args are simple tokens (we trust input for now)
        cmd.extend(args)
    cmd.append(target)
    return cmd

def run_nmap_blocking(target: str, args: List[str], timeout_seconds: Optional[int] = None) -> Tuple[int, Optional[str], Optional[dict], Optional[str]]:
    """
    Runs nmap synchronously. Returns (exit_code, raw_xml, parsed_dict_or_None, error_str_or_None)
    """
    timeout_seconds = timeout_seconds or MAX_SCAN_SECONDS
    cmd = build_nmap_command(target, args)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
        raw = proc.stdout or ""
        parsed = None
        try:
            # parse xml to dict; xmltodict returns OrderedDict-like
            if raw.strip():
                parsed = xmltodict.parse(raw)
        except Exception as e:
            parsed = None
        return proc.returncode, raw, parsed, None
    except subprocess.TimeoutExpired as e:
        return -1, getattr(e, "output", None), None, f"timeout after {timeout_seconds}s"
    except Exception as e:
        return -1, None, None, str(e)
