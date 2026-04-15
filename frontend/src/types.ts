export type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
  cost: number;
  margin: number;
  stock_level: number;
  category: string;
  tags: string[];
};

export type MenuResponse = {
  recommended_ids: number[];
  ai_reasoning: string;
  menu: Product[];
};

export type Ingredient = {
  id: number;
  name: string;
  description: string | null;
  price_per_unit: number;
  category: string;
  stock_level: number;
  min_stock: number;
  unit_type: string;
  tags: string[];
};

export type DishIngredient = {
  ingredient_id: number;
  ingredient_name: string;
  unit_type: string;
  quantity_needed: number;
  current_stock_level: number;
};

export type DishV2 = {
  id: number;
  name: string;
  description: string | null;
  price: number;
  category: string;
  tags: string[];
  is_active: boolean;
  cost: number;
  margin: number;
  available_servings: number;
  ingredients: DishIngredient[];
};

export type DishIngredientInput = {
  ingredient_id: number;
  quantity_needed: number;
};

export type CreateDishPayload = {
  name: string;
  description?: string;
  price: number;
  category: string;
  tags?: string[];
  is_active?: boolean;
  ingredients: DishIngredientInput[];
};

export type SellDishPayload = {
  dish_id: number;
  quantity: number;
  notes?: string;
  created_by?: string;
};

export type DishSaleResult = {
  dish_id: number;
  quantity_sold: number;
  ingredients_consumed: DishIngredient[];
  remaining_available_servings: number;
};

export type StockTransaction = {
  id: number;
  ingredient_id: number;
  transaction_type: string;
  quantity_changed: number;
  reference_type: string | null;
  reference_id: number | null;
  notes: string | null;
  created_by: string | null;
};
