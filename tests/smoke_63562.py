"""Live smoke test against #63562. Run: uv run python tests/smoke_63562.py"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from freshdesk_mcp.server import (
    get_ticket_full,
    download_ticket_attachments,
    extract_inline_images,
    decode_ticket_status,
)

TID = 63562


async def main():
    print(f"=== get_ticket_full({TID}) ===")
    t = await get_ticket_full(TID)
    if "error" in t:
        print("ERR:", t["error"]); return
    print(f"subject: {t.get('subject')}")
    print(f"status: {t.get('status')} -> {t.get('status_label')}")
    print(f"agent: {(t.get('agent') or {}).get('contact', {}).get('name') if t.get('agent') else 'n/a'}")
    print(f"requester: {(t.get('requester') or {}).get('name')}")
    print(f"conversations: {len(t.get('conversations') or [])}")
    print(f"attachments_index: {len(t.get('attachments_index') or [])}")
    desc = t.get("description") or ""
    print(f"description chars: {len(desc)} (no truncation)")
    for i, c in enumerate(t.get("conversations") or []):
        body = c.get("body") or ""
        print(f"  conv[{i}] id={c.get('id')} private={c.get('private')} body_chars={len(body)} attachments={len(c.get('attachments') or [])}")

    print(f"\n=== download_ticket_attachments({TID}) ===")
    da = await download_ticket_attachments(TID)
    print(json.dumps({k: v for k, v in da.items() if k != "saved"}, indent=2, default=str))
    for s in da.get("saved", [])[:5]:
        print(" saved:", s)

    print(f"\n=== extract_inline_images({TID}) ===")
    ei = await extract_inline_images(TID)
    print(json.dumps({k: v for k, v in ei.items() if k != "saved"}, indent=2, default=str))
    for s in ei.get("saved", [])[:10]:
        print(" inline:", s)

    print(f"\n=== decode_ticket_status({t.get('status')}) ===")
    print(await decode_ticket_status(t.get("status")))


if __name__ == "__main__":
    asyncio.run(main())
