import json
import io
import contextlib
from typing import List, Dict

from openai import OpenAI

from utils import OPENAI_API_KEY
from shopify_graphql_api import *

# ---------- OpenAI client ----------
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- System prompt ----------
SYSTEM_PROMPT = (
    "You are GreenTee’s virtual customer‑service agent. "
    "Be concise and friendly. "
    "If the user asks about an order or a product, "
    "first call the appropriate function to fetch real data."
)

# ---------- Static catalog for golf products ----------
GOLF_PRODUCT_CATALOG = {
    "products": [
        {
            "handle": "honma-beres-lady-go-set-limited-edition-package-set",
            "name": "HONMA Beres Lady Go Set – Limited-Edition 12-Piece Package (Golf Bag Incl.)",
            "link": "https://myavatar-store.com/products/honma-beres-lady-go-set-limited-edition-package-set",
            "variants": [
                {
                    "variant_name": "RH / 12-piece set (Driver 12.5°, 5W, H25, H28, 7-10 irons, SW, Chipper, Louise-style putter 33″, cart bag & gift set, size L)",
                    "sku": "GRTGFST01NN",
                    "price": 4099.99
                }
            ],
            "sales_points": [
                "Pure Japanese craftsmanship from the same Sakata artisans who build Honma Five-Star lines.",
                "Ultra-light ARMRQ graphite shafts help moderate-swing women create effortless carry distance.",
                "Coastal blue-and-pearl cosmetics plus a matching luxury bag turn heads on course and in the clubhouse.",
                "Very limited global allocation—scarcity and collectability drive urgency."
            ]
        },
        {
            "handle": "honma-65th-anniversary-limited-edition-sakura-dance-club-series",
            "name": "HONMA 65th-Anniversary “Sakura Dance” Limited Package Set",
            "link": "https://myavatar-store.com/products/honma-65th-anniversary-limited-edition-sakura-dance-club-series",
            "variants": [
                {
                    "variant_name": "Default Title – complete 14-club set with staff bag",
                    "sku": "GRTGFST02NN",
                    "price": 9999.99
                }
            ],
            "sales_points": [
                "Collector’s item celebrating 65 years of Honma engineering; hand-lacquered sakura detailing on every head.",
                "Full 14-club gapping (driver, fairways, hybrids, irons 6-11, SW, milled putter) in exclusive ARMRQ shafts.",
                "Includes matching wood/iron covers and staff-style bag—prestige look for VIP gifting."
            ]
        },
        {
            "handle": "xxio-13-ladies-complete-11pc-package-set",
            "name": "XXIO 13 Ladies Complete 11-Piece Package Set (Bag Incl.)",
            "link": "https://myavatar-store.com/products/xxio-13-ladies-complete-11pc-package-set",
            "variants": [
                {
                    "variant_name": "RH / White bag – 11-piece (Driver 11.5°, 3W, 5W, H5, 7-9 irons, P/A/S, cart bag)",
                    "sku": "GRTGFST03N1",
                    "price": 4379.99
                }
            ],
            "sales_points": [
                "Ultra-light heads and Weight Plus counter-balancing help 70–85 mph swings square the face for more speed.",
                "Rebound Frame driver with slice-fighting bias offers high launch and forgiveness—ideal for beginners to mid-handicaps.",
                "‘Grab-and-go’ completeness (bag included) removes decision fatigue and speeds checkout."
            ]
        },
        {
            "handle": "ping-womens-g-le3-6-pw-uw-sw-iron-set-with-graphite-shafts",
            "name": "PING G Le3 Women’s 11-Piece Package Set",
            "link": "https://myavatar-store.com/products/ping-womens-g-le3-6-pw-uw-sw-iron-set-with-graphite-shafts",
            "variants": [
                {
                    "variant_name": "RH / Full set (Driver, #3 & #5 FW, 5H, 6H, 7-9 irons, PW, SW, Louise putter 33″, cart bag)",
                    "sku": "GRTGFST04R1",
                    "price": 4039.99
                }
            ],
            "sales_points": [
                "PING’s lightest women’s line ever—engineered lofts and low CG add distance without extra effort.",
                "PurFlex cavity badge plus face-savings weight pads boost MOI for forgiveness on off-centre hits.",
                "Louise mallet putter is 10 g lighter than men’s Ketsch, promoting smoother tempo for slower strokes."
            ]
        },
        {
            "handle": "ping-2025-prodi-g-i-junior-club-package-set-11-club-set-golf-bag-included",
            "name": "PING 2025 Prodi G “ I ” Junior Package – 11-Club Set",
            "link": "https://myavatar-store.com/products/ping-2025-prodi-g-i-junior-club-package-set-11-club-set-golf-bag-included",
            "variants": [
                {
                    "variant_name": "RH / Small bag – Driver, FW, H5, 7-9 irons, PW, W54, Putter 28″",
                    "sku": "GRTGFST07R1",
                    "price": 1814.99
                }
            ],
            "sales_points": [
                "Adult-grade G-Series tech (turbulators, Ti 6-4 face) but 15 % lighter for juniors 4′9″–5′2″.",
                "‘Get Golf Growing’ program: free one-time length/lie/loft adjustment as the junior grows—effectively two sets for one price.",
                "High-loft driver and W54 wedge teach proper launch mechanics early."
            ]
        },
        {
            "handle": "ping-2025-prodi-g-n-junior-club-package-set-9pc-club-set-golf-bag-included",
            "name": "PING 2025 Prodi G “ N ” Junior Package – 9-Club Set",
            "link": "https://myavatar-store.com/products/ping-2025-prodi-g-n-junior-club-package-set-9pc-club-set-golf-bag-included",
            "variants": [
                {
                    "variant_name": "RH / Large bag – Driver, FW, H5, 7-9 irons, PW, W58, Putter 29.5″",
                    "sku": "GRTGFST08R1",
                    "price": 1814.99
                }
            ],
            "sales_points": [
                "Same grown-up aerodynamics as the 11-club ‘I’ set, with a trimmed 9-club makeup that keeps price parent-friendly.",
                "Lower-loft 58° wedge encourages creativity around the greens; stand bag lets kids walk comfortably."
            ]
        },
        {
            "handle": "honma-beres-aizu-5-star-ladies-11-piece-package-set-golf-bag-included",
            "name": "HONMA Beres Aizu 5-Star Ladies 14-Piece Package Set",
            "link": "https://myavatar-store.com/products/honma-beres-aizu-5-star-ladies-11-piece-package-set-golf-bag-included",
            "variants": [
                {
                    "variant_name": "RH / 14-piece (Driver 11.5°, 3W, 5W, U22, irons 5-11, AW, SW, P303 putter 34″, luxury Aizu bag)",
                    "sku": "GRTGFST09R1",
                    "price": 49799.98
                }
            ],
            "sales_points": [
                "Strict 100-set global limit; Aizu hand-lacquer artistry on crimson crowns signals exclusivity.",
                "ARMRQ MX 5-Star shafts with 10-axis aerospace carbon weave provide unmatched stability at <45 g.",
                "Perfect for high-net-worth amateurs or C-suite gifting—average margin exceeds $10 k."
            ]
        },
        {
            "handle": "honma-be-09-4-star-ladies-12-piece-club-package-set",
            "name": "HONMA Beres 09 4-Star Ladies 12-Piece Club Package",
            "link": "https://myavatar-store.com/products/honma-be-09-4-star-ladies-12-piece-club-package-set",
            "variants": [
                {
                    "variant_name": "RH / ARMRQ FX shafts, driver 11.5°, 3W, 5W, U22, U25, 7-10 irons, SW, bag",
                    "sku": "GRTGFST10R1",
                    "price": 28919.99
                }
            ],
            "sales_points": [
                "14-carat-gold accents and 4-Star ARMRQ shafts deliver boundary-pushing status and aesthetics.",
                "Wide L-cup faces plus bias structure create higher COR—‘distance with effortless swing.’",
                "Positioned as a more attainable alternative to 5-Star without sacrificing Honma cachet."
            ]
        },
        {
            "handle": "honma-be-09-4-star-women-13-piece-package-set",
            "name": "HONMA Beres 09 4-Star Women’s 13-Piece Package",
            "link": "https://myavatar-store.com/products/honma-be-09-4-star-women-13-piece-package-set",
            "variants": [
                {
                    "variant_name": "RH / Driver 11.5°, 3W, 5W, H22, irons 6-11, SW, cart bag",
                    "sku": "GRTGFST12R1",
                    "price": 26569.99
                }
            ],
            "sales_points": [
                "Hybrid-iron blend (adds H22) suits women seeking higher-launch long-game gapping.",
                "Carries the same 4-Star luxury narrative—gold accents and ARMRQ shafts—at a slightly lower price."
            ]
        },
        {
            "handle": "taylormade-team-junior-sets",
            "name": "TaylorMade Team Junior Sets",
            "link": "https://myavatar-store.com/products/taylormade-team-junior-sets",
            "variants": [
                {
                    "variant_name": "RH / Ages 10-12 (driver 400 cc, FW, Rescue, 7-9 irons, wedge, putter, stand bag)",
                    "sku": "GRTGFST13R1",
                    "price": 679.99
                }
            ],
            "sales_points": [
                "Designed by the same R&D team behind pro-tour sticks—instant brand trust with parents.",
                "28 % lighter swing weight than adult SIM2; higher lofts help kids launch shots easily.",
                "All-"
            ]
        }
    ]
}

