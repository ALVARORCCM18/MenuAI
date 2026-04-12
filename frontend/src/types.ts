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
