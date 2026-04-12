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
        fallback_ids = sorted(
            [item["id"] for item in products],
            key=lambda item_id: (
                -int(next((p["stock_level"] for p in products if p["id"] == item_id), 0) < 10),
                -next((p["margin"] for p in products if p["id"] == item_id), 0),
            ),
        )
        reasoning = (
            "OpenAI no está configurado. Se usa un ranking local basado en stock crítico y margen. "
            "Los platos con stock crítico y mayor margen aparecen primero."
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