# ---------- Function definitions passed to the model ----------
FUNCTION_DEFS: List[Dict] = [
    {
        "name": "get_order_by_name",
        "description": "Get order details by Shopify order name (e.g. KO2‑5558)",
        "parameters": {
            "type": "object",
            "properties": {
                "order_name": {
                    "type": "string",
                    "description": "The full Shopify order name"
                }
            },
            "required": ["order_name"],
        },
    },
    {
        "name": "get_product_by_handle",
        "description": "Get product info by Shopify product handle",
        "parameters": {
            "type": "object",
            "properties": {
                "handle": {
                    "type": "string",
                    "description": "The product handle"
                }
            },
            "required": ["handle"],
        },
    },
    {
        "name": "get_golf_product_catalog",
        "description": (
            "Return the full catalog of golf set and apparel products. "
            "Use this tool whenever the user wants buying advice or detailed information about golf equipment. "
            "Before providing any recommendations you MUST first ask the user a brief set of preference questions—"
            "e.g. player type (men, women, junior), skill level, and budget tier (value, premium, ultra‑luxury). "
            "Only after you have those answers should you pull the catalog and tailor recommendations accordingly."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        },
    },
]

# ---------- Helper to execute real backend functions ----------
def _dispatch_function(name: str, arguments: dict) -> str:
    """
    Call the real backend function and return its JSON‑serialised result.
    """
    if name == "get_order_by_name":
        # Capture the printed output so we can pass it back to the model
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            fetch_and_print_order_by_name(arguments["order_name"])
        result = buf.getvalue()
        # Also echo to terminal so developers can still see it
        print(result)
    elif name == "get_product_by_handle":
        result = get_product_by_handle(arguments["handle"])
    elif name == "get_golf_product_catalog":
        result = GOLF_PRODUCT_CATALOG
    else:
        result = {"error": "unknown_function"}

    # Fallback to str() for non‑serialisable objects (dates, decimals, etc.)
    return json.dumps(result, default=str)


