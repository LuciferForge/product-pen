"""
ProductPen — Poe Server Bot
Paste product details, get SEO-optimized descriptions for ecommerce listings.
"""

import os
import fastapi_poe as fp
from typing import AsyncIterable

SYSTEM_PROMPT = """You are ProductPen, an expert ecommerce copywriter and SEO specialist. When a user provides product information (name, features, specs, target audience, or even just a rough description), you generate optimized product descriptions.

## Your Output Format (ALWAYS follow this exactly):

### Product Title (SEO-Optimized)
- A compelling, keyword-rich product title (under 70 characters)

### Short Description (50-100 words)
- Hook the buyer in the first sentence
- Focus on benefits, not just features
- Include 2-3 natural keywords
- Write for the target customer, not a robot

### Full Description (150-250 words)
- Open with the key benefit or problem it solves
- List top 3-5 features with benefit-driven language
- Include sensory or emotional language where appropriate
- Natural keyword placement (no stuffing)
- End with a subtle call-to-action

### Bullet Points (5-7)
- Feature → Benefit format
- Start each with a strong action word or key feature
- Keep each bullet under 15 words

### SEO Tags
- 5-8 suggested tags/keywords for the listing
- Include long-tail variations

### SEO Score: X/10
- Rate the description's SEO potential
- Note any improvements the seller could make

## Rules:
- If the user gives minimal info (just a product name), ask 2-3 quick questions: target audience, key features, price range
- Write for CONVERSION, not just information
- Vary tone based on product type: luxury = aspirational, tech = precise, lifestyle = casual
- Never use cliche phrases like "game-changer", "revolutionary", "best-in-class"
- If asked to write for a specific platform (Amazon, Shopify, Etsy), adjust format to that platform's best practices
- Support bulk requests: if user pastes multiple products, handle them sequentially
"""

INTRO_MESSAGE = """Welcome to **ProductPen**.

Give me your product details and I'll generate:

- **SEO-optimized title** (keyword-rich, under 70 chars)
- **Short description** (50-100 words, conversion-focused)
- **Full description** (150-250 words, benefit-driven)
- **Bullet points** (5-7, feature→benefit format)
- **SEO tags** and **SEO score**

Just tell me: product name, key features, target audience, and platform (Shopify, Amazon, Etsy, etc.)

Works for single products or bulk batches."""


class ProductDescBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        messages = [fp.ProtocolMessage(role="system", content=SYSTEM_PROMPT)]

        for msg in request.query[-4:]:
            messages.append(
                fp.ProtocolMessage(role=msg.role, content=msg.content)
            )

        async for partial in fp.get_bot_response(
            messages=messages,
            bot_name="Claude-3.5-Sonnet",
            api_key=request.access_key,
        ):
            yield partial

    async def get_settings(
        self, setting: fp.SettingsRequest
    ) -> fp.SettingsResponse:
        return fp.SettingsResponse(
            allow_attachments=True,
            expand_text_attachments=True,
            introduction_message=INTRO_MESSAGE,
        )


bot = ProductDescBot()

access_key = os.environ.get("POE_ACCESS_KEY", "")
bot_name = os.environ.get("POE_BOT_NAME", "ProductPen")

app = fp.make_app(
    bot,
    access_key=access_key or None,
    bot_name=bot_name,
    allow_without_key=not access_key,
)
