import os
import json
from dotenv import load_dotenv
from typing import List, Optional
from openai import OpenAI
from pydantic import BaseModel, ValidationError

load_dotenv()


class AIRecommendation(BaseModel):
    recommended_ids: List[int]
    ai_reasoning: str


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _build_menu_prompt(products: List[dict], weather: Optional[str], time_of_day: Optional[str]) -> str:
    context_lines = []
    if weather:
        context_lines.append(f"Clima: {weather}")
    if time_of_day:
        context_lines.append(f"Hora del día: {time_of_day}")

    context_block = "\n".join(context_lines) if context_lines else "Clima y hora no especificados."

    product_lines = []
    for item in products:
        tags = ", ".join(item.get("tags", []))
        product_lines.append(
            f"{item['id']}: {item['name']} - Precio: {item['price']} €, Coste: {item['cost']} €, Margen: {item['margin']:.2f} €, Stock: {item['stock_level']}, Categoría: {item['category']}, Tags: {tags}"
        )

    return (
        "Eres un asistente que ordena un menú para un restaurante. "
        "Prioriza platos con stock crítico, rentabilidad y contexto de clima/hora. "
        "Devuelve un JSON estricto con los campos recommended_ids y ai_reasoning.\n\n"
        "Contexto:\n"
        f"{context_block}\n\n"
        "Platos disponibles:\n"
        + "\n".join(product_lines)
        + "\n\nResponde solo con el JSON requerido."
    )


def rank_menu(products: List[dict], weather: Optional[str] = None, time_of_day: Optional[str] = None) -> AIRecommendation:
    if not client:
        # Fallback ranking that accounts for context (weather, time_of_day), stock (available servings)
        # and margin. This gives preference to dishes that match the context and have more
        # available servings and higher margin.
        def context_score(p: dict) -> int:
            score = 0
            tags = [t.lower() for t in p.get("tags", [])]
            w = (weather or "").lower()
            t = (time_of_day or "").lower()

            if w:
                if "solead" in w or "sun" in w:
                    if any(tag in tags for tag in ("fresco", "soleado", "veraniego")):
                        score += 5
                if "lluv" in w or "rain" in w:
                    if any(tag in tags for tag in ("caliente", "confort", "hervido")):
                        score += 5
                if "frio" in w or "cold" in w:
                    if any(tag in tags for tag in ("caliente", "confort")):
                        score += 5

            if t:
                if "mañ" in t or "manan" in t or "morning" in t:
                    if any(tag in tags for tag in ("desayuno", "mañana", "breakfast")):
                        score += 4
                if "tard" in t or "afternoon" in t or "lunch" in t:
                    if any(tag in tags for tag in ("tarde", "almuerzo", "lunch")):
                        score += 3
                if "noch" in t or "noche" in t or "night" in t or "evening" in t:
                    if any(tag in tags for tag in ("noche", "cena", "dinner")):
                        score += 4

            return score

        scored = []
        for p in products:
            avail = float(p.get("stock_level") or 0)
            margin = float(p.get("margin") or 0)
            cscore = context_score(p)
            # final score weights: make context much stronger so weather/time materially
            # affect ranking; then available servings and margin.
            final = cscore * 100 + avail * 1.0 + margin * 0.1
            scored.append((p.get("id"), final, cscore, avail, margin))

        scored.sort(key=lambda x: x[1], reverse=True)
        fallback_ids = [item[0] for item in scored]

        reasoning = (
            "OpenAI no está configurado. Se usa un ranking local que combina coincidencia de contexto (clima/hora), "
            "disponibilidad y margen. Los platos que mejor coinciden con el clima/hora y tienen más raciones disponibles "
            "suben en la lista."
        )
        return AIRecommendation(recommended_ids=fallback_ids, ai_reasoning=reasoning)

    prompt = _build_menu_prompt(products, weather, time_of_day)
    schema = {
        "name": "menu_recommendation",
        "schema": {
            "type": "object",
            "properties": {
                "recommended_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Lista de IDs ordenada de mayor a menor prioridad.",
                },
                "ai_reasoning": {
                    "type": "string",
                    "description": "Explicación de la estrategia de recomendación.",
                },
            },
            "required": ["recommended_ids", "ai_reasoning"],
            "additionalProperties": False,
        },
    }

    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
        response_format={"type": "json_schema", "json_schema": schema},
        max_output_tokens=350,
    )

    parsed = None
    if hasattr(response, "output_parsed") and isinstance(response.output_parsed, dict):
        parsed = response.output_parsed
    elif hasattr(response, "output"):
        try:
            parsed = json.loads(response.output[0].get("content", [{}])[0].get("text", "{}"))
        except Exception:
            parsed = None

    if not parsed:
        raise RuntimeError("No se pudo parsear la respuesta de OpenAI.")

    try:
        recommendation = AIRecommendation.model_validate(parsed)
    except ValidationError as exc:
        raise RuntimeError(f"Respuesta de OpenAI inválida: {exc}") from exc

    return recommendation