# ---------- Core conversation driver ----------
def run_conversation(user_input: str, history: List[Dict]) -> str:
    """
    Send the conversation to OpenAI, handle any requested tool calls,
    and return the assistant's final reply.
    """
    # Add the user's latest message so the model can see it
    history.append({"role": "user", "content": user_input})

    while True:
        response = client.chat.completions.create(
            model="o3",
            messages=history,
            tools=[{"type": "function", "function": fn} for fn in FUNCTION_DEFS],
            tool_choice="auto",
        )
        msg = response.choices[0].message

        # New‑spec: model may return `tool_calls`; fall back to legacy `function_call`
        pending_calls = []
        if getattr(msg, "tool_calls", None):
            pending_calls = msg.tool_calls
        elif getattr(msg, "function_call", None):
            pending_calls = [msg]  # wrap legacy single call for uniform handling

        if pending_calls:
            for tool_call in pending_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments or "{}")

                # Record assistant request (optional but keeps context)
                history.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": getattr(tool_call, "id", "call_0"),
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": json.dumps(arguments),
                                },
                            }
                        ],
                    }
                )

                # Run backend function and record its output
                function_response = _dispatch_function(function_name, arguments)
                call_id = getattr(tool_call, "id", "call_0")
                history.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": function_response,
                    }
                )

            # Continue the loop so the model can read the fresh data
            continue

        # No tool call → final answer
        history.append(msg)
        return msg.content or "I'm not sure how to help with that."


# ---------- CLI for local testing ----------
def main() -> None:
    """
    Simple command‑line interface to test the agent locally.
    """
    conversation: List[Dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Type 'quit' to exit.")
    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"quit", "exit"}:
            break

        bot_reply = run_conversation(user_text, conversation)
        print("Bot:", bot_reply)


if __name__ == "__main__":
    main()