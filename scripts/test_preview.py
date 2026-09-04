import asyncio
import httpx
from backend.app.main import app

async def test():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/v1/interpretations/discovery-people")
        print("Discovery people status:", r.status_code)
        people = r.json()
        print("Found people:", len(people))
        for p in people:
            hook = p.get("hook_observation", {}).get("text") if p.get("hook_observation") else "None"
            print(f"  {p['display_name']} ({p['astrology']['sun_sign']}) - Score: {p['compatibility_score']:.1f}%")
            print(f"    Hook: {hook}")

        if people:
            target = people[0]
            print(f"\n--- Testing Compare Preview with {target['display_name']} ({target['id']}) ---")
            comp_res = await c.post(
                "/v1/interpretations/compare-preview",
                json={"target_user_id": target["id"], "locale": "ka"}
            )
            print("Compare Status:", comp_res.status_code)
            if comp_res.status_code == 200:
                data = comp_res.json()
                print("Score:", data["score"])
                print("Dimensions:", data["dimensions"])
                print("Primary Interp:", data["interpretation"]["text"])
                print(f"Signals ({len(data['signals'])} total):")
                for s in data["signals"][:3]:
                    interp = s.get("interpretation", {}).get("text", "No interp")
                    print(f"  - [{s['category']}] {s['name']}: {interp}")
                print("Best Topics:", data["best_topics"])
                print("Starters:", data["conversation_starters"])
                print("Deep Analysis Title:", data["deep_analysis"]["title"])
                print("Deep Analysis Summary:", data["deep_analysis"]["summary"])
                print("Deep Analysis Dynamic:", data["deep_analysis"]["core_dynamic"]["headline"])
                print("Deep Analysis Text:", data["deep_analysis"]["core_dynamic"]["text"])
            else:
                print("Error:", comp_res.text)

if __name__ == "__main__":
    asyncio.run(test())
